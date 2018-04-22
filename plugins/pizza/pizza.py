import re
from json import loads
from os import path

dirname = path.dirname(__file__)
pizza_file = path.join(dirname, "pizza.json")


class Pizza(object):
    trigger = re.compile('pizza', flags=re.I)

    def can_respond_to(self, sentence):
        return re.search(self.trigger, sentence)

    def response(self):
        source = loads(open(pizza_file).read())
        return "\n".join(
            f">• <{details['URL']}|{place}>: {details['Phone']}"
            for place, details
            in source.items()
        )
