#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import random
import re
from slackclient import SlackClient
from lunchlady import string_menu, daily_menu, pizza_menu, bazinga_menu, mat_menu
from datetime import datetime, timedelta

BOT_ID = "10" #os.environ.get("BOT_ID")
RESPONSE_DELAY = timedelta(minutes=1)


class Lunchlady(object):
    def __init__(self):
        self.can_speak_again = datetime.now()
        self.name_match = re.compile("<@" + BOT_ID + ">|doris", flags=re.I)
        self.keywords = {
            "lunsj|lunch|dinner|middag": daily_menu,
            "pizza": pizza_menu,
            "bazinga": bazinga_menu,
            "mat": mat_menu
            }
        self.other_responses = ["Whatever.",
                                "Okey dokey.",
                                "Yon meat, 'tis sweet as summer's wafting breeze.",
                                "Mine ears are only open to the pleas of those who speak ye olde English.",
                                "Speak up, kid.",
                                "Your mother wears army boots."]

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        if datetime.now() < self.can_speak_again:
            print("can't speak until", self.can_speak_again)
        else:
            self.can_speak_again = datetime.now() + RESPONSE_DELAY

        response = ""
        print(command)
        for string, menu in self.keywords.items():
            if re.compile(string, flags=re.I).search(command):
                response = string_menu(menu())
                break
        else:
            response = random.choice(self.other_responses)

        if not response:
            response = "There are no menus available right now. How about you order some pizza instead?\n" + pizza_menu()

        slack_client.api_call("chat.postMessage", channel=channel,
                              unfurl_links=False,
                              text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        if slack_rtm_output:
            for output in slack_rtm_output:
                if output and 'text' in output and self.name_match.search(output['text']):
                    return output['text'], output['channel']
        return None, None


def reconnect(bot):
    if slack_client.rtm_connect():
        print("Doris is connected and running!")
        while True:
            command, channel = bot.parse_slack_output(slack_client.rtm_read())
            if command and channel:
                bot.handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



if __name__ == "__main__":
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    doris = Lunchlady()
    while True:
        try:
            reconnect(doris)
        except ConnectionResetError:
            continue
