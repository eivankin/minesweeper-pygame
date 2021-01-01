from utilities import *


class Cell(pg.sprite.Sprite):
    CELL_CONTENT = {  # TODO: replace with images
        '*': load_image(''),  # mine
        '?': load_image(''),  # question mark
        'F': load_image('')  # flag mark
    }

    def __init__(self, x: int, y: int, cell_size: int, *groups):
        super().__init__(*groups)
        self.content = None

    def set_content(self, content):
        """:param content: any key from Cell.CELL_CONTENT dictionary or int (count of neighbor mines)"""
        if type(content) == int:
            self.content = content
        else:
            try:
                self.content = self.CELL_CONTENT[content]
            except KeyError:
                raise KeyError('no such content for cell')


class Indicator(pg.sprite.Sprite):
    pass


class Counter(pg.sprite.Sprite):
    pass
