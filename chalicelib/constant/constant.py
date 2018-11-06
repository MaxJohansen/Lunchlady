import re
import logging
from bs4 import BeautifulSoup
from datetime import date
from urllib.request import urlopen
from os import path
from json import loads

logger = logging.getLogger(f"doris.plugins.{__name__}")

dirname = path.dirname(__file__)
urls = {
    "BAZINGA": "https://samskipnaden.no/tromso/mat-drikke/vare-kafeer-og-kaffebarer/bazinga",
    "MAT": "https://samskipnaden.no/tromso/mat-drikke/vare-kafeer-og-kaffebarer/mat",
    "MIX": "https://samskipnaden.no/tromso/mat-drikke/vare-kafeer-og-kaffebarer/mix-kiosken",
}


class Constant:
    places = "|".join(["\\bMAT\\b", "\\bBAZINGA\\b", "\\bMIX\\b", "kiosk"])
    trigger = re.compile(places, flags=re.I)

    def __init__(self, source=None, date=date.today()):
        self.day = date.weekday()
        self.opening_hours = loads(
            open(path.join(dirname, "opening_hours.json")).read()
        )

    @classmethod
    def can_respond_to(self, sentence):
        return bool(self.trigger.search(sentence))

    def is_open(self, place):
        try:
            return self.opening_hours[place][self.day]
        except IndexError:
            return False

    def response(self, *args):
        place = self.trigger.search(args[0])[0].upper()
        if place == "KIOSK":
            place = "MIX"
        if not self.is_open(place):
            return f"*{place}* is closed today"
        self.source = urlopen(urls[place])
        opening_hours = self.get_opening_hours(place)

        menu = self.soupify().find("div", class_="view-content-rows")

        result = f"{place} (closes at *{opening_hours}* today) are serving:\n"
        result += self.string_menu(self.parse_menu_from_ul(menu("li")))

        return result

    def string_menu(self, items):
        result = f">*Food*\n"
        for meal in sorted(items):
            result += f">• {meal}\n"
        return result

    def get_opening_hours(self, place):
        return self.opening_hours[place][self.day]

    def extract_element(self, navstring, fieldname):
        try:
            res = (
                navstring.find("div", class_=f"views-field-{fieldname}")
                .find("div")
                .string
            )
        except AttributeError:
            res = (
                navstring.find("div", class_=f"views-field-{fieldname}")
                .find("strong")
                .string
            )

        if not res:
            res = (
                navstring.find("div", class_="views-field-nothing")
                .find("strong")
                .string
            )
        return res.strip() or "Nothing"

    def soupify(self):
        html = self.source.read()
        return BeautifulSoup(html, "html.parser")

    def parse_menu_from_ul(self, unordered_list):
        menu = list()
        for li in unordered_list:
            prices = [
                int(price)
                for price in re.findall("\\d+", self.extract_element(li, "field-price"))
            ]
            name = self.extract_element(li, "nothing")
            desc = self.extract_element(li, "field-description")
            menu.append(Meal(name, desc, prices))

        return menu


class Meal:
    def __init__(self, name, description, prices):
        self.prices = prices
        self.price_string = " / ".join([str(x) for x in prices])
        self.name = name
        self.description = description

    def __str__(self):
        res = f"{self.name}"
        if self.price_string:
            res = f"*{self.price_string},-* " + res
        if self.description and self.description != self.name:
            res = res + f" ({self.description})"

        return res

    def __lt__(self, other):
        return self.prices < other.prices
