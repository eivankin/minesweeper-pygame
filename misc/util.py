import json
import os
import pygame as pg
from functools import lru_cache

from misc.constants import MAIN_GRAY, DARK_GRAY, UPDATEBOUNDSEVENT, DEFAULT_PRESETS
from misc.components import GamePreset


def get_preset_name(radio_group: pg.sprite.Group):
    presets_from_indexes = {i: name for i, name in enumerate(get_presets())}
    return presets_from_indexes.get(
        next(filter(lambda x: x[1].checked, enumerate(radio_group)))[0], 'custom'
    )


def handle_change():
    pg.event.post(pg.event.Event(UPDATEBOUNDSEVENT))


def terminate():
    pg.quit()
    exit()


@lru_cache(maxsize=128)
def get_presets(path: str = 'presets.json') -> dict[str, GamePreset]:
    if os.path.isfile(path):
        with open(path) as data:
            raw_presets = json.load(data)
    else:
        raw_presets = DEFAULT_PRESETS.copy()

    return {name: GamePreset(**raw_presets[name]) for name in raw_presets}


@lru_cache(maxsize=1024)
def load_image(name: str, color_key=None):
    fullname = os.path.join('assets', name)
    image = pg.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def draw_cell(width, height, indent=3, convex=True,
              primary_color=MAIN_GRAY, shadow_color=DARK_GRAY, glare_color='white') -> pg.Surface:
    surface = pg.Surface((width, height))
    points = [(0, height), (height / 2, height / 2), (width - height / 2, height / 2), (width, 0)]
    bright_vertex, dark_vertex = ((0, 0), (width, height)) if convex else ((width, height), (0, 0))
    pg.draw.polygon(surface, pg.Color(glare_color), [*points, bright_vertex])
    pg.draw.polygon(surface, shadow_color, [*points, dark_vertex])
    pg.draw.rect(surface, primary_color, (indent, indent, width - indent * 2,
                                          height - indent * 2), 0)
    return surface
