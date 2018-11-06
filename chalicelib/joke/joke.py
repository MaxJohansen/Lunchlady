import html
import re
from requests import get
import logging

logger = logging.getLogger(f"doris.plugins.{__name__}")


class Joke:
    trigger = re.compile("joke|funny", flags=re.I)
    joke_url = "https://icanhazdadjoke.com"
    stronk_joke_url = (
        "http://api.icndb.com/jokes/random?firstName=Lunchlady&lastName=Doris"
    )

    @classmethod
    def can_respond_to(self, sentence):
        return bool(self.trigger.search(sentence))

    def response(self, *args):
        command = args[0]
        if re.search("stronk", command, re.I):
            logger.debug("Fetching a STRONK joke!")
            joke = get(self.stronk_joke_url)
            joke = joke.json()["value"]["joke"]
            joke = html.unescape(joke)
            return (
                joke.replace(" He ", " She ")
                .replace(" he ", " she ")
                .replace(" He's ", " She's")
                .replace(" he's ", " she's")
                .replace(" His ", " Her ")
                .replace(" his ", " her ")
                .replace(" him ", " her ")
            )
        else:
            logger.debug("Fetching a dad joke")
            joke = get(self.joke_url, headers={"Accept": "text/plain"})
            joke = joke.content.decode("utf-8")
            joke = html.unescape(joke)
            return joke
