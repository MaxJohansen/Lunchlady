#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import logging
import time
from slackclient import SlackClient
from plugins.chatter.chatter import Chatter
from plugins.core.core import DailyMenu

logger = logging.getLogger('doris')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Lunchlady(object):
    def __init__(self, slackclient):
        self.client = slackclient
        self.load_modules()
        self.keywords = {
            'lunch|lunsj': DailyMenu
        }

    def load_modules(self):
        pass

    def handle_command(self, user, channel, command):
        """Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """

        user = self.client.server.users.find(user)
        logger.info(f"{user.real_name} ({user.name}): '{command}'")

        response = None
        for word, responder in self.keywords.items():
            if re.compile(word, flags=re.I).search(command):
                logger.debug(f"{command} matched with {word}")
                response = responder().response()
                break

        if not response:
            response = "No food today, sweetheart."

        logger.debug(f"Responding with {response[:40]}")
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response,
            unfurl_links=False,
            as_user=True
        )

    def parse_slack_output(self, slack_rtm_output):
        """Returns the user, channel and the text
        from a slack message object
        """
        if not slack_rtm_output:
            return None, None, None

        logger.debug(f"Incoming: {slack_rtm_output}")
        for output in slack_rtm_output:
            if 'text' in output:
                return output['user'], output['channel'], output['text']

        return None, None, None

    def chat_loop(self):
        while True:
            user, channel, text = self.parse_slack_output(
                self.client.rtm_read())
            # Only respond if bot was mentioned by name
            if text and self.name_match.search(text):
                self.handle_command(user, channel, text)
            # Sleep 1 second between reads
            time.sleep(1)

    def connect(self):
        if self.client.rtm_connect():
            names = self.client.server.login_data['self']['name'].split('_')
            name = " ".join(name.capitalize() for name in names)
            ID = self.client.server.login_data['self']['id']
            self.name_match = re.compile(
                f"<@{ID}>|{'|'.join(names)}", flags=re.I)
            logger.info(f"{name} ({ID}) is connected and running!")

            self.chat_loop()
        else:
            logger.fatal("Connection failed. Invalid Slack token or bot ID?")
            exit()


if __name__ == "__main__":
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    doris = Lunchlady(slack_client)
    while True:
        try:
            doris.connect()
        except ConnectionResetError:
            continue
