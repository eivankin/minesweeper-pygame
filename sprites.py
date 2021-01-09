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
        elif content == 'mine':
            self.content = content
            self.content_image = load_image(f'{content}.png')
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
        self.image.fill(DARK_GRAY)
        pg.draw.rect(self.image, MAIN_GRAY, (1, 1, self.rect.w - 2, self.rect.h - 2), 0)

    def open(self, user=True):
        """:param user: is cell opening by user or by program (on game ending)"""

        if not self.is_opened and self.mark is None:
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, pg.Color('red') if user and self.content == 'mine' else MAIN_GRAY,
                         (1, 1, self.rect.w - 2, self.rect.h - 2), 0)
            if self.content_image:
                self.image.blit(self.content_image, (0, 0))
            self.is_opened = True

    def __repr__(self):
        """For debugging"""
        return str(self.content) if self.content != 'mine' else '*'


class Indicator(pg.sprite.Sprite):
    def __init__(self, x, y, size, *groups):
        self.size = size
        self.image = draw_cell(size, size)
        self.rect = pg.Rect(x, y, size, size)
        self.lock_state = False
        self.states = {state: load_image(f'states/{state}.png')
                       for state in ['ok', 'win', 'move', 'lose']}
        self.change_state('ok')
        super().__init__(*groups)
        self.clicked = False

    def change_state(self, state):
        if not self.lock_state:
            try:
                self.image.blit(self.states[state], (4, 4))
                if state == 'lose' or state == 'win':
                    self.lock_state = True
            except KeyError:
                raise KeyError(f'No such state: {state}')

    def click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.lock_state = False
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, MAIN_GRAY,
                         (2, 2, self.rect.w - 4, self.rect.h - 4), 0)
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
        self.value = start_value
        self.image = draw_cell(width, height, 2, False)
        self.rect = pg.Rect(x, y, width, height)
        super().__init__(*groups)
