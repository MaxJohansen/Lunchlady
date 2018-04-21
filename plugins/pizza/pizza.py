from json import loads
from os import path

dirname = path.dirname(__file__)
pizza_file = path.join(dirname, "pizza.json")


class PizzaMenu(object):
    def __init__(self):
        self.source = loads(open(pizza_file).read())

    def response(self):
        return "\n".join(
            f">• <{details['URL']}|{place}>: {details['Phone']}"
            for place, details
            in self.source.items()
        )
