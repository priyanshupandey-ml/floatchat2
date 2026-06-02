from Data_pipeline import process_argo_data
from vector_store import create_vector_store
from embeddings import get_embeddings
from profile_summary import get_new_profile_documents
from retrive import ask_rag
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "8860"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ocean_db"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("Connected Successfully!", engine)


def main(question):

    data_path = input("Enter Argo file/folder path: ")

    # STEP 1: Process NetCDF → PostgreSQL
    process_argo_data(data_path)

    # STEP 2: Get only NEW profiles
    docs = get_new_profile_documents(engine)

    print("New docs:", len(docs))

    # STEP 3: Load embedding model
    embedding_model = get_embeddings()

    vectorstore = None  # ✅ safe init

    # STEP 4: IF new docs exist → embed + store in chroma
    if docs and len(docs) > 0:

        vectorstore = create_vector_store(embedding_model, docs)

        print(f"Stored {len(docs)} new profiles in Chroma DB")

    # STEP 5: ALWAYS ensure vectorstore exists before querying
    if vectorstore is None:
        from langchain_chroma import Chroma

        vectorstore = Chroma(
            collection_name="ocean_measurements",
            persist_directory="./chroma_db",
            embedding_function=embedding_model
        )

    # STEP 6: RAG Query
    answer = ask_rag(vectorstore, question)

    print("Answer:", answer)


main("What is the maximum depth observed in the dataset?")