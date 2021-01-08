from sprites import *
from random import choice
from itertools import product

FPS = 60
N = 9  # Default field settings. TODO: make it editable for user
MINES_COUNT = 10
LEFT_INDENT, TOP_INDENT, CELL_SIZE = 15, 70, 30
FIELD_INDENT = 5


class Field(pg.sprite.Group):
    def __init__(self, width, height, left_indent, top_indent, cell_size, *sprites):
        super().__init__(*sprites)
        self.w = width
        self.h = height
        self.left = left_indent
        self.top = top_indent
        self.cell_size = cell_size
        self.field = [[Cell(left_indent + y * cell_size, top_indent + x * cell_size, cell_size, self)
                       for y in range(width)] for x in range(height)]
        self.first_move = True
        self.mines = {}
        self.playing = True

    def init_mines(self, exclude_coords, mines_count=MINES_COUNT):
        coords = set(product(range(self.h), range(self.w)))
        coords.remove(exclude_coords)
        for _ in range(mines_count):
            c = choice(list(coords))
            self.mines[c] = True
            self.field[c[0]][c[1]].set_content('mine')
            for row in self.field[max(0, c[0] - 1):min(self.h, c[0] + 2)]:
                for cell in filter(lambda x: x.content != 'mine',
                                   row[max(0, c[1] - 1):min(self.w, c[1] + 2)]):
                    cell.set_content(cell.content + 1)
            coords.remove(c)
        # # DEBUG
        # from pprint import pprint
        # pprint(self.field)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        i = (y - self.top) // self.cell_size
        j = (x - self.left) // self.cell_size
        return (i, j) if 0 <= i <= self.h and 0 <= j <= self.w else None

    def get_click(self, mouse_pos):
        if self.playing:
            cell_coords = self.get_cell(mouse_pos)
            if cell_coords:
                if self.first_move:
                    self.init_mines(cell_coords)
                    self.first_move = False
                i, j = cell_coords
                self.field[i][j].open()
                if cell_coords in self.mines:
                    for i, j in self.mines:
                        if (i, j) != cell_coords:
                            self.field[i][j].open(False)
                    self.playing = False


if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()
    field = Field(N, N, LEFT_INDENT, TOP_INDENT, CELL_SIZE)
    screen = pg.display.set_mode((LEFT_INDENT * 2 + CELL_SIZE * N, TOP_INDENT + CELL_SIZE * N + LEFT_INDENT))
    x0, y0 = LEFT_INDENT - FIELD_INDENT, TOP_INDENT - FIELD_INDENT
    x1, y1 = LEFT_INDENT + N * CELL_SIZE + FIELD_INDENT, TOP_INDENT + N * CELL_SIZE + FIELD_INDENT
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                field.get_click(event.pos)
        screen.fill(MAIN_GRAY)
        pg.draw.polygon(screen, DARK_GRAY, [(x1, y0), (x0, y0), (x0, y1)])
        pg.draw.polygon(screen, pg.Color('white'), [(x1, y0), (x1, y1), (x0, y1)])
        field.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
