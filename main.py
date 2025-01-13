import os
import requests
import time
from bs4 import BeautifulSoup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update

# Replace with your actual bot token
BOT_TOKEN = "7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk"

PROXY_SOURCES = [
    "https://www.freeproxylists.net/",
    "https://free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://www.sslproxies.org/",
    "https://proxy-daily.com/",
    "https://www.proxynova.com/proxy-server-list/",
    "https://spys.me/proxy.txt",
    "https://www.my-proxy.com/free-proxy-list.html",
    "https://www.proxyscrape.com/free-proxy-list",
    "https://www.geonode.com/free-proxy-list/",
    "https://hidemy.name/en/proxy-list/",
    "https://proxylist.geonode.com/",
    "https://openproxy.space/list/http",
    "https://openproxylist.xyz/",
    "https://proxylistdownload.com/",
    "https://proxylists.net/",
    "https://rootjazz.com/proxies/proxies.txt",
    "https://multiproxy.org/txt_all/proxy.txt",
    "https://gimmeproxy.com/api/getProxy",
]

def scrape_proxies():
    proxies = []
    for source in PROXY_SOURCES:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxies.append({"ip": ip, "port": port})
        except Exception as e:
            print(f"Error scraping from {source}: {e}")
    return proxies

def test_proxy_latency(proxy):
    try:
        start = time.time()
        response = requests.get("https://httpbin.org/ip", proxies={"http": f"http://{proxy['ip']}:{proxy['port']}"}, timeout=5)
        if response.status_code == 200:
            latency = time.time() - start
            return latency
    except:
        pass
    return float('inf')  # Treat unresponsive proxies as having infinite latency

def save_and_categorize_proxies(proxies):
    high_quality = []
    medium_quality = []
    low_quality = []

    for proxy in proxies:
        latency = test_proxy_latency(proxy)
        formatted_proxy = f"{proxy['ip']}:{proxy['port']}"
        if latency < 0.5:
            high_quality.append(formatted_proxy)
        elif 0.5 <= latency <= 1.5:
            medium_quality.append(formatted_proxy)
        else:
            low_quality.append(formatted_proxy)

    # Save to files
    with open("high_quality.txt", "w") as file:
        file.write("\n".join(high_quality))
    with open("medium_quality.txt", "w") as file:
        file.write("\n".join(medium_quality))
    with open("low_quality.txt", "w") as file:
        file.write("\n".join(low_quality))

    return len(high_quality), len(medium_quality), len(low_quality), ["high_quality.txt", "medium_quality.txt", "low_quality.txt"]

def send_and_delete_files(update: Update, context: CallbackContext):
    update.message.reply_text("Scraping proxies... Please wait.")
    proxies = scrape_proxies()
    total_proxies = len(proxies)

    if total_proxies == 0:
        update.message.reply_text("No proxies found.")
        return

    # Notify the number of proxies scraped
    update.message.reply_text(f"Scraped a total of {total_proxies} proxies.")

    high, medium, low, files = save_and_categorize_proxies(proxies)

    # Notify categorized counts
    update.message.reply_text(
        f"Categorized proxies:\n"
        f"High-quality: {high}\n"
        f"Medium-quality: {medium}\n"
        f"Low-quality: {low}"
    )

    # Send files and delete them
    for file_name in files:
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_name, "rb"))
        os.remove(file_name)  # Delete the file after sending

    update.message.reply_text("Files sent and cleaned up successfully.")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Proxy Scraper Bot is running!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Scrape and send command handler
    dispatcher.add_handler(CommandHandler("scrape", send_and_delete_files))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
