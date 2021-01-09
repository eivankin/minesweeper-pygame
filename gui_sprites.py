from utilities import *


class TextInput(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, value_validator=None, *groups):
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.validator = value_validator
        self.__value = None
        self.active = False

    def set_value(self, value):
        if self.validator is None or self.validator.validate(value):
            self.__value = value

    def update(self, *args):
        pass


class RadioButton(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, radius, *groups):
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, radius * 2, radius * 2)
        self.image = pg.Surface((radius * 2, radius * 2))
        self.image.fill(MAIN_GRAY)
        pg.draw.circle(self.image, 'black', (left_x + radius, top_y + radius), radius)
        self.checked = False

    def update(self, *args):
        pass
