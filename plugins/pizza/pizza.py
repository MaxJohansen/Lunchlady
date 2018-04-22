import re
from json import loads
from os import path
import logging
logger = logging.getLogger(f"doris.plugins.{__name__}")

dirname = path.dirname(__file__)
pizza_file = path.join(dirname, "pizza.json")


class Pizza(object):
    trigger = re.compile('pizza', flags=re.I)

    @classmethod
    def can_respond_to(self, sentence):
        return bool(self.trigger.search(sentence))

    def response(self, *args):
        source = loads(open(pizza_file).read())
        logger.debug(f"Found {len(source)} pizza options")
        return "\n".join(
            f">• <{details['URL']}|{place}>: {details['Phone']}"
            for place, details
            in source.items()
        )
