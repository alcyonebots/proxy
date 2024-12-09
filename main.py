import random
import string
import requests
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from threading import Event

# Instagram URL and headers
INSTAGRAM_URL = "https://www.instagram.com/{}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Instagram cookies (Replace with your cookies)
COOKIES = {
    "mid": "ZvgqmAABAAGOGTQsZ-y0A4LdB1sE",
    "datr": "lyr4Zi0YSNjckLSCrAEA67xD",
    "ig_did": "1D6BC97F-7C04-4BF3-B1D0-081BE10E9A35",
    "ig_nrcb": "1",
    "csrftoken": "WmbdCZloqlyGUBGDrDiMDnhC9eRV8lp0",
    "wd": "630x1247",
    "ds_user_id": "65808199746",
    "sessionid": "65808199746%3AryjTYAU52ULMSu%3A8%3AAYcTM05WjoD57pOfwDq8Dsiw9mRtAC753XxDfecalA",
    "rur": "PRN,65808199746,1765291636:01f7aabbf994d760f400591ff2e5249cb1c84b40ad6c7ec9cc438e372f67e248d033837c",
    "dpr": "1.7142857142857142",
}

# Group IDs for logging and available usernames
LOG_GROUP_ID = -1002295649275  # Replace with the ID of your log group
AVAILABLE_GROUP_ID = -1002377251885  # Replace with the ID of your available group

# Global set to store already searched usernames
searched_usernames = set()

# Thread control
stop_event = Event()

# Function to check if a username is available
def check_username_availability(username: str) -> (bool, str):
    """Check if an Instagram username is available."""
    try:
        response = requests.get(
            INSTAGRAM_URL.format(username), headers=HEADERS, cookies=COOKIES
        )
        
        # If status code is 404, the username is available
        if response.status_code == 404:
            return True, "Available"
        # If status code is 200, the username is taken
        elif response.status_code == 200:
            return False, "Username already taken"
        else:
            return False, f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"

def check_usernames(update: Update, context: CallbackContext, length: int) -> None:
    """Generate and check usernames of the specified length."""
    stop_event.clear()
    update.message.reply_text(f"Starting to check {length}-letter usernames, 5 usernames per 10 seconds...")

    while not stop_event.is_set():
        for _ in range(5):  # Check 5 usernames in a batch
            username = generate_username(length)

            # Skip if the username has already been checked
            if username in searched_usernames:
                continue

            is_available, reason = check_username_availability(username)

            # Add the username to the set of searched usernames
            searched_usernames.add(username)

            if is_available:
                # Send available username to available group
                context.bot.send_message(chat_id=AVAILABLE_GROUP_ID, text=f"Available username: @{username}")
            else:
                # Log unavailable username to log group
                context.bot.send_message(chat_id=LOG_GROUP_ID, text=f"Unavailable username: @{username} - Reason: {reason}")
        
        # Wait for 10 seconds after checking 5 usernames
        time.sleep(10)

    update.message.reply_text("Process stopped.")

def generate_username(length: int) -> str:
    """Generate a random username of the given length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def stop(update: Update, context: CallbackContext) -> None:
    """Stop the bot from checking usernames."""
    stop_event.set()
    update.message.reply_text("Stopping the username check process.")

def start(update: Update, context: CallbackContext) -> None:
    """Start command to greet the user."""
    update.message.reply_text("Welcome! Use /four or /five to check username availability.")

# Function to test a specific username
def test_username(update: Update, context: CallbackContext) -> None:
    """Test the availability of a custom 5-letter username."""
    if len(context.args) != 1:
        update.message.reply_text("Please provide exactly one username. Example: /test test123")
        return

    username = context.args[0]

    # Ensure the username is exactly 5 characters
    if len(username) != 5:
        update.message.reply_text("Please provide a username with exactly 5 characters.")
        return

    # Skip if the username has already been checked
    if username in searched_usernames:
        update.message.reply_text(f"The username @{username} has already been checked.")
        return

    # Check the availability of the custom username
    is_available, reason = check_username_availability(username)

    # Add the username to the set of searched usernames
    searched_usernames.add(username)

    if is_available:
        update.message.reply_text(f"The username @{username} is available!")
        context.bot.send_message(chat_id=AVAILABLE_GROUP_ID, text=f"Available username: @{username}")
    else:
        update.message.reply_text(f"The username @{username} is unavailable. Reason: {reason}")
        context.bot.send_message(chat_id=LOG_GROUP_ID, text=f"Unavailable username: @{username} - Reason: {reason}")

# Setup the main function with dispatcher
def main():
    """Start the bot."""
    updater = Updater("7689326948:AAHl9eqQk1_-130IihUQ2z0xn-VSzVRU1Ig", use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("four", check_usernames, pass_args=True, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("five", check_usernames, pass_args=True, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("test", test_username, pass_args=True))  # Add /test handler

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
