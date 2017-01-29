import os
import time
from slackclient import SlackClient
from lunchlady import get_menu, string_menu


BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
KEYWORDS = {"lunch", "lunsj", "dinner", "middag"}


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = ""
    found_keyword = command.intersection(KEYWORDS)
    if found_keyword:
        response = string_menu(get_menu())
    else:
        response = "Whatever."

    if not response:
        response = "Nothin' today, sweetheart."

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    print(slack_rtm_output)
    if slack_rtm_output:
        for output in slack_rtm_output:
            if output and 'text' in output and AT_BOT in output['text']:
                return set(output['text'].split(AT_BOT)[1].strip().lower().split()), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Doris is connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")