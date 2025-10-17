
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from .scraper import PumaScraper 

class VectorDBManager:
    """Manages all interactions with the ChromaDB vector database."""
    def __init__(self, path: str = "./chroma_db", collection_name: str = "promo_sensei_offers"):
        self.client = chromadb.PersistentClient(path=path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def ingest(self, offers: List[Dict]):
        if not offers:
            print("No offers to ingest.")
            return

        documents = [f"{o['title']}: {o['description']}" for o in offers]
        
        metadatas = [
            {
                "brand": o['brand_name'],
                "link": o.get('offer_link', 'N/A'),
                "title": o['title'],
                "full_offer_description": o['description'] 
            } for o in offers
        ]
        
        ids = [f"offer_{i}_{o['brand_name']}_{o['title'][:20]}" for i, o in enumerate(offers)]

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Ingestion complete. {len(documents)} offers upserted with rich metadata.")

    def query(self, query_text: str, n_results: int = 5, brand: str = None) -> Dict:
        """Queries the collection for relevant documents, with optional brand filtering."""
        if brand:
            where_clause = {"brand": brand}
            return self.collection.query(
                query_texts=[query_text], n_results=n_results, where=where_clause
            )
        else:
            return self.collection.query(
                query_texts=[query_text], n_results=n_results
            )

def run_ingestion_for_offers(all_offers: List[Dict]):
    """Takes a list of offers and ingests them into the vector DB."""
    db_manager = VectorDBManager()
    db_manager.ingest(all_offers)
    return f"Refresh complete! Scraped and indexed {len(all_offers)} offers."