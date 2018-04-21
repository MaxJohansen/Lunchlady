import random
from json import loads
from os import path

dirname = path.dirname(__file__)
chatter_lines = path.join(dirname, "lines.json")


class Chatter(object):
    def __init__(self):
        self.lines = loads(open(chatter_lines).read())

    def response(self):
        return random.choice(self.lines)
