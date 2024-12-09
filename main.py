import requests
from bs4 import BeautifulSoup
import time
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Function to get country info for a given IP address
def get_country(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        return data.get("country", "Unknown")
    except requests.RequestException:
        return "Unknown"

# Fetch proxies from various sources and identify their type
def fetch_sslproxies():
    url = "https://www.sslproxies.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

def fetch_free_proxy_list():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

def fetch_us_proxy():
    url = "https://www.us-proxy.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

def fetch_socks_proxy():
    url = "https://www.socks-proxy.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (SOCKS4/SOCKS5)")
    return proxies

def fetch_proxyscrape():
    url = "https://www.proxyscrape.com/free-proxy-list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        # Check if the row contains at least 2 columns (IP and port)
        if len(cols) > 1:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            # Add the proxy with its type (HTTP/HTTPS)
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

def fetch_proxy_list_download():
    url = "https://www.proxy-list.download/HTTPS"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

def fetch_geonode():
    url = "https://www.geonode.com/free-proxy-list/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port} (HTTP/HTTPS)")
    return proxies

# Function to test proxy quality by response time
def test_proxy(proxy):
    url = "http://www.google.com"
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    try:
        start_time = time.time()
        response = requests.get(url, proxies=proxies, timeout=5)
        end_time = time.time()
        if response.status_code == 200:
            return end_time - start_time
    except requests.RequestException:
        return None

# Categorize proxies based on their response time and include country and type
def categorize_proxies(proxies):
    high_quality = []
    medium_quality = []
    low_quality = []
    
    for proxy in proxies:
        # Extracting IP, Port, and Type
        proxy_info = proxy.split(" ")
        ip, port = proxy_info[0].split(":")
        proxy_type = proxy_info[1] if len(proxy_info) > 1 else "Unknown"
        country = get_country(ip)
        
        # Testing response time
        response_time = test_proxy(proxy)
        if response_time is not None:
            proxy_with_info = f"{proxy} (Country: {country}, Type: {proxy_type})"
            if response_time < 1:
                high_quality.append(proxy_with_info)
            elif 1 <= response_time < 3:
                medium_quality.append(proxy_with_info)
            else:
                low_quality.append(proxy_with_info)
    
    return high_quality, medium_quality, low_quality
# Function to handle the /proxies command
def proxies(update: Update, context: CallbackContext):
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
    
    # Categorize proxies based on quality, country, and type
    high_quality, medium_quality, low_quality = categorize_proxies(all_proxies)

    # Send high-quality proxies to the user
    if high_quality:
        high_quality_response = "High Quality Proxies:\n"
        high_quality_response += '\n'.join(high_quality[:5])  # Limit to 5 proxies
        update.message.reply_text(high_quality_response)
    else:
        update.message.reply_text("No high-quality proxies found.")

    # Send medium-quality proxies to the user
    if medium_quality:
        medium_quality_response = "\nMedium Quality Proxies:\n"
        medium_quality_response += '\n'.join(medium_quality[:5])  # Limit to 5 proxies
        update.message.reply_text(medium_quality_response)
    else:
        update.message.reply_text("No medium-quality proxies found.")

    # Send low-quality proxies to the user
    if low_quality:
        low_quality_response = "\nLow Quality Proxies:\n"
        low_quality_response += '\n'.join(low_quality[:5])  # Limit to 5 proxies
        update.message.reply_text(low_quality_response)
    else:
        update.message.reply_text("No low-quality proxies found.")
        
# Main function to start the bot
def main():
    # Replace with your own bot's token
    token = "7215448892:AAFfMvaXe1j8PUrrfdRvN9XHZpPHlAjOBxk"

    updater = Updater(token)
    dispatcher = updater.dispatcher
    
    # Command to get proxies
    dispatcher.add_handler(CommandHandler("proxies", proxies))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
