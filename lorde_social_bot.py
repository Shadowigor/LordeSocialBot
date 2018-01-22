#!/usr/bin/env python3

from time import sleep
import pickle
import json
import re
import requests
import tweepy
import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

DEBUG = True
subscribers = []
sub_file = "/opt/lorde_social_bot/subscribers"
secret_file = "/opt/lorde_social_bot/secret"
admin_id = None

def telegram_start(bot, update):
    global subscribers
    global DEBUG
    chat_id = update.message.chat_id
    if not chat_id in subscribers:
        subscribers.append(chat_id)
        bot.send_message(chat_id = chat_id, text = "Hello! From now on, I will keep you informed whenever Ella tweets, likes on Twitter or posts on Instagram! You can unsubscribe again with /stop.")
        if DEBUG:
            message = "Somebody subscribed: "
            if update.message.chat.first_name is not None:
                message += update.message.chat.first_name + " "
            if update.message.chat.last_name is not None:
                message += update.message.chat.last_name + " "
            if update.message.chat.title is not None:
                message += update.message.chat.title + " "
            if update.message.chat.username is not None:
                message += "(@" + update.message.chat.username + ")"
            print(message)
        with open(sub_file, "wb") as fp:
            pickle.dump(subscribers, fp)
    else:
        bot.send_message(chat_id = chat_id, text = "I have already started!")

def telegram_stop(bot, update):
    global subscribers
    global DEBUG
    chat_id = update.message.chat_id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        bot.send_message(chat_id = chat_id, text = "You have successfully unsubscribed. Bye!")
        if DEBUG:
            message = "Somebody unsubscribed: "
            if update.message.chat.first_name is not None:
                message += update.message.chat.first_name + " "
            if update.message.chat.last_name is not None:
                message += update.message.chat.last_name + " "
            if update.message.chat.title is not None:
                message += update.message.chat.title + " "
            if update.message.chat.username is not None:
                message += "(@" + update.message.chat.username + ")"
            print(message)
        with open(sub_file, "wb") as fp:
            pickle.dump(subscribers, fp)

def telegram_help(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = "Available commands\n\n/start  Start the bot\n/stop   Stop the bot")

def telegram_userlist(bot, update):
    global subscribers
    global admin_id
    if str(update.message.chat_id) == admin_id:
        message = "A list of all current subscribers:\n"
        for sub in subscribers:
            chat = bot.getChat(chat_id = sub)
            message += " - "
            if chat.first_name is not None:
                message += chat.first_name + " "
            if chat.last_name is not None:
                message += chat.last_name + " "
            if chat.title is not None:
                message += chat.title + " "
            if chat.username is not None:
                message += "(@" + chat.username + ")"
            message += "\n"
        bot.send_message(chat_id = admin_id, text = message)

def get_insta_pics():
    response = requests.get("https://instagram.com/lordemusic/")
    regex = re.search('<script type="text/javascript">window\._sharedData = (.*);</script>', response.text).group(1)
    j = json.loads(regex)
    nodes = j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
    return [node["code"] for node in nodes]

def main():
    global subscribers
    global DEBUG
    global admin_id
    print("Starting up...")
    with open(secret_file, "r") as fp:
        for line in fp:
            entry = line.split(" ")
            if entry[0] == "twitter_consumer_key:":
                twitter_consumer_key = entry[1][:-1]
            if entry[0] == "twitter_consumer_secret:":
                twitter_consumer_secret = entry[1][:-1]
            if entry[0] == "twitter_access_token:":
                twitter_access_token = entry[1][:-1]
            if entry[0] == "twitter_access_token_secret:":
                twitter_access_token_secret = entry[1][:-1]
            if entry[0] == "telegram_token:":
                telegram_token = entry[1][:-1]
            if entry[0] == "instagram_username:":
                instagram_username = entry[1][:-1]
            if entry[0] == "instagram_password:":
                instagram_password = entry[1][:-1]
            if entry[0] == "admin_id:":
                admin_id = entry[1][:-1]

    # === Twitter initialization ===
    print("Initializing Twitter API...")
    twitter_user_id = 355307031
    tweet_count = 50

    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)

    user = api.get_user(user_id = twitter_user_id)

    # Initialized the current state of the timelines
    old_tweets = [tweet.id_str for tweet in api.user_timeline(user_id = twitter_user_id, count = tweet_count)]
    old_favs = [fav.id_str for fav in api.favorites(user_id = twitter_user_id, count = tweet_count)]

    # === Instagram initialization
    print("Initializing Instagram API...")
    old_insta_pics = get_insta_pics()

    # === Telegram initialization ===
    print("Initializing Telegram API...")
    updater = Updater(token = telegram_token)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start", telegram_start)
    start_handler_ex = CommandHandler("start@lordesocialbot", telegram_start)
    stop_handler = CommandHandler("stop", telegram_stop)
    stop_handler_ex = CommandHandler("stop@lordesocialbot", telegram_stop)
    help_handler = CommandHandler("help", telegram_help)
    help_handler_ex = CommandHandler("help@lordesocialbot", telegram_help)
    userlist_handler = CommandHandler("userlist", telegram_userlist)
    userlist_handler_ex = CommandHandler("userlist@lordesocialbot", telegram_userlist)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(start_handler_ex)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(stop_handler_ex)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(help_handler_ex)
    dispatcher.add_handler(userlist_handler)
    dispatcher.add_handler(userlist_handler_ex)
    try:
        with open(sub_file, "rb") as fp:
            subscribers = pickle.load(fp)
    except FileNotFoundError:
        with open(sub_file, "w") as fp:
            pass
    except IOError as e:
        print("There was some error opening the subscribers file: " + e)
    except EOFError:
        pass
    updater.start_polling()

    print("Starting main loop...")
    running = True
    while running:
        try:
            # === Twitter part ===
            new_tweets = []
            current_tweets = []
            new_favs = []
            current_favs = []

            # Get the newest tweets and favorites
            tweets = api.user_timeline(user_id = twitter_user_id, count = tweet_count)
            favs = api.favorites(user_id = twitter_user_id, count = tweet_count)

            # Check whether the newest tweet has been seen yet and repeat that
            # for older tweets as well if multiple tweets were posted at the
            # same time.
            for tweet in tweets:
                tweet_id = tweet.id_str
                if not tweet_id in old_tweets:
                    new_tweets.append(tweet_id)
                current_tweets.append(tweet_id)

            old_tweets = current_tweets

            # Same for favorites
            for fav in favs:
                fav_id = fav.id_str
                if not fav_id in old_favs:
                    new_favs.append(fav_id)
                current_favs.append(fav_id)

            old_favs = current_favs

            # === Instagram part ===
            current_insta_pics = []
            new_insta_pics = []

            current_insta_pics = get_insta_pics()
            new_insta_pics = [pic for pic in current_insta_pics if not pic in old_insta_pics]
            old_insta_pics = current_insta_pics

            # === Telegram part ===
            for tweet in reversed(new_tweets):
                for sub in subscribers:
                    updater.bot.send_message(chat_id = sub, text = "Ella tweeted something!\nhttps://twitter.com/lorde/status/" + tweet)
                    if DEBUG:
                        print("Ella tweeted something!: https://twitter.com/lorde/status/" + tweet)

            for fav in reversed(new_favs):
                for sub in subscribers:
                    updater.bot.send_message(chat_id = sub, text = "Ella liked something!\nhttps://twitter.com/lorde/status/" + fav)
                    if DEBUG:
                        print("Ella liked something!: https://twitter.com/lorde/status/" + fav)

            for pic in reversed(new_insta_pics):
                for sub in subscribers:
                    updater.bot.send_message(chat_id = sub, text = "Ella posted something!\nhttps://instagram.com/p/" + pic)
                    if DEBUG:
                        print("Ella posted something!: https://instagram.com/p/" + pic)

            # Rate limit of tweets is 1500/15min and for favorites it is
            # 75/15min. If we, in the worst case, send a request all 15s,
            # or 60/15min, we should be fine. And we won't slow down just
            # for Instagram.
            sleep(15)
        except KeyboardInterrupt:
            print("\nExiting")
            updater.stop()
            running = False

if __name__ == "__main__":
    main()
