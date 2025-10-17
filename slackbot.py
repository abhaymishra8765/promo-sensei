import os
import threading
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.rag_query import rag_handler
from src.scraper import PumaScraper
from src.ingest_to_vector_db import run_ingestion_for_offers

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/promosensei")
def handle_command(ack, respond, command):
    ack()

    text = command.get("text", "").strip()
    parts = text.split(maxsplit=1)
    subcommand = parts[0].lower() if parts else "help"
    query = parts[1] if len(parts) > 1 else ""

    if subcommand == "search":
        if not query:
            respond("Please provide a search term. Usage: `/promosensei search <your query>`")
            return
        respond(f"Searching for deals related to *'{query}'*...")
        ai_response = rag_handler.get_response(query=query)
        respond(text=ai_response)

    elif subcommand == "summary":
        respond("Generating a summary of the top deals for you...")
        summary_query = "Summarize the top 5 best deals available right now"
        ai_response = rag_handler.get_response(query=summary_query)
        respond(text=ai_response)

    elif subcommand == "brand":
        if not query:
            respond("Please provide a brand name. Usage: `/promosensei brand <brand_name>`")
            return
        respond(f"Searching for the latest deals from *{query}*...")
        brand_query = f"summarize all current offers for {query}"
        ai_response = rag_handler.get_response(query=brand_query, brand=query.capitalize())
        respond(text=ai_response)

    elif subcommand == "refresh":
        respond("Starting the data refresh process. This may take a moment...")

        def ingestion_task():
            try:
                print("Refresh triggered: Scraping Puma...")
                puma_scraper = PumaScraper()
                all_offers = puma_scraper.scrape()

                if all_offers:
                    print(f"Refresh: Scraped {len(all_offers)} offers. Ingesting...")
                    result_message = run_ingestion_for_offers(all_offers)
                    print("Refresh: Ingestion complete.")
                    respond(result_message) 
                else:
                    print("Refresh: No offers scraped.")
                    respond("Refresh complete, but no offers were found during the scrape.")

            except Exception as e:
                print(f"Refresh Error: {e}")
                respond(f"An error occurred during refresh: {e}")

        thread = threading.Thread(target=ingestion_task)
        thread.start()

    else: 
        respond(
            "Welcome to Promo Sensei! Here are the available commands:\n"
            "• `/promosensei search <query>`: Find specific deals.\n"
            "• `/promosensei summary`: Get a summary of the top deals available.\n"
            "• `/promosensei brand <brand>`: Get all offers for a specific brand.\n"
            "• `/promosensei refresh`: Update the promotion database."
        )

if __name__ == "__main__":
    print("Promo Sensei bot is starting...") 
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()