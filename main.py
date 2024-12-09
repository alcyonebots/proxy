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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    proxies = []
    
    # Attempt to find the table
    table = soup.find('table', {'id': 'proxylisttable'})
    if table is None:
        print("SSL Proxies table not found!")
        return proxies
    
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "HTTPS" if "https" in cols[3].text.lower() else "HTTP"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    return proxies

def fetch_free_proxy_list():
    url = "https://free-proxy-list.net/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    proxies = []
    
    # Check if the table exists
    table = soup.find('table', {'id': 'proxylisttable'})
    if table is None:
        print("Table with id 'proxylisttable' not found!")
        return proxies  # Return empty list if the table is not found
    
    # Proceed if table is found
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = "HTTPS" if "https" in cols[4].text.lower() else "HTTP"
            proxies.append(f"{ip}:{port}:{proxy_type}")
    
    return proxies

def fetch_us_proxy():
    url = "https://www.us-proxy.org/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    proxies = []
    
    # Check if the table exists
    table = soup.find('table', {'class': 'table table-striped table-bordered'})
    if table is None:
        print("Table with class 'table table-striped table-bordered' not found on proxyscrape!")
        return proxies  # Return empty list if the table is not found
    
    # Proceed if table is found
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy_type = cols[4].text.strip()  # Proxy type column (e.g., HTTP, HTTPS, SOCKS4, SOCKS5)
            proxies.append(f"{ip}:{port}:{proxy_type}")
    
    return proxies
def fetch_proxy_list_download():
    url = "https://www.proxy-list.download/api/v1/get?type=https"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    proxies = []
    if response.text:
        proxy_list = response.text.split('\r\n')
        for proxy in proxy_list:
            proxies.append(f"{proxy}:https")
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
        response = requests.get("http://www.google.com", proxies={"http": f"http://{proxy}", "https": f"https://{proxy}"}, timeout=10)
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

    high_quality, medium_quality, low_quality = categorize_proxies(all_proxies)

    # Send categorized proxies to respective groups
    context.bot.send_message(chat_id=HIGH_QUALITY_GROUP_ID, text="\n".join(high_quality))
    context.bot.send_message(chat_id=MEDIUM_QUALITY_GROUP_ID, text="\n".join(medium_quality))
    context.bot.send_message(chat_id=LOW_QUALITY_GROUP_ID, text="\n".join(low_quality))

# Main function to handle bot setup
def main():
    updater = Updater("7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk", use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("sendproxies", send_proxies_to_groups))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
        
