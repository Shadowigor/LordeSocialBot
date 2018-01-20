#!/usr/bin/env python3

from time import sleep
import pickle
import json
import re
import requests
import tweepy
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler

subscribers = []
sub_file = "subscribers"
secret_file = "secret"

def telegram_start(bot, update):
    global subscribers
    chat_id = update.message.chat_id
    if not chat_id in subscribers:
        subscribers.append(chat_id)
        bot.send_message(chat_id = chat_id, text = "Hello! From now on, I will keep you informed whenever Ella tweets or likes something! You can unsubscribe again with /stop.")
    else:
        bot.send_message(chat_id = chat_id, text = "I have already started!")
    with open(sub_file, "wb") as fp:
        pickle.dump(subscribers, fp)

def telegram_stop(bot, update):
    global subscribers
    chat_id = update.message.chat_id
    subscribers.remove(chat_id)
    with open(sub_file, "wb") as fp:
        pickle.dump(subscribers, fp)
    bot.send_message(chat_id = chat_id, text = "You have successfully unsubscribed. Bye!")

def telegram_help(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = "Available commands\n\n\\start  Start the bot\n\\stop  Stop the bot")

def get_insta_pics():
    #response = requests.get("https://instagram.com/lordemusic/")
    response = requests.get("https://instagram.com/test65814308954/")
    regex = re.search('<script type="text/javascript">window\._sharedData = (.*);</script>', response.text).group(1)
    j = json.loads(regex)
    nodes = j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
    return [node["code"] for node in nodes]

def main():
    global subscribers
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
                instagram_password= entry[1][:-1]

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

    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start", telegram_start)
    start_handler_ex = CommandHandler("start@lordesocialbot", telegram_start)
    stop_handler = CommandHandler("stop", telegram_stop)
    stop_handler_ex = CommandHandler("stop@lordesocialbot", telegram_stop)
    help_handler = CommandHandler("help", telegram_help)
    help_handler_ex = CommandHandler("help@lordesocialbot", telegram_help)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(start_handler_ex)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(stop_handler_ex)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(help_handler_ex)
    try:
        with open("subscribers", "rb") as fp:
            subscribers = pickle.load(fp)
    except FileNotFoundError:
        with open("subscribers", "w") as fp:
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

            for fav in reversed(new_favs):
                for sub in subscribers:
                    updater.bot.send_message(chat_id = sub, text = "Ella liked something!\nhttps://twitter.com/lorde/status/" + fav)

            for pic in reversed(new_insta_pics):
                for sub in subscribers:
                    updater.bot.send_message(chat_id = sub, text = "Ella posted something!\nhttps://instagram.com/p/" + pic)

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
