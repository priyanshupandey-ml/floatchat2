from sqlalchemy import create_engine,inspect,text
import pandas as pd
from langchain_core.documents import Document

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
    

    



summary_df = pd.read_sql("""
SELECT
    platform_id,
    cycle_number,
    MIN(timestamp) AS observation_time,
    AVG(latitude) AS latitude,
    AVG(longitude) AS longitude,
    COUNT(*) AS measurements,
    MAX(depth) AS max_depth,
    MIN(temperature) AS min_temp,
    MAX(temperature) AS max_temp,
    MIN(salinity) AS min_sal,
    MAX(salinity) AS max_sal
FROM ocean_measurements
GROUP BY platform_id, cycle_number
""", engine)

summary_df["profile_id"] = (
    summary_df["platform_id"].astype(str)
    + "_"
    + summary_df["cycle_number"].astype(str)
)

summary_df["embedded"]=False
# col_names=summary_df.columns.tolist()
# print(col_names)
# print(summary_df.head())

existing_profiles = pd.read_sql(
    "SELECT profile_id FROM profile_summaries",
    engine
)

existing_ids = set(existing_profiles["profile_id"])

summary_df = summary_df[
    ~summary_df["profile_id"].isin(existing_ids)
]

summary_df.to_sql(
    "profile_summaries",
    engine,
    if_exists="append",
    index=False
)


def get_new_profile_documents(engine):

    query = """
    SELECT *
    FROM profile_summaries
    WHERE embedded = FALSE
    """

    new_summaries = pd.read_sql(query, engine)

    docs = []
    profile_ids = []
    metadata_list = []

    for _, row in new_summaries.iterrows():

        doc = f"""
Profile ID: {row['profile_id']}
Float ID: {row['platform_id']}

Cycle Number: {row['cycle_number']}

Observation Time: {row['observation_time']}

Location:
Latitude: {row['latitude']}
Longitude: {row['longitude']}

Measurements: {row['measurements']}

Maximum Depth: {row['max_depth']} m

Temperature Range:
Minimum: {row['min_temp']} °C
Maximum: {row['max_temp']} °C

Salinity Range:
Minimum: {row['min_sal']}
Maximum: {row['max_sal']}
"""


        profile_ids.append(row["profile_id"])

        docs.append(
        Document(
            page_content=doc,
            metadata={ "platform_id": str(row["platform_id"]),
                      "profile_id": str(row["profile_id"]),
            "cycle_number": int(row["cycle_number"]),
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "max_depth": float(row["max_depth"])
            }
        )
    )


    return docs
    