# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, no-member
"""
Webrcrawlers functions
"""
from bs4 import BeautifulSoup
from urllib import request
from .main import app

def read_webpage(webpage):
    return webpage.read()


def get_dania_dnia_from_pod_koziolek():
    """
    Returns data for new meal of a day.
    """
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
        for food in meal:
            itme = "{}".format(food)
            itme = itme.strip("\xa0")
            if itme != "<br/>" and itme and itme != "\xa0" \
                    and itme != ":):)":
                list_of_meals.append(itme)
    meal_of_a_day = {}
    list_of_meals.pop(0)
    soup_of_a_day = list_of_meals[0]
    if not list_of_meals[1].startswith("1."):
        if "zupa" in list_of_meals[1]:
            soup_of_a_day_2 = list_of_meals[1]
            if not list_of_meals[2].startswith("1."):
                soup_of_a_day += list_of_meals[2]
                list_of_meals.pop(2)
            meal_of_a_day["zupa_dnia_2"] = soup_of_a_day_2
            list_of_meals.pop(1)
        else:
            soup_of_a_day += list_of_meals[1]
            list_of_meals.pop(1)
    list_of_meals.pop(0)
    meal_of_a_day["zupa_dnia"] = soup_of_a_day
    meal_of_a_day_1 = ""
    while not list_of_meals[0].startswith("2.") and list_of_meals[0]:
        meal_of_a_day_1 += list_of_meals[0]
        meal_of_a_day_1 += " "
        list_of_meals.pop(0)
    meal_of_a_day_1 = meal_of_a_day_1.strip(" ")
    meal_of_a_day["danie_dania_1"] = meal_of_a_day_1
    if list_of_meals[0]:
        meal_of_a_day_2 = ' '.join(line for line in list_of_meals)
        meal_of_a_day_2 = meal_of_a_day_2.strip(" ")
        meal_of_a_day["danie_dania_2"] = meal_of_a_day_2
    return meal_of_a_day


def get_week_from_tomas():
    """
    Returns weak of meals from Tomas ! use only on mondays !.
    """
    url = app.config['URL_TOMAS']
    webpage = request.urlopen(url)
    magic_soup = BeautifulSoup(read_webpage(webpage))
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
            item = item.replace("\n", "")
            item = item.replace("\t", "")
            item = item.replace('<span class="biala">', "")
            item = item.replace('<span class="dzien">', "")
            item = item.replace('</span>', "")
            item = item.strip("\xa0")
            item = item.strip()
            if item != "<br/>" and item and item != "\xa0" \
                    and item != ":):)":
                alist.append(item)
    while "kcal" in str(alist) and alist[0]:
        meal = alist[0]
        alist.pop(0)
        while "kcal" not in alist[0] and alist[0] != 'ZUPA DNIA:' and alist[0]:
            meal += " "
            meal += alist[0]
            alist.pop(0)
        tomas_menu['diet'].append(meal)
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
