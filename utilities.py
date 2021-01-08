import os
import pygame as pg

MAIN_GRAY = (191, 191, 191)
DARK_GRAY = (127, 127, 129)


def terminate():
    pg.quit()
    exit()


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
