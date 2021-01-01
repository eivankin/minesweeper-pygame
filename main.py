from sprites import *

FPS = 60


class Field:
    def __init__(self, width: int, height: int, left: int, top: int, cell_size: int):
        self.width = width
        self.height = height
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.field = [[Cell(x, y, cell_size) for y in range(width)] for x in range(height)]
        self.first_move = True

    def init_mines(self, exclude_coords: tuple, mines_count: int):
        pass

    def get_cell(self, mouse_pos: tuple):
        x, y = mouse_pos
        i = (y - self.top) // self.cell_size
        j = (x - self.left) // self.cell_size
        return (i, j) if 0 <= i <= self.height and 0 <= j <= self.width else None

    def get_click(self, mouse_pos):
        pass


if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()
    field = Field(10, 10, 30, 30, 20)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
        pg.display.flip()
        clock.tick(FPS)
