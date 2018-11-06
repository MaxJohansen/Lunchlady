import random
import re
import logging
from json import loads
from os import path

logger = logging.getLogger(f"doris.plugins.{__name__}")

dirname = path.dirname(__file__)
chatter_lines = path.join(dirname, "lines.json")


class Chatter:
    trigger = re.compile("h[ae]llo|howdy|h[ae][iy]", flags=re.I)

    @classmethod
    def can_respond_to(self, sentence):
        return bool(self.trigger.search(sentence))

    def response(self, *args):
        lines = loads(open(chatter_lines).read())

        return random.choice(lines)
