#!/usr/bin/env python3

import logging
import re
import json
import requests

class Instagram:
    def __init__(self, username):
        self.log = logging.getLogger("LordeSocialBot.Instagram")
        self.log.info("Initializing Instagram API")
        self.username = username

        # We will retry as long as necessary
        self.old = None
        while self.old is None:
            self.old = self.get_current()

    def get_current(self):
        self.log.debug("Getting new Instagram posts")
        try:
            response = requests.get("https://instagram.com/" + self.username)
        except requests.exceptions.RequestException as e:
            self.log.debug(str(e))
            return None

        regex = re.search('<script type="text/javascript">window\._sharedData = (.*);</script>', response.text)
        if regex is None:
            self.log.warning("Could not parse Instagram website")
            return None

        try:
            j = json.loads(regex.group(1))
            nodes = j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
            codes = [node["code"] for node in nodes]
            if codes == []:
                return None
            return codes
        except json.JSONDecodeError as e:
            self.log.warning(str(e))
            return None
        except (IndexError, KeyError, TypeError):
            self.log.warning("Could not parse Instagram website")
            return None
