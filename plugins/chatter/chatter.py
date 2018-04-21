import random
from json import loads
from os import path

dirname = path.dirname(__file__)
chatter_lines = path.join(dirname, "lines.json")


class Chatter(object):
    def response(self):
        lines = loads(open(chatter_lines).read())
        return random.choice(lines)
