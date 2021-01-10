from utilities import *

UPDATEBOUNDSEVENT = pg.USEREVENT + 1
TOGGLECURSOREVENT = pg.USEREVENT + 2


def handle_change():
    pg.event.post(pg.event.Event(UPDATEBOUNDSEVENT))


class TextInput(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, font: pg.font.Font, value_validator=None,
                 *groups, on_value_change=lambda: None):
        self.value_change_handler = on_value_change
        self.indent = 1
        self.font = font
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.image = pg.Surface((width, height))
        self.image.fill('black')
        pg.draw.rect(self.image, 'white',
                     (self.indent, self.indent, width - self.indent * 2, height - self.indent * 2))
        self.validator = value_validator
        self.__value = ''
        self.active = False
        self.display_cursor = False

    def set_value(self, value):
        if self.validator is None or self.validator.validate(value):
            self.__value = value
            self.value_change_handler()

    def get_value(self):
        if type(self.validator) == IntValidator:
            return int(self.__value) if self.__value != '' else 0
        return self.__value

    def update(self, *args):
        if args:
            if self.active and args[0].type == TOGGLECURSOREVENT:
                self.display_cursor = not self.display_cursor
            if args[0].type == pg.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(*args[0].pos)
            if args[0].type == pg.KEYDOWN and self.active:
                self.set_value(self.__value + args[0].unicode)
            if args[0].type == pg.KEYDOWN and args[0].key == pg.K_BACKSPACE and self.active:
                self.__value = self.__value[:-1]
        text = (self.__value + '|') if self.display_cursor and self.active else self.__value
        pg.draw.rect(self.image, 'white',
                     (self.indent, self.indent, self.rect.w - self.indent * 2, self.rect.h - self.indent * 2))
        indent = (self.rect.h - self.font.get_height()) // 2 - 1
        self.image.blit(self.font.render(text, True, (0, 0, 0)), (indent, indent))


class RadioButton(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, radius, *groups, checked=False):
        super().__init__(*groups)
        self.r = radius
        self.rect = pg.Rect(left_x, top_y, radius * 2, radius * 2)
        self.image = pg.Surface((radius * 2, radius * 2))
        self.checked = checked
        self._draw_current_state()

    def _draw_current_state(self):
        self.image.fill(MAIN_GRAY)
        pg.draw.circle(self.image, 'black', (self.r, self.r), self.r, 1)
        if self.checked:
            pg.draw.circle(self.image, 'black', (self.r, self.r), self.r - 3)

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(*args[0].pos):
            for button in self.groups()[0].sprites():
                button.checked = False
            self.checked = True
        self._draw_current_state()


class Button(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, label, font: pg.font.Font, *groups, on_click=lambda: None):
        super().__init__(*groups)
        self.font = font
        self.click_handler = on_click
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.clicked = False
        self.width, self.height, self.label = width, height, label
        self._draw_current_state()

    def _draw_current_state(self):
        if self.clicked:
            self.image = draw_cell(self.width, self.height, convex=False)
        else:
            self.image = draw_cell(self.width, self.height)
        text = self.font.render(self.label, True, (0, 0, 0))
        x, y = self.width // 2 - text.get_width() // 2, self.height // 2 - text.get_height() // 2
        self.image.blit(text, (x, y))

    def update(self, *args):
        if args:
            if args[0].type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(*args[0].pos):
                self.clicked = True
            elif args[0].type == pg.MOUSEBUTTONUP and self.clicked:
                self.clicked = False
                self.click_handler()
            self._draw_current_state()


class Label(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, text, font: pg.font.Font, *groups):
        super().__init__(*groups)
        text_surface = font.render(text, True, (0, 0, 0))
        w, h = text_surface.get_width(), text_surface.get_height()
        self.image = pg.Surface((w, h))
        self.image.fill(MAIN_GRAY)
        self.image.blit(text_surface, (0, 0))
        self.rect = pg.Rect(left_x, top_y, w, h)
