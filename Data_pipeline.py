import xarray as xr
import numpy as np  
import pandas as pd
import os
from pathlib import Path
from sqlalchemy import create_engine,inspect,text



DB_USER = "postgres"
DB_PASSWORD = "8860"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ocean_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

with engine.connect() as conn:
    print("Connected Successfully!",engine)
inspector = inspect(engine)

print(inspector.get_table_names())


class ArgoLoader:

    def load_file(self, path):
        try:
            return xr.open_dataset(path)

        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None

    def load_folder(self, folder_path):

        for file_path in Path(folder_path).rglob("*.nc"):

            try:
                ds = xr.open_dataset(file_path)

                yield {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "dataset": ds
                }

            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
                
class Argonormalizer:
    COMMON_SCHEMA = [
    "source",
    "platform_id",
    "cycle_number",
    "timestamp",
    "latitude",
    "longitude",
    "depth",
    "temperature",
    "salinity",
    "oxygen",
    "chlorophyll"
]
    def normalize_data(self,ds):
            rows=[]
            n_profiles = ds.dims["N_PROF"]

            for i in range(n_profiles):
                source = "Argo"
                platform_id = str(ds["PLATFORM_NUMBER"].values[i], "utf-8").strip()

                cycle_number = int(ds["CYCLE_NUMBER"].values[i])
                timestamp = pd.to_datetime(ds["JULD"].values[i])

                latitude = float(ds["LATITUDE"].values[i])

                longitude = float(ds["LONGITUDE"].values[i])

                depth = ds["PRES"].values[i]
                temperature = ds["TEMP"].values[i]
                salinity = ds["PSAL"].values[i]
                oxygen=None
                chlorophyll=None

                for p, t, s in zip(depth, temperature, salinity):

                    if np.isnan(p) or np.isnan(t) or np.isnan(s):
                        continue

                    rows.append({
                        "source": source,
                        "platform_id": platform_id,
                        "cycle_number": cycle_number,
                        "timestamp": timestamp,
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth": p,
                        "temperature": t,
                        "salinity": s,
                        "oxygen": oxygen,
                        "chlorophyll": chlorophyll
                    })
            def convert_to_dataframe(rows):
                return pd.DataFrame(rows)
            return convert_to_dataframe(rows)
        


def file_already_processed(file_name):
    
    query = text("""
        SELECT 1
        FROM processed_files
        WHERE file_name = :file_name
        LIMIT 1
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {"file_name": file_name}
        ).fetchone()

    return result is not None


def mark_file_processed(file_name):

    query = text("""
        INSERT INTO processed_files (file_name)
        VALUES (:file_name)
    """)

    with engine.begin() as conn:
        conn.execute(
            query,
            {"file_name": file_name}
        )
        
def process_argo_data(folder_path):
    path = Path(folder_path)
    if path.is_dir():
        loader = ArgoLoader()
        normalizer = Argonormalizer()


        for item in loader.load_folder(folder_path):
            file_name = item["file_name"]

            if file_already_processed(file_name):
                print(f"Skipping {file_name}")
                continue

            ds = item["dataset"]

            df = normalizer.normalize_data(ds)

            df.to_sql(
                "ocean_measurements",
                engine,
                if_exists="append",
                index=False,
                chunksize=5000,
                method="multi")

            mark_file_processed(file_name)
            print(f"Processed {item['file_name']}")
    
    elif path.is_file():
        loader = ArgoLoader()
        normalizer = Argonormalizer()
        
        if file_already_processed(path.name):
            print(f"Skipping {path.name}")
            return
        ds = loader.load_file(folder_path)
        
        df = normalizer.normalize_data(ds)
        df.to_sql(
                "ocean_measurements",
                engine,
                if_exists="append",
                index=False,
                chunksize=5000,
                method="multi"
            )
        mark_file_processed(path.name)
        print(f"Processed {folder_path}")
        
        
    else:
        print(f"Failed to load dataset from {folder_path}")
        return None
    
#process_argo_data(r"E:\Job Important Documents\Projects\FloatChat\Float_Data\01Jan")
