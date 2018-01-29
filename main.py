#!/usr/bin/env python3

import logging
from lordesocialbot.config import Config
from lordesocialbot.instagram import Instagram
from lordesocialbot.twitter import Twitter
from lordesocialbot.telegram import Telegram
from time import time, sleep
from sys import argv, stdout

def main():
    # You might have to adjust that path depending on how you run/install the
    # script!
    config_path = "/usr/local/etc/lordesocialbot.conf"

    if argv[1] is not None:
        config_path = argv[1]

    try:
        config = Config(config_path)
    except (ConfigMissingException, KeyError):
        return

    log = logging.getLogger("LordeSocialBot")
    log.setLevel(config.loglevel)
    handler = logging.handlers.StreamHandler()
    log.addHandler(handler)
    handler = logging.handlers.FileHandler(config.logfile)
    log.addHandler(handler)

    try:
        instagram = Instagram(config.instagram_username)
        twitter = Twitter(config)
        telegram = Telegram(config)
    except PermissionError:
        return

    # So we know the name of the person we're monitoring
    name = config.target_real_name

    try:
        while True:
            timestamp = time.time()
            new_tweets = twitter.get_new_tweets()
            new_favs = twitter.get_new_favs()
            new_posts = instagram.get_new_posts()

            # We reverse everything so that the oldest tweets, etc. are send
            # first.
            for tweet in reversed(new_tweets):
                telegram.send_to_all("{0} tweeted something!: https://twitter.com/-/status/{1}".format(name, tweet))

            for fav in reversed(new_favs):
                telegram.send_to_all("{0} liked something!: https://twitter.com/-/status/{1}".format(name, fav))

            for pic in reversed(new_insta_pics):
                telegram.send_to_all("{0} posted something!: https://instagram.com/p/{1}".format(name, pic))

            # The rate limit of tweets is 1500/15min and for favorites it is
            # 75/15min. If we send a request all 15s, or 60/15min, we should
            # be fine. As we scrape the Instagram data manually and not via the
            # API, we shouldn't hit a rate limit there, especially not with
            # those values.
            delay = time.time() - timestamp
            if delay > 0:
                sleep(15 - delay)
    except KeyboardInterrupt:
        log.info("\nExiting")
        telegram.stop()

if __name__ == "__main__":
    main()
