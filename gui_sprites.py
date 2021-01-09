from utilities import *


class TextInput(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, font, value_validator=None, *groups):
        indent = 1
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.image = pg.Surface((width, height))
        self.image.fill('black')
        pg.draw.rect(self.image, 'white', (indent, indent, width - indent * 2, height - indent * 2))
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
        pg.draw.circle(self.image, 'black', (radius, radius), radius, 1)
        pg.draw.circle(self.image, 'black', (radius, radius), radius - 3)
        self.checked = False

    def update(self, *args):
        pass


class Button(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, label, font: pg.font.Font, *groups):
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.image = draw_cell(width, height)
        text = font.render(label, True, (0, 0, 0))
        x, y = width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2
        self.image.blit(text, (x, y))


class Label(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, text, font: pg.font.Font, *groups):
        super().__init__(*groups)
        text_surface = font.render(text, True, (0, 0, 0))
        w, h = text_surface.get_width(), text_surface.get_height()
        self.image = pg.Surface((w, h))
        self.image.fill(MAIN_GRAY)
        self.image.blit(text_surface, (0, 0))
        self.rect = pg.Rect(left_x, top_y, w, h)
