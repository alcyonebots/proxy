import requests
import time
from bs4 import BeautifulSoup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

# Replace these with your actual bot token
BOT_TOKEN = "7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk"

PROXY_SOURCES = [
    "https://www.socks-proxy.net/",  # SOCKS5 proxies
    "https://www.sockslist.net/",  # Additional SOCKS5 proxies
    "https://www.socksproxylist24.top/",  # More SOCKS5 proxies
    "https://www.proxy-list.download/Socks5",  # More SOCKS5 proxies
    "https://www.privoxy.org/Proxies/SOCKS5",  # SOCKS5 proxies
]

def scrape_proxies():
    proxies = []

    # Scrape all the proxy sources
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            if "socks-proxy.net" in url:
                rows = soup.find("table", {"class": "table-striped"}).find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.append({"ip": ip, "port": port, "type": "SOCKS5"})
            
            elif "sockslist.net" in url:
                rows = soup.find("table").find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.append({"ip": ip, "port": port, "type": "SOCKS5"})
            
            elif "socksproxylist24.top" in url:
                rows = soup.find("table").find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 3:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.append({"ip": ip, "port": port, "type": "SOCKS5"})
            
            elif "proxy-list.download/Socks5" in url:
                rows = soup.find("table", {"class": "table table-bordered table-striped"}).find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.append({"ip": ip, "port": port, "type": "SOCKS5"})
            
            elif "privoxy.org" in url:
                rows = soup.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxies.append({"ip": ip, "port": port, "type": "SOCKS5"})
            
        except Exception as e:
            print(f"Error scraping from {url}: {e}")
    
    return proxies

def test_proxy_latency(proxy):
    try:
        start = time.time()
        response = requests.get("https://httpbin.org/ip", proxies={"http": f"http://{proxy['ip']}:{proxy['port']}"}, timeout=5)
        if response.status_code == 200:
            latency = time.time() - start
            return latency
    except Exception as e:
        print(f"Error testing proxy {proxy['ip']}:{proxy['port']} - {e}")
    return float('inf')  # Treat unresponsive proxies as having infinite latency

def categorize_and_send_proxies(proxies, update):
    high_quality = []
    medium_quality = []
    low_quality = []
    
    # Test and categorize proxies
    for proxy in proxies:
        latency = test_proxy_latency(proxy)
        formatted_proxy = f"{proxy['type']},{proxy['ip']},{proxy['port']}"
        
        if latency < 0.5:  # Less than 500 ms
            high_quality.append(formatted_proxy)
        elif 0.5 <= latency <= 1.5:  # Between 500 ms and 1500 ms
            medium_quality.append(formatted_proxy)
        else:  # Greater than 1500 ms
            low_quality.append(formatted_proxy)
    
    # Create and send the proxy lists
    if high_quality:
        with open("high_proxy.txt", "w") as file:
            for proxy in high_quality:
                file.write(f"{proxy}\n")
        update.message.reply_text("High-quality proxies found, sending the file...")
        update.message.reply_document(open("high_proxy.txt", "rb"))
        os.remove("high_proxy.txt")  # Delete file after sending

    if medium_quality:
        with open("medium_proxy.txt", "w") as file:
            for proxy in medium_quality:
                file.write(f"{proxy}\n")
        update.message.reply_text("Medium-quality proxies found, sending the file...")
        update.message.reply_document(open("medium_proxy.txt", "rb"))
        os.remove("medium_proxy.txt")

    if low_quality:
        with open("low_proxy.txt", "w") as file:
            for proxy in low_quality:
                file.write(f"{proxy}\n")
        update.message.reply_text("Low-quality proxies found, sending the file...")
        update.message.reply_document(open("low_proxy.txt", "rb"))
        os.remove("low_proxy.txt")

def scrape(update, context):
    """Trigger the proxy scraping and sending process."""
    update.message.reply_text("Starting proxy scraping... Please wait a moment.")
    proxies = scrape_proxies()
    print(f"Scraped {len(proxies)} proxies.")
    
    if not proxies:
        update.message.reply_text("No proxies found!")
        return
    
    categorize_and_send_proxies(proxies, update)
    update.message.reply_text("Scraping and sending of proxies completed.")

def start(update, context):
    update.message.reply_text("Proxy Scraper Bot is running!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Scrape command handler
    dispatcher.add_handler(CommandHandler("scrape", scrape))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
                    
