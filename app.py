#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import logging
from requests import post
from chalice import Chalice
from chalicelib.utils import plugin_loader

BOT_TOKEN = os.environ["BOT_TOKEN"]
SLACK_URL = "https://slack.com/api/chat.postMessage"

app = Chalice(app_name="lunchlady-doris")
app.debug = True

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("doris")


@app.route("/", methods=["POST"])
def index():
    data = app.current_request.json_body
    if "challenge" in data:
        return data["challenge"]

    slack_event = data["event"]

    if "bot_id" in slack_event:
        logger.warn("Ignoring bot event")
        return

    user = slack_event["user"]
    command = slack_event["text"]
    channel = slack_event["channel"]
    msgtype = slack_event["type"]

    logging.info(f'[{channel}] {user}: "{command}"')

    if not relevant_to_bot(slack_event):
        logger.warn(f"Not relevant to bot: {command} type is {msgtype}")
        return

    response = get_response(command)
    logger.debug(f'Responding with "{truncate(response)}"')
    send_to(channel, response)
    return response


def relevant_to_bot(event):
    bot_mentioned = event["type"] == "app_mention"
    logger.debug(f"Bot was tagged? {bot_mentioned}")
    name_dropped = re.search("doris", event["text"], flags=re.I)
    logger.debug(f"Someone said Doris? {name_dropped}")
    direct_message = event["channel"].startswith("D")
    logger.debug(f"Direct message? {direct_message}")
    return bot_mentioned or name_dropped or direct_message


def send_to(recipient, string):
    post(SLACK_URL, data={"token": BOT_TOKEN, "channel": recipient, "text": string})


def get_response(command):
    handlers = []
    plugins = plugin_loader()
    for plugin in plugins:
        if plugin.can_respond_to(command):
            logger.debug(f'"{command}" can be handled by {plugin.__name__}')
            handlers.append(plugin)

    if len(handlers) > 1:
        names = ", ".join(handler.__name__ for handler in handlers)
        logger.warning(f"Found {len(handlers)} handlers for '{command}': {names}")

    if handlers:
        handler = handlers[0]
        logger.info(f"Asking {handler.__name__} plugin for response")
        return handler().response(command)
    else:
        try:
            logger.debug(f'"{command}" did not match any handlers')
            chatty = next(
                (x for x in plugins if re.match("chat", x.__name__, flags=re.I))
            )
            logger.info(f"Asking {chatty.__name__} plugin for response")
            return chatty().response()
        except (StopIteration, AttributeError):
            return "I do not understand what you want."


def truncate(string):
    if len(string) > 40:
        return string[:37] + "..."
    return string
