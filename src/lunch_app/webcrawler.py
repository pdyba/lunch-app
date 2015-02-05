from bs4 import BeautifulSoup
from urllib import request


def get_dania_dnia_from_pod_koziolek():
    webpage = request.urlopen("http://www.pod-koziolkiem.pl/")
    soup = BeautifulSoup(webpage.read())
    lista = []
    menu = soup.find_all(
        "span",
        {
            "style": "color: #ffffff; font-family: 'Segoe Print',"
                     " sans-serif; font-size: medium; line-height: 1.3em;"
        },
    )
    for meal in menu:
        for food in meal:
            thing = "{}".format(food)
            thing = thing.strip("\xa0")
            if thing != "<br/>" and thing and thing != "\xa0" \
                    and thing != ":):)":
                lista.append(thing)
    danie_dnia = {}
    lista.pop(0)
    zupa_dnia = lista[0]
    if not lista[1].startswith("1."):
        if "zupa" in lista[1]:
            zupa_dnia_2 = lista[1]
            if not lista[2].startswith("1."):
                zupa_dnia += lista[2]
                lista.pop(2)
            danie_dnia["zupa_dnia_2"] = zupa_dnia_2
            lista.pop(1)
        else:
            zupa_dnia += lista[1]
            lista.pop(1)
    lista.pop(0)
    danie_dnia["zupa_dnia"] = zupa_dnia
    danie_dania_1 = ""
    while not lista[0].startswith("2.") and lista[0]:
        danie_dania_1 += lista[0]
        danie_dania_1 += " "
        lista.pop(0)
    danie_dania_1 = danie_dania_1.strip(" ")
    danie_dnia["danie_dania_1"] = danie_dania_1
    if lista[0]:
        danie_dania_2 = ""
        for line in lista:
            danie_dania_2 += line
            danie_dania_2 += " "
        danie_dania_2 = danie_dania_2.strip(" ")
        danie_dnia["danie_dania_2"] = danie_dania_2
    return danie_dnia


def get_week_from_tomas():
    webpage = request.urlopen("http://www.tomas.net.pl/niagara.php")
    soup = BeautifulSoup(webpage.read())
    menu = soup.find_all("td", {"class": "biala"})
    lista = []
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
            thing = "{}".format(food)
            thing = thing.replace("\n", "")
            thing = thing.replace("\t", "")
            thing = thing.replace('<span class="biala">', "")
            thing = thing.replace('<span class="dzien">', "")
            thing = thing.replace('</span>', "")
            thing = thing.strip("\xa0")
            thing = thing.strip()
            if thing != "<br/>" and thing and thing != "\xa0" \
                    and thing != ":):)":
                lista.append(thing)
    while "kcal" in str(lista) and lista[0]:
        danie = lista[0]
        lista.pop(0)
        while "kcal" not in lista[0] and lista[0] != 'ZUPA DNIA:' and lista[0]:
            danie += " "
            danie += lista[0]
            lista.pop(0)
        tomas_menu['diet'].append(danie)
    for i in range(1, 6):
        day_manu = {
            'zupy': [],
            'dania': [],
            'zupa_i_dania': [],
        }
        if lista[0] == 'ZUPA DNIA:':
            lista.pop(0)
        zupy = lista[0].split(',')
        for zupa in zupy:
            zupa = zupa.strip()
            zupa = zupa.strip('.')
            day_manu['zupy'].append(zupa)
        lista.pop(0)
        if lista[0] == 'DANIE DNIA:':
            lista.pop(0)
        while lista and lista[0] != 'ZUPA DNIA:':
            day_manu['dania'].append(lista[0])
            lista.pop(0)
        for zupa in day_manu['zupy']:
            for danie in day_manu['dania']:
                zupa_i_dania = zupa + " + " + danie
                day_manu['zupa_i_dania'].append(zupa_i_dania)
        tomas_menu['dzien_{}'.format(i)] = day_manu

    return tomas_menu
