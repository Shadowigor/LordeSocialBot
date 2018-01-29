#!/usr/bin/env python3

import config
import logging

class TelegramCommands:
    def __init__(config, telegram):
        self.conf = config
        self.log = logging.getLogger("LordeSocialBot.TelegramCommands")
        self.telegram = telegram

    # === USER COMMANDS =======================================================
    def start(bot, update):
        chat_id = update.message.chat_id
        if not chat_id in self.conf.subscribers:
            self.conf.subscribers.append(chat_id)
            self.telegram.send(bot = bot, chat_id = chat_id, text = "Hello! From now on, I will keep you informed whenever Ella tweets, likes on Twitter or posts on Instagram! You can unsubscribe again with /stop.")
            log.info("Somebody subscribed: [{0}]".format(self.telegram.user_info(chat_id)))
            self.conf.save_subscribers()
        else:
            self.telegram.send(bot = bot, chat_id = chat_id, text = "I have already started!")

    def stop(bot, update):
        chat_id = update.message.chat_id
        if chat_id in self.conf.subscribers:
            self.conf.subscribers.remove(chat_id)
            self.telegram.send(bot = bot, chat_id = chat_id, text = "You have successfully unsubscribed. Bye!")
            self.log.info("Somebody unsubscribed: [{0}]".format(self.telegram.user_info(chat_id)))
            

    def help(bot, update):
        self.telegram.send(bot = bot, chat_id = update.message.chat_id, message = "Available commands\n\n/start  Start the bot\n/stop   Stop the bot")

    # === ADMIN COMMANDS ======================================================
    def userlist(bot, update):
        if str(update.message.chat_id) == self.conf.admin_id:
            message = "A list of all current subscribers:\n"
            for sub in self.conf.subscribers:
                message += " - {0}\n ".format(self.telegram.user_info(sub))
            self.telegram.send(bot = bot, chat_id = update.message.chat_id, message = message)
