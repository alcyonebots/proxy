import random
import string
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Global variable to store the job instance and searched usernames
search_job = None
searched_usernames = set()  # Set to track searched usernames

# Function to check Instagram username availability
def check_instagram_username(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.instagram.com/"
    }
    cookies = {
        "sessionid": "70428131521%3AJMtbf1lvxIIeUd%3A12%3AAYfCryRL9DNQQdu8CI58GsQUVK4zB2ubRnqCh-g3sg",
        "csrftoken": "VgyMLeMtGSvpEZklyvziwy4zq6bWwFRD",
        "mid": "ZvlJagABAAGw-dfijK9dT9DsMV3c",
        "ig_did": "F23ED838-1118-44F5-8A2A-DECFF8DDA9C6",
        "ds_user_id": "70428131521",
        "rur": "\"HIL\\05470428131521\\0541763029054:01f7d179c259025912db145c54cf1363da9d391b8bd11a3ed3de39cbcdee1b78a5824040\""
    }
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10, allow_redirects=False)
        print(f"Checked {username}: Status Code {response.status_code}")
        
        if response.status_code == 404:
            return True  # Username is available
        elif response.status_code == 200:
            return False  # Username is taken
        elif response.status_code == 302:
            print(f"Redirect detected for {username}. Likely a bot detection mechanism.")
            return False  # Treat redirects as unavailable for safety
        else:
            print(f"Unexpected response for {username}: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking username {username}: {e}")
        return False

# Example usage
username = "testuser1234"
is_available = check_instagram_username(username)
print(f"Is '{username}' available? {'Yes' if is_available else 'No'}")

# Function to generate random 4-5 letter usernames (including numbers)
def generate_random_username(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to search for available usernames
def search_usernames(context: CallbackContext):
    job = context.job
    chat_id = job.context['chat_id']  # Chat ID to send messages
    username_length = job.context['length']  # Length of the username
    for _ in range(2):  # Check 2 usernames per iteration (reduce to avoid rate limits)
        username = generate_random_username(username_length)
        if username in searched_usernames:
            continue
        searched_usernames.add(username)
        context.bot.send_message(chat_id=chat_id, text=f"Searching for username: {username}")
        
        if check_instagram_username(username):
            context.bot.send_message(chat_id=chat_id, text=f"✅ Available username found: {username}")
        else:
            context.bot.send_message(chat_id=chat_id, text=f"❌ Username not available: {username}")

# Start command - start the username search based on the selected type
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome! Use /four to search for 4-letter usernames or /five to search for 5-letter usernames."
    )

# Start searching for 4-letter usernames
def four(update: Update, context: CallbackContext):
    global search_job
    chat_id = update.message.chat_id
    if search_job:
        update.message.reply_text("Already searching for usernames. Use /stop to stop the search.")
        return
    search_job = context.job_queue.run_repeating(
        search_usernames, interval=60, first=0, context={'chat_id': chat_id, 'length': 4}
    )
    update.message.reply_text("Started searching for 4-letter usernames.")

# Start searching for 5-letter usernames
def five(update: Update, context: CallbackContext):
    global search_job
    chat_id = update.message.chat_id
    if search_job:
        update.message.reply_text("Already searching for usernames. Use /stop to stop the search.")
        return
    search_job = context.job_queue.run_repeating(
        search_usernames, interval=60, first=0, context={'chat_id': chat_id, 'length': 5}
    )
    update.message.reply_text("Started searching for 5-letter usernames.")

# Stop command - stop the username search
def stop(update: Update, context: CallbackContext):
    global search_job
    if search_job:
        search_job.schedule_removal()
        search_job = None
        update.message.reply_text("Stopped the username search.")
    else:
        update.message.reply_text("No search process is running.")

# Main function to run the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot's token
    updater = Updater("7689326948:AAHl9eqQk1_-130IihUQ2z0xn-VSzVRU1Ig", use_context=True)

    # Dispatcher to register handlers
    dp = updater.dispatcher

    # Register commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("four", four))
    dp.add_handler(CommandHandler("five", five))
    dp.add_handler(CommandHandler("stop", stop))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
in()
        
