
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
        documents = [f"Title: {o['title']}. Description: {o['description']}" for o in offers]
        metadatas = [{"brand": o['brand_name'], "link": o.get('offer_link', 'N/A')} for o in offers]
        ids = [f"offer_{i}_{o['brand_name']}" for i, o in enumerate(offers)]
        
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Ingestion complete. {len(documents)} offers upserted into the database.")
    
    def query(self, query_text: str, n_results: int = 5, brand: str = None) -> Dict:
        """Queries the collection for relevant documents, with optional brand filtering."""
        
        
        if brand:
            where_clause = {"brand": brand}
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )
        else:
            
            return self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )

def run_ingestion():
    """Initializes scrapers and ingests their data into the vector DB."""
    print("Starting data ingestion process...")
    puma_scraper = PumaScraper()
    all_offers = puma_scraper.scrape()
    
    db_manager = VectorDBManager()
    db_manager.ingest(all_offers)
    print("Ingestion process finished.")
    return f"Refresh complete! Scraped and indexed {len(all_offers)} offers."

if __name__ == '__main__':
    run_ingestion()