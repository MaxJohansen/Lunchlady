import random
import re
from json import loads
from os import path

dirname = path.dirname(__file__)
chatter_lines = path.join(dirname, "lines.json")


class Chatter(object):
    trigger = re.compile('h[ae]llo|howdy|h[ae]i', flags=re.I)

    def can_respond_to(self, sentence):
        return re.search(self.trigger, sentence)

    def response(self):
        lines = loads(open(chatter_lines).read())
        return random.choice(lines)
