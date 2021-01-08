from utilities import *


class Cell(pg.sprite.Sprite):
    CELL_CONTENT = {  # TODO: replace with images
        '*': None,  # mine
        '?': None,  # question mark
        'F': None  # flag mark
    }

    def __init__(self, x, y, cell_size, *groups):
        super().__init__(*groups)
        self.content = None
        self.rect = pg.rect.Rect(x, y, cell_size, cell_size)
        s = pg.Surface((cell_size, cell_size))
        pg.draw.polygon(s, pg.Color('white'), [(cell_size, 0), (0, 0), (0, cell_size)])
        pg.draw.polygon(s, DARK_GRAY, [(cell_size, 0), (cell_size, cell_size), (0, cell_size)])
        pg.draw.rect(s, MAIN_GRAY, (2, 2, cell_size - 4, cell_size - 4), 0)
        self.image = s
        self.is_opened = False

    def set_content(self, content):
        """:param content: any key from Cell.CELL_CONTENT dictionary or int (count of neighbor mines)"""
        if type(content) == int:
            self.content = content
        else:
            try:
                self.content = self.CELL_CONTENT[content]
            except KeyError:
                raise KeyError('no such content for cell')

    def click(self):
        if not self.is_opened:
            self.image.fill(DARK_GRAY)
            pg.draw.rect(self.image, MAIN_GRAY, (1, 1, self.rect.w - 2, self.rect.h - 2), 0)
            if self.content:
                self.image.blit(self.content, (0, 0))
            self.is_opened = True


class Indicator(pg.sprite.Sprite):
    pass


class Counter(pg.sprite.Sprite):
    pass
