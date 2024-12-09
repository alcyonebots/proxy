import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time

# Replace with actual Telegram group chat IDs for high, medium, and low quality proxies
HIGH_QUALITY_GROUP_ID = -1002377251885
MEDIUM_QUALITY_GROUP_ID = -1002295649275
LOW_QUALITY_GROUP_ID = -1002299532202

# Function to get country info for a given IP address
def get_country(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        return data.get("country", "Unknown")
    except requests.RequestException:
        return "Unknown"

# Fetch proxies from different sources
def fetch_sslproxies():
    url = "https://www.sslproxies.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'id': 'proxylisttable'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "HTTPS" if "https" in cols[3].text.lower() else "HTTP"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_free_proxy_list():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'id': 'proxylisttable'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "HTTPS" if "https" in cols[4].text.lower() else "HTTP"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_us_proxy():
    url = "https://www.us-proxy.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'class': 'table table-striped table-bordered'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "HTTPS" if "https" in cols[3].text.lower() else "HTTP"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_socks_proxy():
    url = "https://www.socks-proxy.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'class': 'table table-striped table-bordered'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "SOCKS4" if "socks4" in cols[3].text.lower() else "SOCKS5"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_proxyscrape():
    url = "https://www.proxyscrape.com/free-proxy-list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'class': 'table table-striped table-bordered'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = cols[4].text.strip()  # Can be HTTP/SOCKS4/SOCKS5
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_proxy_list_download():
    url = "https://www.proxy-list.download/api/v1/get?type=https"
    response = requests.get(url)
    proxies = []
    if response.text:
        proxy_list = response.text.split('\r\n')
        for proxy in proxy_list:
            proxies.append(f"{proxy}:https")
    return proxies

def fetch_geonode():
    url = "https://www.geonode.com/free-proxy-list/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find('table', {'class': 'table table-striped'}).find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = cols[3].text.strip()
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

# Function to categorize proxies based on response time (simplified)
def categorize_proxies(proxies):
    high_quality = []
    medium_quality = []
    low_quality = []

    for proxy in proxies:
        ip, port, proxy_type = proxy.split(":")[0], proxy.split(":")[1], proxy.split(":")[2]
        country = get_country(ip)
        response_time = test_proxy(proxy)

        # Categorize proxy based on response time
        if response_time is not None:
            proxy_with_info = f"{proxy} (Country: {country}, Type: {proxy_type})"
            if response_time < 1:
                high_quality.append(proxy_with_info)
            elif 1 <= response_time < 3:
                medium_quality.append(proxy_with_info)
            else:
                low_quality.append(proxy_with_info)
    
    return high_quality, medium_quality, low_quality

# Function to test proxy response time (simplified)
def test_proxy(proxy):
    try:
        start = time.time()
        response = requests.get("http://www.google.com", proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"}, timeout=5)
        end = time.time()
        if response.status_code == 200:
            return end - start
    except requests.RequestException:
        return None

# Function to send proxies to the relevant Telegram groups
def send_proxies_to_groups(update: Update, context: CallbackContext):
    # Fetch proxies from multiple sources
    all_proxies = []
    all_proxies += fetch_sslproxies()
    all_proxies += fetch_free_proxy_list()
    all_proxies += fetch_us_proxy()
    all_proxies += fetch_socks_proxy()
    all_proxies += fetch_proxyscrape()
    all_proxies += fetch_proxy_list_download()
    all_proxies += fetch_geonode()

    update.message.reply_text(f"Fetched {len(all_proxies)} proxies.")

    if not all_proxies:
        update.message.reply_text("No proxies were fetched.")
        return

    # Categorize proxies based on quality
    high_quality, medium_quality, low_quality = categorize_proxies(all_proxies)

    # Send high-quality proxies to the high-quality group
    if high_quality:
        high_quality_message = "\n".join(high_quality[:5])  # Limit to 5 proxies
        context.bot.send_message(chat_id=HIGH_QUALITY_GROUP_ID, text=f"High Quality Proxies:\n{high_quality_message}")

    # Send medium-quality proxies to the medium-quality group
    if medium_quality:
        medium_quality_message = "\n".join(medium_quality[:5])  # Limit to 5 proxies
        context.bot.send_message(chat_id=MEDIUM_QUALITY_GROUP_ID, text=f"Medium Quality Proxies:\n{medium_quality_message}")

    # Send low-quality proxies to the low-quality group
    if low_quality:
        low_quality_message = "\n".join(low_quality[:5])  # Limit to 5 proxies
        context.bot.send_message(chat_id=LOW_QUALITY_GROUP_ID, text=f"Low Quality Proxies:\n{low_quality_message}")

# Command handler for the bot to process /sendproxies
def send_proxies(update: Update, context: CallbackContext):
    send_proxies_to_groups(update, context)
    update.message.reply_text("Proxies have been sent to the appropriate groups.")

# Main function to start the bot
def main():
    token = "7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk"
    
    updater = Updater(token)
    dispatcher = updater.dispatcher

    # Command to trigger proxy sending to groups
    dispatcher.add_handler(CommandHandler("sendproxies", send_proxies))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
