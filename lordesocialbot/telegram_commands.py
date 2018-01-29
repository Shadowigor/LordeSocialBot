#!/usr/bin/env python3

import logging
from telegram.ext import CommandHandler

class TelegramCommands:
    def __init__(self, config, telegram, dispatcher):
        # List of all commands, including admin commands
        commands = {
            "start",
            "stop",
            "help",
            "userlist"
        }

        self.conf = config
        self.log = logging.getLogger("LordeSocialBot.TelegramCommands")
        self.telegram = telegram

        for command in commands:
            exec("dispatcher.add_handler(CommandHandler('{0}', self.{0}))".format(command))
            exec("dispatcher.add_handler(CommandHandler('{0}@{1}', self.{0}))".format(command, config.bot_name))

    # === USER COMMANDS =======================================================
    def start(self, bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.conf.subscribers:
            self.conf.subscribers.append(chat_id)
            self.telegram.send(bot = bot, chat_id = chat_id, text = "Hello! From now on, I will keep you informed whenever Ella tweets, likes on Twitter or posts on Instagram! You can unsubscribe again with /stop.")
            log.info("Somebody subscribed: [{0}]".format(self.telegram.user_info(chat_id)))
            self.conf.save_subscribers()
        else:
            self.telegram.send(bot = bot, chat_id = chat_id, text = "I have already started!")

    def stop(self, bot, update):
        chat_id = update.message.chat_id
        if chat_id in self.conf.subscribers:
            self.conf.subscribers.remove(chat_id)
            self.telegram.send(bot = bot, chat_id = chat_id, text = "You have successfully unsubscribed. Bye!")
            self.log.info("Somebody unsubscribed: [{0}]".format(self.telegram.user_info(chat_id)))

    def help(self, bot, update):
        self.telegram.send(bot = bot, chat_id = update.message.chat_id, message = "Available commands\n\n/start  Start the bot\n/stop   Stop the bot")

    # === ADMIN COMMANDS ======================================================
    def userlist(self, bot, update):
        if str(update.message.chat_id) in self.conf.admins:
            message = "A list of all current subscribers:\n"
            for sub in self.conf.subscribers:
                message += " - {0}\n ".format(self.telegram.user_info(sub))
            self.telegram.send(bot = bot, chat_id = update.message.chat_id, message = message)
