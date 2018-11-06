import logging
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import date
from itertools import takewhile
from os import path
from json import loads
import re

logger = logging.getLogger(f"doris.plugins.{__name__}")
dirname = path.dirname(__file__)

base_url = "http://samskipnaden.no/dagens-meny/day/1/{:%Y%m%d}"


class Core:
    words = ["lunsj", "lunch", "middag", "dinner", "cook", "food", "h[au]ngr?y"]
    trigger = re.compile("|".join(words), flags=re.I)

    @classmethod
    def can_respond_to(self, sentence):
        relevant = bool(self.trigger.search(sentence))
        weekday = date.today().weekday() in range(0, 5)
        if not weekday:
            logger.debug("Cannot find cafeteria menus on weekends")
        return relevant and weekday

    def __init__(self, source=None, date=date.today()):
        if source is None:  # pragma: no cover
            self.source = urlopen(base_url.format(date))
        else:
            self.source = source
        self.date = date
        self.day = date.weekday()
        self.opening_hours = loads(
            open(path.join(dirname, "opening_hours.json")).read()
        )

    def response(self, *args):
        daily_menus = (
            self.soupify()
            .find("div", class_="view-content-rows")
            .find_all("div", class_="view-grouping-title")
        )

        if not daily_menus:
            logger.info(f"No menus found on {self.date}")
            return "The cafeterias are closed today."

        logger.info(f"Finding menus from {', '.join(x.string for x in daily_menus)}")

        places = dict()
        for x in daily_menus:
            place = dict()
            for submenu in takewhile(
                lambda z: z not in daily_menus, x.find_next_siblings("div")
            ):
                try:
                    mealtime = submenu.find("h3").string
                except AttributeError:
                    mealtime = "Hele dagen"
                place[mealtime] = self.parse_menu_from_ul(submenu("li"))
            places[x.string] = place
        return self.string_menu(places)

    def soupify(self):
        html = self.source.read()
        return BeautifulSoup(html, "html.parser")

    def string_menu(self, menu_dict):
        result = ""
        for place, menus in menu_dict.items():
            opening_hours = self.get_opening_hours(place)
            opening_notice = (
                f"(closes at *{opening_hours}* today)" if opening_hours else ""
            )
            result += f"*{place}* {opening_notice} are serving:\n"
            for menu, items in menus.items():
                result += f">*{menu}*\n"
                for meal in sorted(items):
                    result += f">• {meal}\n"
        return result

    def get_opening_hours(self, place):
        place = self.opening_hours.get(place, None)
        if not place:
            return
        return place[self.day]

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

    def parse_menu_from_ul(self, unordered_list):
        menu = list()
        for li in unordered_list:
            prices = [
                int(price)
                for price in re.findall("\d+", self.extract_element(li, "field-price"))
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
