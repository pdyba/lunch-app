# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Webrcrawlers functions
"""
from bs4 import BeautifulSoup
from urllib import request
import re


def read_webpage(webpage):
    """
    Returns web page content.
    """
    return webpage.read()


def get_dania_dnia_from_pod_koziolek():
    """
    Returns data for new meal of a day.
    """
    from .main import app

    url = app.config['URL_POD_KOZIOLKIEM']
    webpage = request.urlopen(url)
    magic_soup = BeautifulSoup(read_webpage(webpage))
    list_of_meals = []
    menu = magic_soup.find_all(
        "span",
        {
            "style": "color: #ffffff; font-family: 'Segoe Print',"
                     " sans-serif; font-size: medium; line-height: 1.3em;"
        },
    )
    for meal in menu:
        item = "{}".format(meal.text)
        item = item.strip("\xa0")
        cleaner = (
            item != "<br/>" and
            item and
            item != "\xa0" and
            item != ":):)" and
            "-201" not in item and
            len(item) > 2
        )
        if cleaner and len(re.findall('[0-9]+', item)) <= 1:
            list_of_meals.append(item)
        elif cleaner:
            new_meal_list = re.split('[0-9].', item)
            for meal in enumerate(new_meal_list):
                if meal[1]:
                    list_of_meals.append("{}.{}".format(meal[0], meal[1]))
    meal_of_a_day = {
        "zupy": [],
        "dania_dnia": [],
    }
    number = 0
    while number < len(list_of_meals)-1:
        if list_of_meals[number][0].isdigit() and \
                not list_of_meals[number+1][0].isdigit():
            list_of_meals[number] += list_of_meals[number+1]
            list_of_meals.pop(number+1)
            number = 0
        number += 1
    for meal in list_of_meals:
        if not meal[0].isdigit():
            meal_of_a_day["zupy"].append(meal)
        else:
            meal_of_a_day["dania_dnia"].append(meal)
    return meal_of_a_day


def get_week_from_tomas_crawler():
    """
    Returns weak of meals from Tomas ! use only on mondays !.
    """
    from .main import app

    url = app.config['URL_TOMAS']
    webpage = request.urlopen(url)
    magic_soup = BeautifulSoup(read_webpage(webpage), 'html.parser')
    menu = magic_soup.find_all("td", {"class": "biala"})
    alist = []
    tomas_menu = {
        'diet': [],
        'dzien_1': {},
        'dzien_2': {},
        'dzien_3': {},
        'dzien_4': {},
        'dzien_5': {},
    }
    for meal in menu:
        for food in meal:
            item = "{}".format(food)
            item = item.replace("\n", "").replace("\t", "")\
                .replace('<span class="biala">', "")\
                .replace('<span class="dzien">', "")\
                .replace('</span>', "").strip("\xa0").strip()
            if item != "<br/>" and item and item != "\xa0" \
                    and item != ":):)":
                alist.append(item)
    while "kcal" in str(alist) or "..." in str(alist) and alist[0]:
        meal = alist[0]
        alist.pop(0)
        while ("kcal" and '...') not in alist[0] and alist[0] != 'ZUPA DNIA:':
            meal += alist[0]
            meal += " "
            alist.pop(0)
            tomas_menu['diet'].append(meal.strip('...').strip())

    for i in range(1, 6):
        day_manu = {
            'zupy': [],
            'dania': [],
            'zupa_i_dania': [],
        }
        if alist[0] == 'ZUPA DNIA:':
            alist.pop(0)
        soups = alist[0].split(',')
        for soup in soups:
            soup = soup.strip()
            soup = soup.strip('.')
            day_manu['zupy'].append(soup)
        alist.pop(0)
        if alist[0] == 'DANIE DNIA:':
            alist.pop(0)
        while alist and alist[0] != 'ZUPA DNIA:':
            day_manu['dania'].append(alist[0])
            alist.pop(0)
        for soup in day_manu['zupy']:
            for meal in day_manu['dania']:
                sopu_and_meal = soup + " + " + meal
                day_manu['zupa_i_dania'].append(sopu_and_meal)
        tomas_menu['dzien_{}'.format(i)] = day_manu

    return tomas_menu
