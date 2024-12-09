import random
import string
import requests
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

# Group IDs for logging
LOG_GROUP_ID = -1002295649275 # Replace with your log group ID
AVAILABLE_GROUP_ID = -1002377251885  # Replace with your available group ID

# Thread control
stop_event = Event()

def check_username_availability(username: str) -> (bool, str):
    """
    Check if an Instagram username is available.
    Returns a tuple (is_available, reason).
    """
    response = requests.get(
        INSTAGRAM_URL.format(username), headers=HEADERS, cookies=COOKIES
    )
    if response.status_code == 404:
        return True, "Available"
    elif response.status_code == 200:
        return False, "Already taken"
    else:
        return False, f"Error: {response.status_code}"

def generate_username(length: int) -> str:
    """Generate a random username of the given length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def start(update: Update, context: CallbackContext) -> None:
    """Start command to greet the user."""
    update.message.reply_text("Welcome! Use /four or /five to check username availability.")

def stop(update: Update, context: CallbackContext) -> None:
    """Stop the bot from checking usernames."""
    stop_event.set()
    update.message.reply_text("Stopping the username check process.")

def check_usernames(update: Update, context: CallbackContext, length: int) -> None:
    """Generate and check usernames of the specified length."""
    stop_event.clear()
    update.message.reply_text(f"Starting to check {length}-letter usernames...")

    while not stop_event.is_set():
        username = generate_username(length)
        is_available, reason = check_username_availability(username)

        if is_available:
            context.bot.send_message(chat_id=AVAILABLE_GROUP_ID, text=f"Available username: @{username}")
        else:
            context.bot.send_message(chat_id=LOG_GROUP_ID, text=f"Unavailable username: @{username} - Reason: {reason}")

    update.message.reply_text("Process stopped.")

def check_four(update: Update, context: CallbackContext) -> None:
    """Check 4-letter usernames."""
    check_usernames(update, context, 4)

def check_five(update: Update, context: CallbackContext) -> None:
    """Check 5-letter usernames."""
    check_usernames(update, context, 5)

def main():
    """Run the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your bot's token
    updater = Updater("7689326948:AAHl9eqQk1_-130IihUQ2z0xn-VSzVRU1Ig", use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("four", check_four))
    dispatcher.add_handler(CommandHandler("five", check_five))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
