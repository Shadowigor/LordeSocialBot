#!/usr/bin/env python3

import config
import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram_commands import TelegramCommands

class Telegram:
    def __init__(config):
        self.conf = config
        self.log = logging.getLogger("LordeSocialBot.Telegram")
        self.updater = Updater(token = self.conf.telegram_token)
        dispatcher = updater.dispatcher
        self.bot = updater.bot
        commands = TelegramCommands()
        dispatcher.add_handler(CommandHandler("start", commands.start))
        dispatcher.add_handler(CommandHandler("stop", commands.stop))
        dispatcher.add_handler(CommandHandler("help", commands.help))
        dispatcher.add_handler(CommandHandler("userlist", commands.userlist))
        dispatcher.add_handler(CommandHandler("start@lordesocialbot", commands.start))
        dispatcher.add_handler(CommandHandler("stop@lordesocialbot", commands.stop))
        dispatcher.add_handler(CommandHandler("help@lordesocialbot", commands.help))
        dispatcher.add_handler(CommandHandler("userlist@lordesocialbot", commands.userlist))
        updater.start_polling(timeout = 0, read_latency = 10)

    def send(chat_id, message):
        retries = 0
        while True:
            try:
                self.bot.send_message(chat_id = chat_id, text = message)
                return True
            except telegram.error.NetworkError as e:
                if retries == 5:
                    self.log.warn("There is still a network error while sending message to user [{0}] after 5 retries: {1}".format(self.user_info(chat_id), str(e)))
                else:
                    self.log.debug("Network error while sending message to user [{0}]: {1}".format(self.user_info(chat_id), str(e)))
            except telegram.error.ChatMigrated as e:
                self.log.debug("Group migrated to supergroup for group [{0}]: {1} -> {2}".format(self.user_info(e.new_chat_id), chat_id, e.new_chat_id))
                self.conf.subscribers[index] = e.new_chat_id
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

    def user_info(chat_id):
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

    def send_to_all(message):
        self.log.info("Notifying subscribers: " + message)
        to_remove = []
        for index, sub in enumerate(self.conf.subscribers):
            if not notify_one(bot = bot, chat_id = chat_id, message = message):
                to_remove.append(sub)
        for sub in to_remove:
            self.conf.subscribers.remove(sub)

    def stop():
        self.updater.stop()
