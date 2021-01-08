from sprites import *

FPS = 60
N = 9  # Default field settings. TODO: make it editable for user
MINES_COUNT = 10
LEFT_INDENT, TOP_INDENT, CELL_SIZE = 10, 70, 20
FIELD_INDENT = 3


class Field(pg.sprite.Group):
    def __init__(self, width, height, left_indent, top_indent, cell_size, *sprites):
        super().__init__(*sprites)
        self.width = width
        self.height = height
        self.left = left_indent
        self.top = top_indent
        self.cell_size = cell_size
        self.field = [[Cell(left_indent + x * cell_size, top_indent + y * cell_size, cell_size, self)
                       for y in range(width)] for x in range(height)]
        self.first_move = True

    def init_mines(self, exclude_coords, mines_count=MINES_COUNT):
        pass

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        i = (y - self.top) // self.cell_size
        j = (x - self.left) // self.cell_size
        return (i, j) if 0 <= i <= self.height and 0 <= j <= self.width else None

    def get_click(self, mouse_pos):
        pass


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
        screen.fill(MAIN_GRAY)
        pg.draw.polygon(screen, DARK_GRAY, [(x1, y0), (x0, y0), (x0, y1)])
        pg.draw.polygon(screen, pg.Color('white'), [(x1, y0), (x1, y1), (x0, y1)])
        field.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
