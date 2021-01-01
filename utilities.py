import os
import pygame as pg


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
