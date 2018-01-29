#!/usr/bin/env python3

import logging
import pickle

class ConfigMissingException(Exception):
    pass

class Config:
    def __init__(config_file):
        configs = [
            "twitter_user_id",
            "tweet_load_count",
            "admin_id",
            "verbosity",
            "subscribers_file",
            "secret_file"
        ]

        secrets = [
            "twitter_consumer_key",
            "twitter_consumer_secret",
            "twitter_access_token",
            "twitter_access_token_secret",
            "telegram_token"
        ]

        verbosity_levels = {
            "debug":  logging.DEBUG
            "info": logging.INFO
            "warning": logging.WARNING
            "error": logging.ERROR
            "critical": logging.CRITICAL
            "quiet": logging.CRITICAL
            "silent": logging.CRITICAL
            "none": logging.CRITICAL
        }

        # Load configs
        with open(config_file, "r") as fp:
            for line in fp:
                entry = line.split(" ")
                if entry[0] in configs:
                    exec("self.{0} = entry[1][:-1]".format(entry[0]))
                    configs.remove(entry[0])

        # Make sure all configs are specified
        if configs != []:
            for config in configs:
                print("Error: Missing config: {0}".format(config), file = sys.stderr)
            raise ConfigMissingException

        # Load secrets
        with open(self.secret_file, "r") as fp:
            for line in fp:
                entry = line.split(" ")
                if entry[0] in config:
                    exec("self.{0} = entry[1][:-1]".format(entry[0]))
                    secrets.remove(entry[0])

        # Make sure all secrets are specified
        if secrets != []:
            for secret in secrets:
                print("Error: Missing config: {0}".format(secret), file = sys.stderr)
            raise ConfigMissingException

        # Translate the verbosity string to the appropriate number
        try:
            self.loglevel = verbosity_levels[self.verbosity]
        except KeyError:
            print("Unknown verbosity level: {0}".format(self.verbosity))
            raise

        # Load subscribers
        try:
            with open(self.subscribers_file, "rb") as fp:
                self.subscribers = pickle.load(fp)
        except FileNotFoundError:
            with open(self.subscribers_file, "w") as fp:
                pass
        except EOFError:
            pass

    def save_subscribers():
        with open(self.subscribers_file, "wb") as fp:
            pickle.dump(self.subscribers, fp)
