#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import date, timedelta
from collections import namedtuple
from itertools import takewhile

Meal = namedtuple("Meal", ["pris", "navn", "beskrivelse"])

base_url = "http://samskipnaden.no/dagens-meny/day/1/{:%Y%m%d}"

SKIP_LIST = ("Markedet", "ILP-kafeen", "Musikkafeen")
MH_mantor = "17:00"
MH_fre = "16:00"
Teo_mantor = "17:30"
Teo_fre = "17:00"

MH_OPENING_HOURS = { 0: MH_mantor, 1: MH_mantor, 2: MH_mantor, 3: MH_mantor, 4: MH_fre}
TEO_OPENING_HOURS = { 0: Teo_mantor, 1: Teo_mantor, 2: Teo_mantor, 3: Teo_mantor, 4: Teo_fre}

OPENING_HOURS = {"MH-kafeen": MH_OPENING_HOURS, "Teorifagskafeen": TEO_OPENING_HOURS}

def get_menu(other_day=False):
    day = other_day or date.today()
    # print(f"Fetching {base_url.format(day)}...")
    web_content = urlopen(base_url.format(day)).read()
    soup = BeautifulSoup(web_content, "html.parser")
    content = soup.find("div", class_="view-content-rows").find_all("div", class_="view-grouping-title")

    das_dict = dict()

    for x in content:
        if x.string in SKIP_LIST:
            # print("Skipping ", x.string)
            continue
        das_dict[x.string] = dict()
        for submenu in takewhile(lambda x: x not in content, x.find_next_siblings("div")):
            try:
                mealtime = submenu.find("h3").string
            except AttributeError:
                continue
            das_dict[x.string][mealtime] = parse_menu_from_ul(submenu("li"))

    return das_dict


def parse_menu_from_ul(unordered_list):
    menu = list()
    for x in unordered_list:
        price = x.find("div", class_="views-field views-field-field-price").string
        name = x.find("div", class_="views-field views-field-field-dish").string
        desc = x.find("div", class_="views-field views-field-field-description").string
        menu.append(Meal(navn=name, pris=price, beskrivelse=desc))

    return menu


def print_menu(menu_dict):
    print(string_menu(menu_dict))


def string_menu(menu_dict):
    result = ""
    day = date.today().weekday()

    for place, menus in menu_dict.items():
        try:
            opening_hours = "stenger *{}* i dag".format(OPENING_HOURS[place][day])
        except KeyError:
            opening_hours = "stengt i dag"
        result += "*{}* ({}) serverer:\n".format(place, opening_hours)
        for menu, items in menus.items():
            result += ">*{}*\n".format(menu)
            for meal in sorted(items):
                result += ">• *{meal.pris}* {meal.navn} ({meal.beskrivelse})\n".format(meal=meal)
    return result


if __name__ == "__main__":
    day = date.today()
    menu = get_menu(day)
    print_menu(menu)
