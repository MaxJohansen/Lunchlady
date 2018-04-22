from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import date, time
from itertools import takewhile
from os import path
from json import loads
import re

dirname = path.dirname(__file__)

base_url = "http://samskipnaden.no/dagens-meny/day/1/{:%Y%m%d}"


class Core(object):
    trigger = re.compile('lunsj|lunch|middag|dinner', flags=re.I)

    def can_respond_to(self, sentence):
        return re.search(self.trigger, sentence)

    def __init__(self, source=None, date=date.today()):
        if source is None:  # pragma: no cover
            self.source = urlopen(base_url.format(date))
        else:
            self.source = source
        self.day = date.weekday()
        self.opening_hours = loads(
            open(path.join(dirname, "opening_hours.json")).read())

    def response(self):
        daily_menus = self.soupify() \
            .find("div", class_="view-content-rows") \
            .find_all("div", class_="view-grouping-title")
        das_dict = dict()

        for x in daily_menus:
            das_dict[x.string] = dict()
            for submenu in takewhile(lambda x: x not in daily_menus, x.find_next_siblings("div")):
                try:
                    mealtime = submenu.find("h3").string
                except AttributeError:
                    mealtime = "Ukategorisert"
                das_dict[x.string][mealtime] = self.parse_menu_from_ul(
                    submenu("li"))
        return self.string_menu(das_dict)

    def soupify(self):
        html = self.source.read()
        return BeautifulSoup(html, "html.parser")

    def string_menu(self, menu_dict):
        result = ""
        for place, menus in menu_dict.items():
            opening_hours = self.get_opening_hours(place)
            result += f"*{place}* (stenger *{opening_hours}* i dag) serverer:\n".format(place,
                                                                                        opening_hours)
            for menu, items in menus.items():
                result += f">*{menu}*\n"
                for meal in sorted(items):
                    result += f">• {meal}\n"
        return result

    def get_opening_hours(self, place):
        return self.opening_hours[place][self.day]

    def extract_element(self, navstring, fieldname):
        try:
            res = navstring.find(
                "div", class_=f"views-field-{fieldname}").find("div").string
        except AttributeError:
            res = navstring.find(
                "div", class_=f"views-field-{fieldname}").find("strong").string

        if not res:
            res = navstring.find(
                "div", class_="views-field-nothing").find("strong").string
        return res.strip() or "Nothing"

    def parse_menu_from_ul(self, unordered_list):
        menu = list()
        for x in unordered_list:
            prices = [int(x) for x in re.findall(
                "\d+", self.extract_element(x, "field-price"))]
            name = self.extract_element(x, "nothing")
            desc = self.extract_element(x, "field-description")
            menu.append(Meal(name, desc, prices))

        return menu


class Meal(object):
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
