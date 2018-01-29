#!/usr/bin/env python3

import logging
import tweepy

class Twitter:
    def __init__(self, config):
        self.conf = config
        self.log = logging.getLogger("LordeSocialBot.Twitter")
        self.log.info("Initializing Twitter API")
        self.failed_tries = 0
        try:
            auth = tweepy.OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
            auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)
            self.api = tweepy.API(auth)
        except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
            self.log.error("Failed to authenticate to Twitter: {0}".format(str(e)))
            raise PermissionError()

        # We will retry as long as necessary
        while self.old_favs is None:
            try:
                self.old_tweets = [tweet.id_str for tweet in self.api.user_timeline(user_id = config.twitter_user_id, count = config.tweet_load_count)]
                self.old_favs = [fav.id_str for fav in self.api.favorites(user_id = config.twitter_user_id, count = config.tweet_load_count)]
            except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
                self.log.error("Failed to fetch initial data from twitter: {0}".format(str(e)))

    def filter_new(self, current, old):
        new = []
        current_ids = []
        for obj in current:
            obj_id = obj.id_str
            if not obj_id in old:
                new.append(obj_id)
            current_ids.append(obj_id)
        return new, current_ids

    def get_new_tweets(self):
        self.log.debug("Getting new tweets")
        try:
            current_tweets = self.api.user_timeline(user_id = self.conf.twitter_user_id, count = self.conf.tweet_load_count)
            new_tweets, self.old_tweets = self.filter_new(current = current_tweets, old = self.old_tweets)
            self.failed_tries = 0
            return new_tweets
        except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
            self.failed_tries += 1
            if self.failed_tries > 5:
                self.log.error("Failed to fetch data from twitter repeatedly: {0}".format(str(e)))
            return []

    def get_new_favs(self):
        self.log.debug("Getting new favs")
        try:
            current_favs = self.api.favorites(user_id = self.conf.twitter_user_id, count = self.conf.tweet_load_count)
            new_favs, self.old_favs = self.filter_new(current = current_favs, old = self.old_favs)
            self.failed_tries = 0
            return new_favs
        except (tweepy.error.TweepError, tweepy.error.RateLimitError) as e:
            self.failed_tries += 1
            if self.failed_tries > 5:
                self.log.error("Failed to fetch data from twitter repeatedly: {0}".format(str(e)))
            return []
