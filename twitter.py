#!/usr/bin/env python3

import config
import logging

class Twitter:
    def __init__(config):
        self.conf = config
        self.log = logger.getLogger("LordeSocialBot.Twitter")
        try:
            auth = tweepy.OAuthHandler(config.twitter_consumer_key, config.twitter_consumer_secret)
            auth.set_access_token(config.twitter_access_token, config.twitter_access_token_secret)
            self.api = tweepy.API(auth)
        except tweepy.error #TODO

        while self.favs is None:
            try:
                self.tweets = [tweet.id_str for tweet in self.api.user_timeline(user_id = config.twitter_user_id, count = config.tweet_load_count)]
                self.favs = [fav.id_str for fav in self.api.favorites(user_id = config.twitter_user_id, count = config.tweet_load_count)]
            except tweepy.error #TODO

    def filter_new(current, old):
        new = []
        current_ids = []
        for obj in current:
            obj_id = obj.id_str
            if not obj_id in old:
                new.append(obj_id)
            current_ids.append(obj_id)
        return new, current_ids

    def get_new_tweets():
        try:
            current_tweets = api.user_timeline(user_id = self.conf.twitter_user_id, count = self.conf.tweet_load_count)
            new_tweets, self.old_tweets = self.filter_new(current = current_tweets, old = self.old_tweets)
        except tweepy.error #TODO
            return []
        return new_tweets

    def get_new_favs():
        try:
            current_favs = api.favorites(user_id = self.conf.twitter_user_id, count = self.conf.tweet_load_count)
            new_favs, self.old_favs = twitter_filter_new(current = current_favs, old = self.old_favs)
        except tweepy.error #TODO
            return []
        return new_favs
