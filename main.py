import asyncio
import logging
import re
import socks
import socket
import httpx
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from time import time
from bs4 import BeautifulSoup
import urllib.request

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Proxy Scraping Classes (same as your original code)
class Scraper:
    def __init__(self, method, _url):
        self.method = method
        self._url = _url

    def get_url(self, **kwargs):
        return self._url.format(**kwargs, method=self.method)

    async def get_response(self, client):
        return await client.get(self.get_url())

    async def handle(self, response):
        return response.text

    async def scrape(self, client):
        response = await self.get_response(client)
        proxies = await self.handle(response)
        pattern = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?")
        return re.findall(pattern, proxies)

class ProxyScrapeScraper(Scraper):
    def __init__(self, method, timeout=1000, country="All"):
        self.timout = timeout
        self.country = country
        super().__init__(method,
                         "https://api.proxyscrape.com/?request=getproxies"
                         "&proxytype={method}"
                         "&timeout={timout}"
                         "&country={country}")

    def get_url(self, **kwargs):
        return super().get_url(timout=self.timout, country=self.country, **kwargs)

class GeneralTableScraper(Scraper):
    async def handle(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        proxies = set()
        table = soup.find("table", attrs={"class": "table table-striped table-bordered"})
        for row in table.findAll("tr"):
            count = 0
            proxy = ""
            for cell in row.findAll("td"):
                if count == 1:
                    proxy += ":" + cell.text.replace("&nbsp;", "")
                    proxies.add(proxy)
                    break
                proxy += cell.text.replace("&nbsp;", "")
                count += 1
        return "\n".join(proxies)

scrapers = [
    ProxyScrapeScraper("http"),
    ProxyScrapeScraper("socks4"),
    ProxyScrapeScraper("socks5"),
    GeneralTableScraper("http"),
]

# Telegram Bot Commands
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to Proxy Bot! Type /scrape <proxy_type> to scrape and check proxies.")
    update.message.reply_text("Available proxy types: http, socks4, socks5")

def scrape(update: Update, context: CallbackContext) -> None:
    # Parse the proxy type from the command
    proxy_type = context.args[0] if context.args else None
    if not proxy_type or proxy_type not in ['http', 'socks4', 'socks5']:
        update.message.reply_text("Please provide a valid proxy type: http, socks4, or socks5.")
        return
    
    update.message.reply_text(f"Scraping {proxy_type} proxies, please wait...")

    # Start scraping and checking
    asyncio.run(scrape_and_check_proxies(proxy_type, update))

async def scrape_and_check_proxies(proxy_type, update: Update):
    proxies = []
    client = httpx.AsyncClient(follow_redirects=True)

    # Scrape proxies based on the selected type
    proxy_scrapers = [s for s in scrapers if s.method == proxy_type]

    tasks = []
    async def scrape_scraper(scraper):
        try:
            proxies.extend(await scraper.scrape(client))
        except Exception:
            pass

    for scraper in proxy_scrapers:
        tasks.append(asyncio.ensure_future(scrape_scraper(scraper)))

    await asyncio.gather(*tasks)
    await client.aclose()

    proxies = set(proxies)
    if not proxies:
        update.message.reply_text("No proxies found!")
        return

    # Categorize proxies by quality
    high, medium, low = await categorize_proxies(proxies)

    # Send categorized proxies to respective Telegram groups
    send_to_group(update, high, "High-quality Proxies")
    send_to_group(update, medium, "Medium-quality Proxies")
    send_to_group(update, low, "Low-quality Proxies")

    update.message.reply_text(f"Found and categorized {len(proxies)} proxies.")

async def categorize_proxies(proxies):
    high = []
    medium = []
    low = []

    site = "https://www.google.com"  # Default site to test proxies

    for proxy in proxies:
        result = check_proxy(proxy, site)
        if result == "high":
            high.append(proxy)
        elif result == "medium":
            medium.append(proxy)
        else:
            low.append(proxy)

    return high, medium, low

def check_proxy(proxy, site):
    try:
        proxy_split = proxy.split(":")
        host = proxy_split[0]
        port = int(proxy_split[1])

        socks.set_default_proxy(socks.SOCKS5, host, port)
        socket.socket = socks.socksocket

        start_time = time()
        response = urllib.request.urlopen(site, timeout=10)
        end_time = time()

        response_time = end_time - start_time
        if response_time < 1:
            return "high"  # fast response -> high quality
        elif response_time < 2:
            return "medium"  # average response -> medium quality
        else:
            return "low"  # slow response -> low quality
    except Exception:
        return "low"  # if proxy fails, consider it low quality

def send_to_group(update, proxies, category):
    if proxies:
        # Replace with your actual group chat IDs
        high_quality_group_id = -1002377251885
        medium_quality_group_id = -1002295649275
        low_quality_group_id = -1002299532202

        if category == "High-quality Proxies":
            group_id = high_quality_group_id
        elif category == "Medium-quality Proxies":
            group_id = medium_quality_group_id
        else:
            group_id = low_quality_group_id

        message = f"{category}:\n" + "\n".join(proxies)
        update.bot.send_message(chat_id=group_id, text=message)

# Error handling
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    # Telegram Bot Token from @BotFather
    token = '7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk'
    
    updater = Updater(token)
    dispatcher = updater.dispatcher
    
    # Commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("scrape", scrape))
    
    # Error handling
    dispatcher.add_error_handler(error)
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
            
