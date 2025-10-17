
import os
from groq import Groq
from dotenv import load_dotenv
from src.ingest_to_vector_db import VectorDBManager

load_dotenv()

class RAGQueryHandler:
    """Handles the logic for the RAG pipeline. It connects the vector DB to the LLM."""
    def __init__(self):
        self.db_manager = VectorDBManager()
        self.llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def _build_prompt(self, query: str, context: dict) -> str:
        """Constructs a detailed prompt using the rich metadata."""
        context_docs = context.get('documents', [[]])[0]
        context_metas = context.get('metadatas', [[]])[0]

        if not context_docs:
            return ""

        context_str = "\n\n".join([
            f"- Title: {meta.get('title')}\n  - Offer Details: {meta.get('full_offer_description')}\n  - Brand: {meta.get('brand')}\n  - Link: {meta.get('link')}"
            for doc, meta in zip(context_docs, context_metas)
        ])
        
        return f"""
        You are Promo Sensei, a helpful Slack assistant. Your task is to answer the user's question by summarizing the provided offers based ONLY on the context below.

        **Formatting Instructions:**
        - Create a clear, bulleted list for the offers.
        - For each offer, you MUST use the following multi-line format.
        - Extract the sale price, original price, and discount from the 'Offer Details' to construct the 'Offer' line.

        **Required Output Format:**
        >*[Product Title]*
        >• *Offer:* Now available for [Sale Price] (was [Original Price]). This is a [Discount] deal.
        >• *Brand:* [Brand Name]
        >• *Link:* <[URL]|View Deal>

        ---
        **CONTEXT:**
        {context_str}
        ---

        **USER'S QUESTION:**
        {query}

        **ANSWER (format your response exactly as instructed above):**
        """

    def get_response(self, query: str, brand: str = None) -> str:
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