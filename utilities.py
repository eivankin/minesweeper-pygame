import os
import pygame as pg
import re
from functools import lru_cache

MAIN_GRAY = (191, 191, 191)
DARK_GRAY = (127, 127, 129)
PRESETS = {'newbie': {'size': (9, 9), 'mines': 10},
           'amateur': {'size': (16, 16), 'mines': 40},
           'professional': {'size': (30, 16), 'mines': 99}}
PRESETS_FROM_INDEXES = {i: name for i, name in enumerate(PRESETS.keys())}

# defined it here for correct work
radio_group = pg.sprite.Group()
INT_REGEX = r'(^|\-)[0-9]+$'


def get_preset_name():
    return PRESETS_FROM_INDEXES.get(
            next(filter(lambda x: x[1].checked, enumerate(radio_group)))[0], 'custom'
        )


def terminate():
    pg.quit()
    exit()


@lru_cache(maxsize=1024)
def load_image(name: str, color_key=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def draw_cell(width, height, indent=3, convex=True) -> pg.Surface:
    s = pg.Surface((width, height))
    points = [(0, height), (height / 2, height / 2), (width - height / 2, height / 2), (width, 0)]
    bright_vertex, dark_vertex = ((0, 0), (width, height)) if convex else ((width, height), (0, 0))
    pg.draw.polygon(s, pg.Color('white'), [*points, bright_vertex])
    pg.draw.polygon(s, DARK_GRAY, [*points, dark_vertex])
    pg.draw.rect(s, MAIN_GRAY, (indent, indent, width - indent * 2, height - indent * 2), 0)
    return s


class IntValidator:
    def __init__(self, min_val: int, max_val: int, global_min=None):
        """:param min_val: minimal value of valid integer (inclusively).
        :param max_val: maximal value of valid integer (inclusively)."""
        super().__init__()
        self.min_val, self.max_val = min_val, max_val
        self.global_min = global_min if global_min is not None else min_val

    def validate(self, value: str) -> bool:
        """:param value: value to validate.
        :return is_value_valid: True if value is a valid integer (validates by regular expression)
        and belongs to interval [min_val, max_val]."""
        return bool(re.match(INT_REGEX, value)) and self.min_val <= int(value) <= self.max_val

    def update_bounds(self, min_val=None, max_val=None):
        if min_val is not None:
            self.min_val = min_val
            if min_val > self.max_val:
                self.max_val = min_val
        if max_val is not None:
            self.max_val = max(max_val, self.global_min)
            if self.max_val < self.min_val:
                self.min_val = self.max_val
