from utilities import *


class Cell(pg.sprite.Sprite):
    def __init__(self, x, y, cell_size, left_indent, top_indent, *groups):
        super().__init__(*groups)
        self.size = cell_size
        self.x, self.y = x, y
        x, y = left_indent + y * cell_size, top_indent + x * cell_size
        self.content = 0
        self.content_image = None
        self.rect = pg.rect.Rect(x, y, cell_size, cell_size)
        self.image = draw_cell(cell_size, cell_size)
        self.is_opened = False
        self.mark = None

    def set_content(self, content):
        """:param content: string 'mine' or int (count of neighbor mines in range [1, 8])"""

        if type(content) == int and 0 < content < 9:
            self.content = content
            self.content_image = load_image(f'numbers/{content}.png')
        elif content == '*':
            self.content = content
            self.content_image = load_image(f'mine.png')
        else:
            raise ValueError('content must be "mine" or int (count of neighbor mines in range [1, 8])')

    def set_mark(self):
        if not self.is_opened:
            if self.mark is None:
                self.mark = 'F'
            elif self.mark == 'F':
                self.mark = 'Q'
            else:
                self.mark = None
            self.image = draw_cell(self.size, self.size)
            if self.mark is not None:
                self.image.blit(load_image(f'{self.mark}.png'), (0, 0))

    def hold(self):
        if not self.is_opened:
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, MAIN_GRAY, (1, 1, self.rect.w - 2, self.rect.h - 2), 0)

    def open(self, user=True):
        """:param user: is cell opening by user or by program (on game ending)"""
        not_mine_cond = not user and self.content != '*'
        if not self.is_opened and (self.mark is None or not_mine_cond):
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, pg.Color('red') if user and self.content == '*' else MAIN_GRAY,
                         (1, 1, self.rect.w - 2, self.rect.h - 2), 0)
            if not_mine_cond:
                self.image.blit(load_image('not-mine.png'), (0, 0))
            elif self.content_image:
                self.image.blit(self.content_image, (0, 0))
            self.is_opened = True

    def __repr__(self):
        """For debugging"""
        if self.content != 0:
            return str(self.content) if self.content else ''
        return str(self.mark)


class Indicator(pg.sprite.Sprite):
    def __init__(self, x, y, size, *groups):
        self.size = size
        self.image = draw_cell(size, size)
        self.rect = pg.Rect(x, y, size, size)
        self.lock_state = False
        self.states = {state: load_image(f'states/{state}.png')
                       for state in ['ok', 'win', 'move', 'lose']}
        self.state_size = self.states['ok'].get_rect().w
        self.change_state('ok')
        super().__init__(*groups)
        self.clicked = False

    def change_state(self, state):
        if not self.lock_state:
            try:
                indent = (self.rect.w - self.state_size) / 2
                self.image.blit(self.states[state], (indent, indent))
                if state == 'lose' or state == 'win':
                    self.lock_state = True
            except KeyError:
                raise KeyError(f'No such state: {state}')

    def click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.lock_state = False
            self.image = draw_cell(self.size, self.size, convex=False)
            self.change_state('ok')
            self.clicked = True

    def release(self):
        res = False
        if self.clicked:
            res = True
            self.clicked = False
            self.image = draw_cell(self.size, self.size)
        if not self.lock_state:
            self.change_state('ok')
        return res


class Counter(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, start_value=0, *groups):
        self.__value = start_value
        self.changed = True
        self.image = draw_cell(width, height, 2, False)
        self.rect = pg.Rect(x, y, width, height)
        self.numbers = {str(num): load_image(f'seven segment/{num}.png') for num in range(10)}
        super().__init__(*groups)

    def change_value(self, d):
        self.__value = min(self.__value + d, 999)  # Prevent overflow
        self.changed = True

    def set_value(self, value):
        self.__value = min(value, 999)  # Prevent overflow
        self.changed = True

    def get_value(self):
        return self.__value

    def update(self, *args):
        if self.changed:
            for i, n in enumerate(str(self.__value)[-3:].rjust(3, '0')):
                self.image.blit(self.numbers[n], (2 + i * 26, 2))
            self.changed = False
