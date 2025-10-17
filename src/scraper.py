from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from typing import List, Dict
import time

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self) -> List[Dict]:
        pass


class PumaScraper(BaseScraper):
    
    def __init__(self, url: str = "https://in.puma.com/in/en/deals"):
        self.url = url

    def scrape(self) -> List[Dict]:
        print("Scraping Puma...")
        offers = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            try:
                page.goto(self.url, timeout=90000, wait_until='domcontentloaded')
                allow_button_selector = "button:has-text('ALLOW')"
                try:
                    page.locator(allow_button_selector).click(timeout=15000)
                    print("'ALLOW' button clicked.")
                except PlaywrightTimeoutError:
                    print("Cookie banner not found.")
                
                print("Starting intelligent scroll loop...")
                item_selector = 'li:has(a[data-test-id="product-list-item-link"])'
                page.wait_for_selector(item_selector, state='visible', timeout=30000)
                last_height = page.evaluate("document.body.scrollHeight")
                while True:
                    page.keyboard.press("End")
                    time.sleep(2)
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                
                print("All products loaded.")
                html_content = page.content()
            except PlaywrightTimeoutError:
                print("CRITICAL TIMEOUT during page load or scroll.")
                return []
            finally:
                browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')
        product_list_items = soup.select('li:has(a[data-test-id="product-list-item-link"])')
        print(f"Found {len(product_list_items)} products. Parsing for detailed offers...")

        for item in product_list_items:
            try:
                title_tag = item.find('h3')
                title = title_tag.text.strip() if title_tag else "No Title"

                sale_price = "N/A"
                original_price_text = ""
                original_price_formatted = ""
                discount = ""

                original_price_tag = item.select_one('s span[data-test-id="price"]')
                if original_price_tag:
                    original_price_text = original_price_tag.text.strip()
                    original_price_formatted = f"(was {original_price_text})"

                all_price_tags = item.find_all('span', {'data-test-id': 'price'})
                for tag in all_price_tags:
                    current_price_text = tag.text.strip()
                    if current_price_text != original_price_text:
                        sale_price = current_price_text
                        break 
                    
                if sale_price == "N/A" and all_price_tags:
                    sale_price = all_price_tags[0].text.strip()

                discount_tag = item.find(attrs={'data-test-id': 'product-badge-sale'})
                if discount_tag:
                    discount = discount_tag.text.strip().replace('-', '') + " off"

                description = f"Offer on {title}. Now available for {sale_price} {original_price_formatted}. "
                if discount:
                    description += f"This is a {discount} deal. "

                link_tag = item.find('a', {'data-test-id': 'product-list-item-link'})
                relative_link = link_tag.get('to') or link_tag.get('href', '')
                offer_link = "https://in.puma.com" + relative_link

                offers.append({
                    "title": title,
                    "description": description.strip(),
                    "time_period": "Not specified",
                    "brand_name": "Puma",
                    "offer_link": offer_link
                })
            except Exception as e:
                print(f"Error parsing a product tile: {e}")

        print(f"Successfully scraped and parsed {len(offers)} detailed offers.")
        return offers

