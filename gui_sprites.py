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
        self.__value = value
        self.value_change_handler()

    def is_valid(self):
        return self.validator is None or self.validator.validate(self.__value)

    def get_value(self):
        if type(self.validator) == IntValidator:
            return int(self.__value) if self.__value != '' and re.match(INT_REGEX, self.__value) else 0
        return self.__value

    def update(self, *args):
        if args:
            if self.active and args[0].type == TOGGLECURSOREVENT:
                self.display_cursor = not self.display_cursor
            if args[0].type == pg.MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(*args[0].pos)
                if self.active:
                    radio_group.sprites()[-1].set_checked()
            if args[0].type == pg.KEYDOWN and self.active:
                self.set_value(self.__value + args[0].unicode)
            if args[0].type == pg.KEYDOWN and args[0].key == pg.K_BACKSPACE and self.active:
                self.__value = self.__value[:-1]
        text = (self.__value + '|') if self.display_cursor and self.active else self.__value
        pg.draw.rect(self.image, 'white',
                     (self.indent, self.indent, self.rect.w - self.indent * 2, self.rect.h - self.indent * 2))
        indent = (self.rect.h - self.font.get_height()) // 2 - 1
        self.image.blit(self.font.render(text, True, (0, 0, 0)), (indent, indent))


class AbstractButton(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, width, height, *groups):
        super().__init__(*groups)
        self.rect = pg.Rect(left_x, top_y, width, height)
        self.image = pg.Surface((width, height))

    def _draw_current_state(self):
        pass

    def update(self, *args):
        self._draw_current_state()


class RadioButton(AbstractButton):
    def __init__(self, left_x, top_y, radius, *groups, checked=False):
        super().__init__(left_x, top_y, radius * 2, radius * 2, radio_group, *groups)
        self.r = radius
        self.checked = checked
        self._draw_current_state()

    def _draw_current_state(self):
        self.image.fill(MAIN_GRAY)
        pg.draw.circle(self.image, 'black', (self.r, self.r), self.r, 1)
        if self.checked:
            pg.draw.circle(self.image, 'black', (self.r, self.r), self.r - 3)

    def set_checked(self):
        for button in self.groups()[0].sprites():
            button.checked = False
        self.checked = True

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(*args[0].pos):
            self.set_checked()
        super().update()


class Button(AbstractButton):
    def __init__(self, left_x, top_y, width, height, label, font: pg.font.Font, *groups, on_click=lambda: None):
        super().__init__(left_x, top_y, width, height, *groups)
        self.font = font
        self.click_handler = on_click
        self.clicked = False
        self.enabled = True
        self.width, self.height, self.label = width, height, label
        self._draw_current_state()

    def _draw_current_state(self):
        text_color = (0, 0, 0)
        if self.clicked:
            self.image = draw_cell(self.width, self.height, convex=False)
        elif self.enabled:
            self.image = draw_cell(self.width, self.height)
        else:
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, MAIN_GRAY, (2, 2, self.rect.w - 3, self.rect.h - 3))
            text_color = DARK_GRAY
        text = self.font.render(self.label, True, text_color)
        x, y = self.width // 2 - text.get_width() // 2, self.height // 2 - text.get_height() // 2
        self.image.blit(text, (x, y))

    def update(self, *args):
        if args:
            if args[0].type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(*args[0].pos) and self.enabled:
                self.clicked = True
            elif args[0].type == pg.MOUSEBUTTONUP and self.clicked:
                self.clicked = False
                self.click_handler()
        if get_preset_name() == 'custom':
            for element in self.groups()[0].sprites():
                if type(element) == TextInput and not element.is_valid():
                    self.enabled = False
                    break
            else:
                self.enabled = True
        else:
            self.enabled = True
        super().update()


class Label(pg.sprite.Sprite):
    def __init__(self, left_x, top_y, text, font: pg.font.Font, *groups, assigned_item=None):
        super().__init__(*groups)
        self.assigned_item = assigned_item
        text_surface = font.render(text, True, (0, 0, 0))
        w, h = text_surface.get_width(), text_surface.get_height()
        self.image = pg.Surface((w, h))
        self.image.fill(MAIN_GRAY)
        self.image.blit(text_surface, (0, 0))
        self.rect = pg.Rect(left_x, top_y, w, h)

    def update(self, *args):
        if args and args[0].type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos) and \
                self.assigned_item is not None:
            self.assigned_item.update(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=self.assigned_item.rect.topleft))


class MenuButton(AbstractButton):
    def __init__(self, left_x, top_y, height, label, font: pg.font.Font, *groups, on_click=lambda: None):
        super().__init__(left_x, top_y, font.render(label, True, 0).get_width() + 10, height, *groups)
        self.hovered = False
        self.clicked = False
        self.font = font
        self.label = label
        self.click_handler = on_click

    def _draw_current_state(self):
        indent = (self.rect.h - self.font.get_height()) // 2
        self.image.fill('#cce8ff' if self.clicked else ('#e5f3ff' if self.hovered else 'white'))
        self.image.blit(self.font.render(self.label, True, (0, 0, 0)), (5, indent))

    def update(self, *args):
        self.hovered = self.rect.collidepoint(pg.mouse.get_pos())
        if args and args[0].type == pg.MOUSEBUTTONUP and self.clicked:
            self.click_handler()
        self.clicked = args and args[0].type == pg.MOUSEBUTTONDOWN and self.hovered
        super().update()
