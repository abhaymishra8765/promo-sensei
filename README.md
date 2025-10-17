## Promo Sensei

Smart Slack-based assistant that monitors e-commerce sites, scrapes real-time promotional offers, and answers user queries about the best deals using a Retrieval-Augmented Generation (RAG) pipeline.

### Highlights

- **Reliable answers**: Grounded in fresh scraped data to avoid hallucinations.
- **Fast responses**: Embedding search in ChromaDB + Groq LLM for low latency.
- **Modular design**: Clear separation for scraping, ingestion, and querying.

### Demo

Watch the demo video here: [Loom – Promo Sensei Demo](https://www.loom.com/share/b10ef57b77eb4f3b86dc0c9c99d345c3?sid=e2775899-72e3-4cf9-bc77-08557bbac2b0)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment](#environment)
- [Slack App Setup](#slack-app-setup)
- [How to Run](#how-to-run)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Key Design Decisions](#key-design-decisions)

---

## Features

- **Playwright scraper** handles dynamic JS, cookie banners, and lazy loading.
- **ChromaDB vector store** for fast similarity search over offers.
- **SentenceTransformers embeddings** using `all-MiniLM-L6-v2`.
- **Groq LLM** for concise, grounded answers.
- **Slack Bolt bot** with slash commands for search/refresh/help.

## Architecture

1. **Data Ingestion** (`/promosensei refresh`)
   - Playwright launches a headless browser and scrapes offers (e.g., Puma).
   - Text is parsed and sent to the ingestion pipeline.
2. **Vectorization & Storage**
   - Sentences embedded with SentenceTransformers.
   - Embeddings + metadata stored in ChromaDB.
3. **Query & Response** (`/promosensei search`)
   - Query embedded → similarity search in ChromaDB.
   - Retrieved context injected into a prompt for Groq LLM.
   - Slack bot returns an answer grounded in retrieved offers.

## Tech Stack

- **Web Scraping**: Playwright, BeautifulSoup4
- **Vector DB**: ChromaDB
- **Embeddings**: SentenceTransformers `all-MiniLM-L6-v2`
- **LLM**: Groq `openai/gpt-oss-120b`
- **Chat**: Slack Bolt SDK
- **Language**: Python 3.11+

## Prerequisites

- Python 3.10+
- Git

## Installation

```bash
git clone https://github.com/abhaymishra8765/promo-sensei.git
cd promo-sensei
```

Create and activate a virtual environment.

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

## Environment

Create a `.env` file in the project root:

```env
# Groq API Key (https://console.groq.com/)
GROQ_API_KEY="gsk_YourGroqApiKeyHere"

# Slack (https://api.slack.com/)
SLACK_BOT_TOKEN="xoxb-YourBotTokenHere"
SLACK_APP_TOKEN="xapp-YourAppLevelTokenHere"
```

## Slack App Setup

1. Go to [`api.slack.com/apps`](https://api.slack.com/apps) → Create New App.
2. Enable Socket Mode.
3. OAuth & Permissions → add Bot Token Scopes:
   - `chat:write`
   - `commands`
4. Slash Commands → Create New Command:
   - Command: `/promosensei`
   - Short Description: Finds the latest promotional deals and offers.
   - Usage Hint: `[search|brand|refresh] [query]`
5. Install App → copy Bot User OAuth Token and App-Level Token into `.env`.

## How to Run

Step 1: populate the database

```bash
python ingest.py
```

Step 2: start the Slack bot

```bash
python slackbot.py
```

## Usage

Interact in Slack using the slash command:

| Command                       | Description                               | Example                             |
| ----------------------------- | ----------------------------------------- | ----------------------------------- |
| `/promosensei search <query>` | Finds deals via natural language.         | `/promosensei search running shoes` |
| `/promosensei brand <name>`   | Retrieves current offers for a brand.     | `/promosensei brand Puma`           |
| `/promosensei refresh`        | Triggers scraping + ingestion.            | `/promosensei refresh`              |
| `/promosensei summary`        | Get a summary of the top deals available. | `/promosensei summary`              |

## Example Interactions

Here are real examples of how Promo Sensei works in Slack:

### Welcome Message

When you first interact with the bot, you'll see:

```
Welcome to Promo Sensei! Here are the available commands:
• /promosensei search <query>: Find specific deals.
• /promosensei summary: Get a summary of the top deals available.
• /promosensei brand <brand>: Get all offers for a specific brand.
• /promosensei refresh: Update the promotion database.
```

### Data Refresh

**User:** `/promosensei refresh`

**Bot Response:**

```
Starting the data refresh process. This may take a moment...
Refresh complete! Scraped and indexed 40 offers.
```

### Summary Command

**User:** `/promosensei summary`

**Bot Response:**

```
Generating a summary of the top deals for you...

Shuffle Mid Sneakers
• Offer: This is a 57% off deal.
• Brand: Puma
• Link: View Deal

Ca Pro Mid Sneakers
• Offer: This is a 50% off deal.
• Brand: Puma
• Link: View Deal

Iconic T7 Mid-Rise Women's Leggings
• Offer: This is a 30% off deal.
• Brand: Puma
• Link: View Deal
```

### Brand Search

**User:** `/promosensei brand puma`

**Bot Response:**

```
Retaliate 2 Running Shoes
• Offer: This is a 45% off deal.
• Brand: Puma
• Link: View Deal

Shuffle Mid Sneakers
• Offer: This is a 57% off deal.
• Brand: Puma
• Link: View Deal
```

### Natural Language Search

**User:** `/promosensei search "Any flat 50% off deals today?"`

**Bot Response:**

```
Searching for deals related to '"Any flat 50% off deals today?"'...

Ca Pro Mid Sneakers
• Offer: This is a 50% off deal.
• Brand: Puma
• Link: View Deal
```

## Troubleshooting

- Playwright not installed: run `playwright install` after venv activation.
- No results on search: ensure `python ingest.py` completed without errors.
- Slack errors: confirm tokens in `.env` and that Socket Mode is enabled.

---

## Key Design Decisions

### Web Scraping (Playwright)

- Chosen for dynamic, JS-heavy sites. Handles cookie banners and lazy loading.
- Anti-bot measures include realistic user-agent and webdriver flag handling.
- Price parsing refined to extract the actual sale price over struck-through MSRP.

### RAG + Vector DB (ChromaDB & Groq)

- Grounded responses: only retrieved context is used to answer.
- Efficient: local similarity search limits tokens sent to the LLM.
- Groq chosen for high throughput, low latency openai family.

### Code Architecture

- Single Responsibility across `PumaScraper`, `VectorDBManager`, `RAGQueryHandler`.
- `BaseScraper` enables adding new retailers without core changes.
- Clear entry points via `ingest.py` and `slackbot.py` simplify running.
