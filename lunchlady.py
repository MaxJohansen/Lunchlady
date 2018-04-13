#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import date
from itertools import takewhile
from bettertime import HumanTime
from requests import get
import re


class Meal(object):
    def __init__(self, prices, name, description):
        self.prices = prices
        self.price_string = " / ".join([str(x) for x in prices])
        self.name = name
        self.description = description

    def __str__(self):
        res = f"{self.name}"
        if self.price_string:
            res = f"*{self.price_string},-* " + res
        if self.description:
            res = res + f" ({self.description})"

        return res

    def __lt__(self, other):
        return self.prices < other.prices


base_url = "http://samskipnaden.no/dagens-meny/day/1/{:%Y%m%d}"

joke_url = "https://icanhazdadjoke.com"
joke_header = {'Accept': 'text/plain'}

# We ignore these cafeterias because they're inconveniently located
SKIP_LIST = ("Markedet", "ILP-kafeen", "Musikkafeen")

# TODO: Implement a better solution for opening hours. This hardcoding is awful.
MH_mantor = HumanTime(17)
MH_fre = HumanTime(16)
Teo_mantor = HumanTime(17, 30)
Teo_fre = HumanTime(17)
Bazinga = HumanTime(18)
Mat_mantor = HumanTime(17)
Mat_fre = HumanTime(16)

MH_OPENING_HOURS = {0: MH_mantor, 1: MH_mantor,
                    2: MH_mantor, 3: MH_mantor, 4: MH_fre}
TEO_OPENING_HOURS = {0: Teo_mantor, 1: Teo_mantor,
                     2: Teo_mantor, 3: Teo_mantor, 4: Teo_fre}
BAZINGA_OPENING_HOURS = {n: Bazinga for n in range(5)}
MAT_OPENING_HOURS = {0: Mat_mantor, 1: Mat_mantor,
                     2: Mat_mantor, 3: Mat_mantor, 4: Mat_fre}

OPENING_HOURS = {"MH-kafeen": MH_OPENING_HOURS,
                 "Teorifagskafeen": TEO_OPENING_HOURS,
                 "BAZINGA": BAZINGA_OPENING_HOURS,
                 "MAT.": MAT_OPENING_HOURS}

PIZZA_PLACES = {"Pizzabakeren": {"URL": "https://www.pizzabakeren.no/pizzameny", "Phone": "77 68 06 10"},
                "Dolly Dimples": {"URL": "https://www.dolly.no/meny/pizza", "Phone": "0 44 40"},
                "Peppe's Pizza": {"URL": "https://www.peppes.no/pp13/wicket/bookmarkable/no.peppes.pepp2013.bestill.pizza.PeppesPizzaIntroPage?14", "Phone": "22 22 55 55"},
                "Retro House": {"URL": "https://www.facebook.com/Retro-Pizzeria-910569502345280/", "Phone": "77 67 77 77"}}


def get_soup():
    # print(f"Fetching {base_url.format(day)}...")
    web_content = urlopen(base_url.format(date.today())).read()
    return BeautifulSoup(web_content, "html.parser")


def daily_menu():
    daily_menus = get_soup().find(
        "div", class_="view-content-rows").find_all("div", class_="view-grouping-title")
    das_dict = dict()

    for x in daily_menus:
        if x.string in SKIP_LIST:
            # print("Skipping ", x.string)
            continue
        das_dict[x.string] = dict()
        for submenu in takewhile(lambda x: x not in daily_menus, x.find_next_siblings("div")):
            try:
                mealtime = submenu.find("h3").string
            except AttributeError:
                continue
            das_dict[x.string][mealtime] = parse_menu_from_ul(submenu("li"))
    return das_dict


def bazinga_menu():
    wanted = re.compile("bazinga", flags=re.I)
    static_menus = get_soup().find(
        "div", class_="views-view--dish-of-the-day-calendar--attachment-1").find_all("div", class_="view-grouping-title")

    for x in static_menus:
        if not wanted.search(x.string):
            continue
        for submenu in takewhile(lambda x: x not in static_menus, x.find_next_siblings("div")):
            return {x.string: {"Fast meny": parse_menu_from_ul(submenu("li"))}}


def mat_menu():
    wanted = re.compile("mat", flags=re.I)
    static_menus = get_soup().find(
        "div", class_="views-view--dish-of-the-day-calendar--attachment-1").find_all("div", class_="view-grouping-title")

    for x in static_menus:
        if not wanted.search(x.string):
            continue
        for submenu in takewhile(lambda x: x not in static_menus, x.find_next_siblings("div")):
            return {x.string: {"Fast meny": parse_menu_from_ul(submenu("li"))}}


def extract_element(navstring, fieldname):
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


def parse_menu_from_ul(unordered_list):
    menu = list()
    for x in unordered_list:
        # TODO: Put this in a MealFactory
        price = [int(x) for x in re.findall(
            "\d+", extract_element(x, "field-price"))]
        name = extract_element(x, "nothing")
        desc = extract_element(x, "field-description")
        if not name:
            continue
        menu.append(Meal(price, name, desc))

    return menu


def print_menu(menu_dict):
    print(string_menu(menu_dict))


def string_menu(menu_dict):
    if isinstance(menu_dict, (str)):
        return menu_dict
    result = ""
    day = date.today().weekday()
    for place, menus in menu_dict.items():
        try:
            opening_hours = f"stenger *{OPENING_HOURS[place][day].strftime('%H:%M')}* i dag"
        except KeyError:
            opening_hours = "stengt i dag"
        result += f"*{place}* ({opening_hours}) serverer:\n".format(place,
                                                                    opening_hours)
        for menu, items in menus.items():
            result += f">*{menu}*\n"
            for meal in sorted(items):
                result += f">• {meal}\n"
    return result


def pizza_menu():
    result = ""
    for place, details in PIZZA_PLACES.items():
        result += f">• <{details['URL']}|{place}>: {details['Phone']}\n"
    return result

def joke_menu():
    """Gets a joke from icanhazdadjoke-API"""
    joke = get(joke_url, headers = joke_header)

    return joke.content.decode("utf-8")
    
if __name__ == "__main__":
    day = date.today()
    joke = joke_menu()
    print(joke)
