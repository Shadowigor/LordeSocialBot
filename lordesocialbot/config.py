#!/usr/bin/env python3

import logging
import pickle
from sys import stderr

class ConfigMissingException(Exception):
    pass

class Config:
    def __init__(self, config_file):
        # A list of all configs that are expected to be found in the config
        # file. If the config is read successfully, you will have a variable
        # self.CONNFIG_NAME with the appropriate value afterwards.
        configs = [
            "twitter_user_id",
            "tweet_load_count",
            "admins",
            "verbosity",
            "subscribers_file",
            "secret_file",
            "target_real_name",
            "instagram_username",
            "bot_name",
            "logfile"
        ]

        # Same as for the configs but with the secrets file
        secrets = [
            "twitter_consumer_key",
            "twitter_consumer_secret",
            "twitter_access_token",
            "twitter_access_token_secret",
            "telegram_token"
        ]

        # Define the meaning of the different verbosity levels
        verbosity_levels = {
            "debug":  logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            "quiet": logging.CRITICAL,
            "silent": logging.CRITICAL,
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
                print("Error: Missing config: {0}".format(config), file = stderr)
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
                print("Error: Missing config: {0}".format(secret), file = stderr)
            raise ConfigMissingException

        # Translate the verbosity string to the appropriate number
        try:
            self.loglevel = verbosity_levels[self.verbosity]
        except KeyError:
            print("Unknown verbosity level: {0}".format(self.verbosity))
            raise

        # Expand list of admins
        self.admins = self.admins.split(" ")

        # Load subscribers
        try:
            with open(self.subscribers_file, "rb") as fp:
                self.subscribers = pickle.load(fp)
        except FileNotFoundError:
            with open(self.subscribers_file, "w") as fp:
                pass
        except EOFError:
            pass

    def save_subscribers(self):
        with open(self.subscribers_file, "wb") as fp:
            pickle.dump(self.subscribers, fp)
