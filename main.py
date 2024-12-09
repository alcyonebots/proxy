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
    "https://www.sslproxies.org/",
    "https://free-proxy-list.net/",
    "https://proxy-daily.com/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://www.proxynova.com/proxy-server-list/",
    "https://hidemy.name/en/proxy-list/"
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
    
    # Proxy source 2: sslproxies.org
    try:
        url = "https://www.sslproxies.org/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("table", {"id": "proxylisttable"}).find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                country = cols[3].text.strip()
                proxy_type = "HTTPS"  # sslproxies.org usually provides HTTPS proxies
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from SSL Proxies: {e}")
    
    # Proxy source 3: free-proxy-list.net
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

    # Proxy source 4: proxy-daily.com
    try:
        url = "https://proxy-daily.com/"
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
        print(f"Error scraping from Proxy Daily: {e}")
    
    # Proxy source 5: us-proxy.org
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
    
    # Proxy source 6: socks-proxy.net
    try:
        url = "https://www.socks-proxy.net/"
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
                proxy_type = "SOCKS5"  # socks-proxy.net provides SOCKS5 proxies
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from Socks Proxy: {e}")
    
    # Proxy source 7: proxynova.com
    try:
        url = "https://www.proxynova.com/proxy-server-list/"
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
        print(f"Error scraping from Proxy Nova: {e}")
    
    # Proxy source 8: hidemy.name
    try:
        url = "https://hidemy.name/en/proxy-list/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("table", {"class": "proxy__t"}).find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                country = cols[2].text.strip()
                proxy_type = "HTTP"
                proxies.append({"ip": ip, "port": port, "type": proxy_type, "country": country})
    except Exception as e:
        print(f"Error scraping from HideMyName: {e}")

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

def categorize_proxies(proxies):
    high_quality = []
    medium_quality = []
    low_quality = []

    for proxy in proxies:
        latency = test_proxy_latency(proxy)
        formatted_proxy = f"{proxy['ip']}:{proxy['port']} | Type: {proxy['type']} | Country: {proxy['country']} | Latency: {latency:.2f}s"
        if latency < 0.5:  # Less than 500 ms
            high_quality.append(formatted_proxy)
        elif 0.5 <= latency <= 1.5:  # Between 500 ms and 1500 ms
            medium_quality.append(formatted_proxy)
        else:  # Greater than 1500 ms
            low_quality.append(formatted_proxy)

    return high_quality, medium_quality, low_quality

def distribute_proxies(context: CallbackContext):
    proxies = scrape_proxies()
    if not proxies:
        print("No proxies found.")
        return

    high_quality, medium_quality, low_quality = categorize_proxies(proxies)

    if high_quality:
        print(f"Sending {len(high_quality)} high-quality proxies...")
        context.bot.send_message(
            HIGH_QUALITY_GROUP,
            f"High Quality Proxies:\n```{chr(10).join(high_quality)}```",
            parse_mode=ParseMode.MARKDOWN
        )
    if medium_quality:
        print(f"Sending {len(medium_quality)} medium-quality proxies...")
        context.bot.send_message(
            MEDIUM_QUALITY_GROUP,
            f"Medium Quality Proxies:\n```{chr(10).join(medium_quality)}```",
            parse_mode=ParseMode.MARKDOWN
        )
    if low_quality:
        print(f"Sending {len(low_quality)} low-quality proxies...")
        context.bot.send_message(
            LOW_QUALITY_GROUP,
            f"Low Quality Proxies:\n```{chr(10).join(low_quality)}```",
            parse_mode=ParseMode.MARKDOWN
        )

def start(update, context):
    update.message.reply_text("Proxy Scraper Bot is running!")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start command handler
    dispatcher.add_handler(CommandHandler("start", start))

    # Schedule the proxy scraper job
    job_queue = updater.job_queue
    job_queue.run_repeating(distribute_proxies, interval=3600, first=0)  # Runs every hour

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
