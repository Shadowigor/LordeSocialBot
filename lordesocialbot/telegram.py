#!/usr/bin/env python3

import logging
from time import sleep
import telegram.error
from telegram.ext import Updater
from lordesocialbot.telegram_commands import TelegramCommands

class Telegram:
    def __init__(self, config):
        self.conf = config
        self.log = logging.getLogger("LordeSocialBot.Telegram")
        self.log.info("Initializing Telegram API")
        self.updater = Updater(token = config.telegram_token)
        self.bot = self.updater.bot
        self.commands = TelegramCommands(config = config, telegram = self, dispatcher = self.updater.dispatcher)
        self.updater.start_polling(timeout = 0, read_latency = 10)

    def send(self, chat_id, message):
        self.log.debug("Sending message to user ".format(chat_id))
        retries = 0
        while True:
            try:
                self.bot.send_message(chat_id = chat_id, text = message)
                return True
            except telegram.error.NetworkError as e:
                if retries == 5:
                    self.log.warning("There is still a network error while sending message to user [{0}] after 5 retries: {1}".format(self.user_info(chat_id), str(e)))
                else:
                    self.log.debug("Network error while sending message to user [{0}]: {1}".format(self.user_info(chat_id), str(e)))
            except telegram.error.ChatMigrated as e:
                self.log.debug("Group migrated to supergroup for group [{0}]: {1} -> {2}".format(self.user_info(e.new_chat_id), chat_id, e.new_chat_id))
                self.conf.subscribers = [e.new_chat_id if sub == chat_id else sub for sub in self.conf.subscribers]
            except telegram.error.InvalidToken:
                raise PermissionError("Invalid Telegram token")
            except telegram.error.RetryAfter as e:
                self.log.debug(str(e))
                sleep(e.retry_after)
            except telegram.error.Unauthorized:
                self.log.debug("User [{0}] has removed or blocked the bot: {1}".format(self.user_info(chat_id), chat_id))
                return False
            retries += 1
        return True

    def user_info(self, chat_id):
        try:
            chat = self.bot.getChat(chat_id = chat_id)
        except telegram.error.TelegramError:
            return "N/A"

        message = "{0}: ".format(chat_id)
        if chat.first_name is not None:
            message += chat.first_name + " "
        if chat.last_name is not None:
            message += chat.last_name + " "
        if chat.title is not None:
            message += chat.title + " "
        if chat.username is not None:
            message += "(@" + chat.username + ")"
        return message

    def send_to_all(self, message):
        self.log.info("Notifying all subscribers: " + message)
        to_remove = []
        for sub in self.conf.subscribers:
            if not send(bot = self.bot, chat_id = sub, message = message):
                to_remove.append(sub)
        for sub in to_remove:
            self.conf.subscribers.remove(sub)

    def stop(self):
        self.updater.stop()
