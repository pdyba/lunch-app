# -*- coding: utf-8 -*-
"""
mock for tests
"""
from unittest.mock import Mock
from os import path

MOCK_ADMIN = Mock()
MOCK_ADMIN.is_admin.return_value = True
MOCK_ADMIN.username = 'test_user'
MOCK_ADMIN.active = True
MOCK_ADMIN.is_anonymous.return_value = False
MOCK_ADMIN.is_active.return_value = True
MOCK_ADMIN.email = 'mock@mock.com'
MOCK_ADMIN.id = 1

MOCK_DATA_KOZIOLEK = Mock()
MOCK_DATA_KOZIOLEK.return_value = {
    'danie_dania_1':
        '1.Kotlet schabowy z ziemniakami gotowanymi i kapusta zasmażana',
    'danie_dania_2':
        '2.Placki ziemniaczane z gulaszem wieprzowym i surówka',
    'zupa_dnia':
        'Zupa Ogórkowa'
}
MOCK_DATA_TOMAS = Mock()
MOCK_DATA_TOMAS.return_value = {
    'dzien_2': {
        'dania': [
            'Pierś z kurczaka panierowana faszerowana boczkiem i serem.',
            'Pulpety wieprzowe w sosie koperkowym, ryż, marchew z groszkiem.',
            'Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
        ],
        'zupy': [
            'żurek',
            'grochówka',
        ],
        'zupa_i_dania': [
            'żurek + Pierś z kurczaka panierowana faszerowana boczkiem.',
            'żurek + Pulpety wieprzowe w sosie koperkowym, ryż, marchew.',
            'żurek + Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
            'grochówka + Pierś z kurczaka panierowana faszerowana boczkiem.',
            'grochówka + Pulpety wieprzowe w sosie koperkowym, ryż.',
            'grochówka + Sałatka z kurczakiem, warzywami i sosem czosnkowym.',
        ]
    },
    'diet': [
        'ok.440kcal Polędwiczki drobiowe 120g, ryż 200g, bukiet warzyw 150g.',
        'ok.490kcal Pierś drobiowa z grilla 120g, kasza  200g, sałata  150g.',
    ],
    'dzien_4': {
        'dania': [
            'Medalion drobiowy panierowany zapiekany z ananasem, ziemniaki.',
            'Leczo węgierskie z mięsem wieprzowym, ryż, surówka kapusty.',
            'Sałatka grillowanym mięsem, warzywami i sosem czosnkowym.',
        ],
        'zupy': [
            'żurek',
            'krem z brokuł',
        ],
        'zupa_i_dania': [
            'żurek + Medalion drobiowy panierowany zapiekany z ananasem.',
            'żurek + Leczo węgierskie z mięsem wieprzowym, ryż, surówka.',
            'żurek + Sałatka grillowanym mięsem, warzywami i sosem czosnko.',
            'krem z brokuł + Medalion drobiowy panierowany zapiekany.',
            'krem z brokuł + Leczo węgierskie z mięsem wieprzowym, ryż.',
            'krem z brokuł + Sałatka grillowanym mięsem, warzywami.',
        ]
    },
    'dzien_1': {
        'dania': [
            'Kawałki kurczaka w sosie chińskim z warzywami, ryż, sałata.',
            'Schab panierowany zapiekany z pieczarkami, ziemniaki.',
            'Sałatka z serem feta, warzywami i sosem vinegret.',
        ],
        'zupy': [
            'żurek',
            'kapuśniak',
        ],
        'zupa_i_dania': [
            'żurek + Kawałki kurczaka w sosie chińskim z warzywami.',
            'żurek + Schab panierowany zapiekany z pieczarkami.',
            'żurek + Sałatka z serem feta, warzywami i sosem vinegret.',
            'kapuśniak + Kawałki kurczaka w sosie chińskim z warzywami.',
            'kapuśniak + Schab panierowany zapiekany z pieczarkami.',
            'kapuśniak + Sałatka z serem feta, warzywami i sosem vinegret.',
        ]
    },
    'dzien_5': {
        'dania': [
            'Miruna panierowana, ziemniaki, surówka z kiszonej kapusty.',
            'Naleśniki zapiekane z kurczakiem (3 szt.), sałata.',
            'Sałatka z tuńczykiem, warzywami, jajkiem i sosem vinegret.',
        ],
        'zupy': [
            'żurek',
            'barszcz ukraiński',
        ],
        'zupa_i_dania': [
            'żurek + Miruna panierowana, ziemniaki, surówka.',
            'żurek + Naleśniki zapiekane z kurczakiem (3 szt.).',
            'żurek + Sałatka z tuńczykiem, warzywami, jajkiem.',
            'barszcz ukraiński + Miruna panierowana, ziemniaki.',
            'barszcz ukraiński + Naleśniki zapiekane z kurczakiem (3 szt.).',
            'barszcz ukraiński + Sałatka z tuńczykiem, warzywami.',
        ]
    },
    'dzien_3': {
        'dania': [
            'Filet drobiowy w płatkach kukurydzianych, ziemniaki, surówka.',
            'Karkówka z grilla, frytki, sałata z warzywami.',
            'Sałatka z warzywami, serem mozzarella i sosem winegret.',
        ],
        'zupy': [
            'żurek',
            'ogórkowa',
        ],
        'zupa_i_dania': [
            'żurek + Filet drobiowy w płatkach kukurydzianych.',
            'żurek + Karkówka z grilla, frytki, sałata.',
            'żurek + Sałatka z warzywami, serem mozzarella.',
            'ogórkowa + Filet drobiowy w płatkach kukurydzianych.',
            'ogórkowa + Karkówka z grilla, frytki, sałata z warzywami.',
            'ogórkowa + Sałatka z warzywami, serem mozzarella.',
        ]
    }
}

MOCK_WWW_TOMAS = Mock()
MOCK_WWW_TOMAS.return_value = open(
    path.abspath(
        path.join(path.dirname(__file__), '../../etc/mock_tomas.html')
    )
)

MOCK_WWW_KOZIOLEK = Mock()
MOCK_WWW_KOZIOLEK.return_value = open(
    path.abspath(
        path.join(path.dirname(__file__), '../../etc/mock_koziolek.html')
    )
)
