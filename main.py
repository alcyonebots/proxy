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

# Fetch proxies from various sources
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
            proxies.append(f"{ip}:{port}")
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
            proxies.append(f"{ip}:{port}")
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
            proxies.append(f"{ip}:{port}")
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
            proxies.append(f"{ip}:{port}")
    return proxies

def fetch_proxyscrape():
    url = "https://www.proxyscrape.com/free-proxy-list"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []
    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) > 0:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxies.append(f"{ip}:{port}")
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
            proxies.append(f"{ip}:{port}")
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
            proxies.append(f"{ip}:{port}")
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

# Categorize proxies based on their response time and include country info
def categorize_proxies(proxies):
    high_quality = []
    medium_quality = []
    low_quality = []
    
    for proxy in proxies:
        ip, port = proxy.split(":")
        country = get_country(ip)
        response_time = test_proxy(proxy)
        if response_time is not None:
            proxy_info = f"{proxy} (Country: {country})"
            if response_time < 1:
                high_quality.append(proxy_info)
            elif 1 <= response_time < 3:
                medium_quality.append(proxy_info)
            else:
                low_quality.append(proxy_info)
    
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
    
    # Categorize proxies based on quality and country
    high_quality, medium_quality, low_quality = categorize_proxies(all_proxies)
    
    # Send categorized proxies to the user
    response = "High Quality Proxies:\n"
    response += '\n'.join(high_quality[:5]) if high_quality else "None"
    response += "\n\nMedium Quality Proxies:\n"
    response += '\n'.join(medium_quality[:5]) if medium_quality else "None"
    response += "\n\nLow Quality Proxies:\n"
    response += '\n'.join(low_quality[:5]) if low_quality else "None"

    update.message.reply_text(response)

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
            
