import random
import string
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue

# Global variable to store the job instance
search_job = None

# Function to check Instagram username availability
def check_instagram_username(username):
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url)
    return response.status_code == 404

# Function to generate random 4-5 letter usernames (including numbers)
def generate_random_username(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to search for available usernames
def search_usernames(context: CallbackContext):
    chat_id = context.job.context  # Chat ID to send messages
    for _ in range(10):  # Check 10 usernames per iteration
        username = generate_random_username(context.job.data)
        if check_instagram_username(username):
            context.bot.send_message(chat_id=chat_id, text=f"Available username found: {username}")

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
    # Schedule a job to search for 4-letter usernames every minute
    search_job = context.job_queue.run_repeating(search_usernames, interval=60, first=0, context=chat_id, data=4)
    update.message.reply_text("Started searching for 4-letter usernames.")

# Start searching for 5-letter usernames
def five(update: Update, context: CallbackContext):
    global search_job
    chat_id = update.message.chat_id
    if search_job:
        update.message.reply_text("Already searching for usernames. Use /stop to stop the search.")
        return
    # Schedule a job to search for 5-letter usernames every minute
    search_job = context.job_queue.run_repeating(search_usernames, interval=60, first=0, context=chat_id, data=5)
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
    updater = Updater("7689326948:AAHl9eqQk1_-130IihUQ2z0xn-VSzVRU1Ig")

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
  
