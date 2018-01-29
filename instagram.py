#!/usr/bin/env python3

import logging

class Instagram:
    def __init__(username):
        self.log = logging.getLogger("LordeSocialBot.Instagram")
        self.username = username
        self.old = None
        while self.old is None:
            self.old = self.get_current()

    def get_current():
        try:
            response = requests.get("https://instagram.com/" + self.username)
        except requests.exceptions.RequestException as e:
            self.log.debug(str(e))
            return None

        regex = re.search('<script type="text/javascript">window\._sharedData = (.*);</script>', response.text)
        if regex is None:
            self.log.warn("Could not parse Instagram website")
            return None

        try:
            j = json.loads(regex.group(1))
            nodes = j["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]
            codes = [node["code"] for node in nodes]
            if codes == []:
                return None
            return codes
        except json.JSONDecodeError as e:
            self.log.warn(str(e))
            return None
        except (IndexError, KeyError, TypeError):
            self.log.warn("Could not parse Instagram website")
            return None
