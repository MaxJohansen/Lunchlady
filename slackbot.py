#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import logging
import time
from slackclient import SlackClient
from plugins.utils import plugin_loader

logger = logging.getLogger('doris')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# INFO is logged to stderr
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Everything is logged to file
fh = logging.FileHandler('doris.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class Lunchlady(object):
    def __init__(self, slackclient):
        self.client = slackclient
        self.plugins = plugin_loader()

    def handle_command(self, user, channel, command):
        """Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """

        user = self.client.server.users.find(user)
        logger.info(
            f"{user.real_name} ({user.name}): \"{command}\"")

        handlers = []
        for plugin in self.plugins:
            if plugin.can_respond_to(command):
                logger.debug(
                    f"'{command}' can be handled by {plugin.__name__}")
                handlers.append(plugin)

        if len(handlers) > 1:
            logger.warning("Found {} handlers for '{}': {}".format(
                len(handlers),
                command,
                ", ".join(handler.__name__ for handler in handlers))
            )

        if handlers:
            handler = handlers[0]
            logger.info(f"Responding with {handler.__name__}")
            response = handler().response(command)
        else:
            try:
                logger.debug(f"'{command}' did not match any handlers")
                chatty = next((x for x in self.plugins if re.match(
                    "chat", x.__name__, flags=re.I)))
                response = chatty().response()
            except:
                logger.debug("Unable to generate response, using default")
                response = "I don't understand what you want from me."

        logger.debug(f"Responding with {response[:40]}")
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response,
            unfurl_links=False,
            as_user=True
        )

    def get_slack_message(self):
        """Returns the user, channel and the text
        from a slack event that includes a text message
        """
        slack_events = self.client.rtm_read()
        if not slack_events:
            return None, None, None

        for event in slack_events:
            if 'text' in event:
                return event['user'], event['channel'], event['text']

        return None, None, None

    def chat_loop(self):
        while True:
            user, channel, text = self.get_slack_message()
            # Only respond if bot was mentioned by name
            if text and self.name_match.search(text) and user is not self.ID:
                self.handle_command(user, channel, text)
            # Sleep 1 second between reads
            time.sleep(1)

    def connect(self):
        if self.client.rtm_connect():
            names = self.client.server.login_data['self']['name'].split('_')
            self.name = " ".join(name.capitalize() for name in names)
            self.ID = self.client.server.login_data['self']['id']
            self.name_match = re.compile(
                f"<@{self.ID}>|{'|'.join(names)}", flags=re.I)
            logger.info(f"{self.name} ({self.ID}) is connected and running!")

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
