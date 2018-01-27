#!/usr/bin/env python3

from time import sleep
import pickle
import json
import re
import requests
import time
import traceback
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
        notify_one(bot = bot, chat_id = chat_id, text = "Hello! From now on, I will keep you informed whenever Ella tweets, likes on Twitter or posts on Instagram! You can unsubscribe again with /stop.")
        log.info("Somebody subscribed: [{0}]".format(telegram_get_user_info(chat_id)))
        with open(sub_file, "wb") as fp:
            pickle.dump(subscribers, fp)
    else:
        notify_one(bot = bot, chat_id = chat_id, text = "I have already started!")

def telegram_stop(bot, update):
    global subscribers
    global DEBUG
    chat_id = update.message.chat_id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        notify_one(bot = bot, chat_id = chat_id, text = "You have successfully unsubscribed. Bye!")
        log.info("Somebody unsubscribed: [{0}]".format(telegram_get_user_info(chat_id)))
        with open(sub_file, "wb") as fp:
            pickle.dump(subscribers, fp)

def telegram_help(bot, update):
    notify_one(bot = bot, chat_id = update.message.chat_id, message = "Available commands\n\n/start  Start the bot\n/stop   Stop the bot")

def notify_one(bot, chat_id, message):
    global subscribers
    log = logging.getLogger("LordeSocialBot.notify_one")
    retries = 0
    while True:
        try:
            updater.bot.send_message(chat_id = chat_id, text = message)
            return True
        except telegram.error.NetworkError as e:
            log.info("Network error while sending message to user [{0}]: {1}".format(telegram_get_user_info(chat_id), str(e)))
            if retries == 5
                log.warn("Network error while sending message to user [{0}]: {1}".format(telegram_get_user_info(chat_id), str(e)))
        except telegram.error.ChatMigrated as e:
            log.info("Group migrated to supergroup for group [{0}]: {1} -> {2}".format(telegram_get_user_info(e.new_chat_id), chat_id, e.new_chat_id))
            subscribers[index] = e.new_chat_id
        except telegram.error.InvalidToken:
            raise PermissionError("Invalid Telegram token")
        except telegram.error.RetryAfter as e:
            log.info(str(e))
            sleep(e.retry_after)
        except telegram.error.Unauthorized:
            log.info("User [{0}] has removed or blocked the bot: {1}".format(telegram_get_user_info(chat_id), chat_id))
            return False
        retries += 1
    return True

def notify_admin(bot, message):
    global admin_id
    retries = 0
    while True:
        try:
            bot.send_message(chat_id = admin_id, text = message)
            return
        except telegram.error.NetworkError as e:
            if retries == 5
                log.warn("Network error while sending message to admin: {0}".format(str(e)))
            else:
                log.info("Network error while sending message to admin: {0}".format(str(e)))
        except telegram.error.InvalidToken:
            raise PermissionError("Invalid Telegram token")
        except telegram.error.RetryAfter as e:
            log.warn(str(e))
            sleep(e.retry_after)
        except telegram.error.Unauthorized:
            log.error("Admin has removed or blocked the bot: {0}".format(sub))
            return
        retries += 1

def telegram_userlist(bot, update):
    global subscribers
    global admin_id
    if str(update.message.chat_id) == admin_id:
        message = "A list of all current subscribers:\n"
        for sub in subscribers:
            message += " - {0}\n ".format(telegram_get_user_info(sub))
        notify_admin(bot, message)

def get_insta_pics():
    log = logging.getLogger("LordeSocialBot.get_insta_pics")
    try:
        response = requests.get("https://instagram.com/lordemusic/")
    except requests.exceptions.RequestException as e:
        log.info(str(e))
        return None

    regex = re.search('<script type="text/javascript">window\._sharedData = (.*);</script>', response.text)
    if regex is None:
        log.warn("Could not parse Instagram website")
        return None

    try:
        j = json.loads(regex.group(1))
        nodes = j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
        codes = [node["code"] for node in nodes]
        if codes == []:
            return None
        return codes
    except json.JSONDecodeError as e:
        log.warn(str(e))
        return None
    except (IndexError, KeyError, TypeError):
        log.warn("Could not parse Instagram website")
        return None

def telegram_get_user_info(bot, user_id):
    try:
        chat = bot.getChat(chat_id = sub)
    except telegram.error.TelegramError:
        return "N/A"

    message = "{0}: ".format(sub)
    if chat.first_name is not None:
        message += chat.first_name + " "
    if chat.last_name is not None:
        message += chat.last_name + " "
    if chat.title is not None:
        message += chat.title + " "
    if chat.username is not None:
        message += "(@" + chat.username + ")"
    return message

def notify_all(bot, message):
    log = logging.getLogger("LordeSocialBot.notify_all")
    log.info("Notifying subscribers: " + message)
    to_remove = []
    for index, sub in enumerate(subscribers):
        if not notify_one(bot = bot, chat_id = chat_id, message = message):
            to_remove.append(sub)
    for sub in to_remove:
        subscribers.remove(sub)

def twitter_filter_new(current, old):
    new = []
    current_ids = []
    for obj in current:
        if not obj.id_str in old:
            new.append(obj.id_str)
        current_ids.append(obj.id_str)
    return new, current_ids

def main():
    global subscribers
    global admin_id

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

    with open(config_file, "r") as fp:
        for line in fp:
            entry = line.split(" ")
            if entry[0] == "twitter_user_id:":
                twitter_user_id = entry[1][:-1]
            if entry[0] == "tweet_load_count:":
                tweet_load_count = entry[1][:-1]
            if entry[0] == "admin_id:":
                admin_id = entry[1][:-1]
            if entry[0] == "verbosity:":
                verbosity = entry[1][:-1]

    if verbosity is None:
        loglevel = logging.WARNING
    elif verbosity == "debug":
        loglevel = logging.DEBUG
    elif verbosity == "info":
        loglevel = logging.INFO
    elif verbosity == "warning":
        loglevel = logging.WARNING
    elif verbosity == "error":
        loglevel = logging.ERROR
    elif verbosity == "critical" or verbosity = "silent" or verbosity == "quiet":
        loglevel = logging.CRITICAL
    else:
        loglevel = logging.WARNING

    logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = loglevel)
    log = getLogger("LordeSocialBot")

    # === Twitter initialization ===
    log.info("Initializing Twitter API...")
    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    api = tweepy.API(auth)
    user = api.get_user(user_id = twitter_user_id)

    # Initialized the current state of the timelines
    old_tweets = [tweet.id_str for tweet in api.user_timeline(user_id = twitter_user_id, count = tweet_load_count)]
    old_favs = [fav.id_str for fav in api.favorites(user_id = twitter_user_id, count = tweet_load_count)]

    # === Instagram initialization
    log.info("Initializing Instagram API...")
    old_insta_pics = None
    while old_insta_pics is None:
        old_insta_pics = get_insta_pics()

    # === Telegram initialization ===
    log.info("Initializing Telegram API...")
    updater = Updater(token = telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", telegram_start))
    dispatcher.add_handler(CommandHandler("stop", telegram_stop))
    dispatcher.add_handler(CommandHandler("help", telegram_help))
    dispatcher.add_handler(CommandHandler("userlist", telegram_userlist))
    dispatcher.add_handler(CommandHandler("start@lordesocialbot", telegram_start))
    dispatcher.add_handler(CommandHandler("stop@lordesocialbot", telegram_stop))
    dispatcher.add_handler(CommandHandler("help@lordesocialbot", telegram_help))
    dispatcher.add_handler(CommandHandler("userlist@lordesocialbot", telegram_userlist))
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
    updater.start_polling(timeout = 0, read_latency = 10)

    log.info("Starting main loop...")
    running = True
    while running:
        try:
            # === Twitter part ===
            current_tweets = api.user_timeline(user_id = twitter_user_id, count = tweet_load_count)
            new_tweets, old_tweets = twitter_filter_new(current = current_tweets, old = old_tweets)

            current_favs = api.favorites(user_id = twitter_user_id, count = tweet_load_count)
            new_favs, old_favs = twitter_filter_new(current = current_favs, old = old_favs)

            # === Instagram part ===
            current_insta_pics = get_insta_pics()
            if current_insta_pics is not None:
                new_insta_pics = [pic for pic in current_insta_pics if not pic in old_insta_pics]
                old_insta_pics = current_insta_pics

            # === Telegram part ===
            for tweet in reversed(new_tweets):
                notify_all("Ella tweeted something!: https://twitter.com/lorde/status/" + tweet)

            for fav in reversed(new_favs):
                notify_all("Ella liked something!: https://twitter.com/lorde/status/" + fav)

            for pic in reversed(new_insta_pics):
                notify_all("Ella posted something!: https://instagram.com/p/" + pic)
                
            # Rate limit of tweets is 1500/15min and for favorites it is
            # 75/15min. If we, in the worst case, send a request all 15s,
            # or 60/15min, we should be fine.
            sleep(15)
        except KeyboardInterrupt:
            print("\nExiting")
            updater.stop()
            running = False
        except tweepy.error.TweepError as e:
            print("TweepError")
            traceback.print_exc()
        except tweepy.error.RateLimitError as e:
            print("TwitterRateLimitError")
            traceback.print_exc()
        except requests.exceptions.RequestException as e:
            print("InstagramRequestException")
            traceback.print_exc()

if __name__ == "__main__":
    main()
