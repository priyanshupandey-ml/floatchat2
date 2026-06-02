from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv
import os   

load_dotenv()

def get_embeddings():
    embeddings = HuggingFaceEndpointEmbeddings(
        model="BAAI/bge-base-en-v1.5",
        task="feature-extraction",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        )
    return embeddings