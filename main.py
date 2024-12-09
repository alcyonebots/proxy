import requests
import time
from bs4 import BeautifulSoup
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace these with your actual bot token and group IDs
BOT_TOKEN = "7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk"
HIGH_QUALITY_GROUP = -1002377251885  # Replace with your High-quality group ID
MEDIUM_QUALITY_GROUP = -1002295649275  # Replace with your Medium-quality group ID
LOW_QUALITY_GROUP = -1002299532202  # Replace with your Low-quality group ID

PROXY_SOURCES = [
    "https://www.freeproxylists.net/",
    "https://free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/"
]

def scrape_proxies():
    proxies = []
    
    # Proxy source 1: freeproxylists.net
    try:
        url = "https://www.freeproxylists.net/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                country = cols[2].text.strip()
                proxy_type = "HTTP"
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from Free Proxy Lists: {e}")
    
    # Proxy source 2: free-proxy-list.net
    try:
        url = "https://free-proxy-list.net/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("table", {"class": "table-bordered"}).find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 8:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                country = cols[3].text.strip()
                proxy_type = cols[4].text.strip()  # Check if the proxy supports HTTPS
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from Free Proxy List: {e}")

    # Proxy source 3: us-proxy.org
    try:
        url = "https://www.us-proxy.org/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("table", {"class": "table-striped"}).find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                country = cols[2].text.strip()
                proxy_type = "HTTP"
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from US Proxy: {e}")
    
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

def categorize_and_send_proxies(proxies, context):
    high_quality = []
    medium_quality = []
    low_quality = []
    
    def send_in_batches(group_id, proxies_list):
        batch_size = 10
        for i in range(0, len(proxies_list), batch_size):
            batch = proxies_list[i:i + batch_size]
            context.bot.send_message(
                group_id,
                f"Proxies:\n```{chr(10).join(batch)}```",
                parse_mode=ParseMode.MARKDOWN
            )
    
    # Test and categorize proxies in batches of 10
    for i, proxy in enumerate(proxies):
        latency = test_proxy_latency(proxy)
        formatted_proxy = f"{proxy['ip']}:{proxy['port']} | Type: {proxy['type']} | Country: {proxy['country']} | Latency: {latency:.2f}s"
        
        if latency < 0.5:  # Less than 500 ms
            high_quality.append(formatted_proxy)
        elif 0.5 <= latency <= 1.5:  # Between 500 ms and 1500 ms
            medium_quality.append(formatted_proxy)
        else:  # Greater than 1500 ms
            low_quality.append(formatted_proxy)
        
        # After 10 proxies are tested, send them to the appropriate group
        if (i + 1) % 10 == 0:
            print(f"Sending batch {i // 10 + 1} of 10 proxies.")
            send_in_batches(HIGH_QUALITY_GROUP, high_quality)
            send_in_batches(MEDIUM_QUALITY_GROUP, medium_quality)
            send_in_batches(LOW_QUALITY_GROUP, low_quality)
            high_quality.clear()
            medium_quality.clear()
            low_quality.clear()

    # Send any remaining proxies if there are less than 10 left
    if high_quality:
        send_in_batches(HIGH_QUALITY_GROUP, high_quality)
    if medium_quality:
        send_in_batches(MEDIUM_QUALITY_GROUP, medium_quality)
    if low_quality:
        send_in_batches(LOW_QUALITY_GROUP, low_quality)

def scrape(update, context):
    """Trigger the proxy scraping and sending process."""
    update.message.reply_text("Starting proxy scraping... Please wait a moment.")
    proxies = scrape_proxies()
    print(f"Scraped {len(proxies)} proxies.")
    
    if not proxies:
        update.message.reply_text("No proxies found!")
        return
    
    categorize_and_send_proxies(proxies, context)
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
