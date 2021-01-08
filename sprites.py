from utilities import *


class Cell(pg.sprite.Sprite):
    def __init__(self, x, y, cell_size, left_indent, top_indent, *groups):
        super().__init__(*groups)
        self.x, self.y = x, y
        x, y = left_indent + y * cell_size, top_indent + x * cell_size
        self.content = 0
        self.content_image = None
        self.rect = pg.rect.Rect(x, y, cell_size, cell_size)
        self.image = draw_cell(cell_size, cell_size)
        self.is_opened = False

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

    def open(self, user=True):
        """:param user: is cell opening by user or by program (on game ending)"""

        if not self.is_opened:
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
    pass


class Counter(pg.sprite.Sprite):
    pass
