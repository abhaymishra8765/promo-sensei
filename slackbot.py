import os
import threading
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.rag_query import rag_handler 
from src.ingest_to_vector_db import run_ingestion

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
                result_message = run_ingestion()
                respond(result_message)
            except Exception as e:
                respond(f"An error occurred during refresh: {e}")

        thread = threading.Thread(target=ingestion_task)
        thread.start()

    else: 
        respond(
            "Welcome to Promo Sensei! Here are the available commands:\n"
            "• `/promosensei search <query>`: Find deals (e.g., `/promosensei search running shoes`).\n"
            "• `/promosensei brand <brand>`: Get all offers for a specific brand (e.g., `/promosensei brand Puma`).\n"
            "• `/promosensei refresh`: Trigger a new scrape and update the database."
        )

if __name__ == "__main__":
    print("Promo Sensei bot is starting...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()