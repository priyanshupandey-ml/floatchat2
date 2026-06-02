from langchain_chroma import Chroma
import os
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



def create_vector_store(embedding_model, docs):

    persist_dir = "./chroma_db"

    # Extract data from Document objects
    texts = [d.page_content for d in docs]
    metadatas = [d.metadata for d in docs]
    ids = [str(d.metadata["profile_id"]) for d in docs]

    # Existing Chroma DB
    if os.path.exists(persist_dir):

        vector_store = Chroma(
            collection_name="ocean_measurements",
            persist_directory=persist_dir,
            embedding_function=embedding_model
        )

        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )

    # Create new Chroma DB
    else:

        vector_store = Chroma.from_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embedding=embedding_model,
            collection_name="ocean_measurements",
            persist_directory=persist_dir
        )
    print(f"Added {len(docs)} new documents to the vector store.")
    profile_ids = [
    d.metadata["profile_id"]
    for d in docs]

    with engine.begin() as conn:
        conn.execute(
            text("""
            UPDATE profile_summaries
            SET embedded = TRUE
            WHERE profile_id = ANY(:ids)
            """),
            {"ids": profile_ids}
        )

    return vector_store
