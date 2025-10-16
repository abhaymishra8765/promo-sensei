
import os
from groq import Groq
from dotenv import load_dotenv
from src.ingest_to_vector_db import VectorDBManager


load_dotenv()

class RAGQueryHandler:
    """
    Handles the logic for the RAG pipeline. It connects the vector DB to the LLM.
    """
    def __init__(self):
        
        self.db_manager = VectorDBManager()
        self.llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _build_prompt(self, query: str, context: dict) -> str:
        """Constructs the prompt for the LLM with the retrieved context."""
        context_docs = context.get('documents', [[]])[0]
        context_metas = context.get('metadatas', [[]])[0]

        if not context_docs:
            return "" 

        
        context_str = "\n\n".join([
            f"- Offer: {doc}\n  - Link: {meta.get('link', 'N/A')}"
            for doc, meta in zip(context_docs, context_metas)
        ])

        
        return f"""
        You are Promo Sensei, a friendly and helpful Slack assistant that finds the best deals.
        Your task is to answer the user's question based ONLY on the following promotional offers.
        Do not use any outside knowledge.
        - Format your response using Slack's markdown (e.g., *bold*, _italics_, `code`).
        - Present the offers in a clear, easy-to-read list.
        - ALWAYS include the direct links to the offers provided in the context.
        - If the context does not contain a relevant answer, say "I couldn't find any specific deals for that, but here are some other promotions you might like."

        ---
        CONTEXT:
        {context_str}
        ---

        USER'S QUESTION:
        {query}

        ANSWER:
        """

    def get_response(self, query: str, brand: str = None) -> str:
        """The main entry point to get a response from the RAG pipeline."""
        
        retrieved_context = self.db_manager.query(query_text=query, brand=brand)
        
        
        prompt = self._build_prompt(query, retrieved_context)

        if not prompt:
            return "Sorry, I couldn't find any relevant deals for your query in the database."

        
        response = self.llm_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content


rag_handler = RAGQueryHandler()