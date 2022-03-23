import pygame as pg

MAIN_GRAY = (191, 191, 191)
DARK_GRAY = (127, 127, 129)

UPDATEBOUNDSEVENT = pg.USEREVENT + 1
TOGGLECURSOREVENT = pg.USEREVENT + 2

DEFAULT_PRESETS = {'beginner': {'field_size': [9, 9], 'mines_count': 10},
                   'intermediate': {'field_size': [16, 16], 'mines_count': 40},
                   'expert': {'field_size': [30, 16], 'mines_count': 99}}
