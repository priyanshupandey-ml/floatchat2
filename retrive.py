from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

load_dotenv()


def ask_rag(vectorstore,question):

    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        task="text-generation",
        huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        max_new_tokens=512,
        temperature=0.5
    )
    
    chat = ChatHuggingFace(llm=llm)

    prompt = PromptTemplate(
        template="""
You are FloatChat, an AI assistant specialized in oceanographic and ARGO float data.

Use ONLY the provided context to answer the user's question.

Instructions:
- Answer based solely on the retrieved context.
- If the answer is not present in the context, say:
  "I could not find relevant information in the available oceanographic data."
- Do not invent values, measurements, locations, dates, or scientific findings.
- When possible, include relevant profile IDs, float IDs, depth ranges, temperature ranges, salinity ranges, locations, and observation dates from the context.
- Keep answers scientifically accurate and easy to understand.
- If multiple profiles are relevant, summarize the important findings.
- Format numerical values clearly with units.


Context:
{context}

Question:
{question}
""",
        input_variables=["context", "question"]
    )

    retriever = vectorstore.as_retriever(
        # search_type="similarity",
        # search_kwargs={
        #     "k": 5,
        #     # "fetch_k": 20
        # }
        # search_type="similarity_score_threshold",
        # search_kwargs={
        #     "k": 5,
        #     "score_threshold": 0.65
        #     }
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 50,
            "lambda_mult": 0.7
        }
    )
    # retrieved_docs = retriever.invoke(question)
    # for doc in retrieved_docs:
    #     print("RETRIEVED DOC:", doc.page_content)
    # print(vectorstore._collection.count())
        

    def format_docs(retrieved_docs):
        return "\n\n".join(
            doc.page_content for doc in retrieved_docs
        )
    
    # context = format_docs(retrieved_docs)
    # final_prompt = prompt.invoke({"context": context, "question": question})
    # print(final_prompt)
    # chat_response = chat.invoke(final_prompt)
    # print(chat_response)

    chain = (
        RunnableParallel(
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(),
            }
        )
        | prompt
        | chat
        | StrOutputParser()
    )

    return chain.invoke(question)
    
# ask_rag("what is the maximum depth observed in the dataset?")