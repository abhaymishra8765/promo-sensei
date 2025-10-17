from src.scraper import PumaScraper
from src.ingest_to_vector_db import run_ingestion_for_offers

def main():
    print("Starting the ingestion process...")

    puma_scraper = PumaScraper()
    puma_offers = puma_scraper.scrape()

    if puma_offers:
        run_ingestion_for_offers(puma_offers)
    else:
        print("No offers were scraped from Puma. Ingestion skipped.")

    print("Ingestion process finished successfully.")

if __name__ == '__main__':
    main()