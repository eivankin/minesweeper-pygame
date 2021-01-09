from sprites import *
from random import choice
from itertools import product

FPS = 60
N = 9  # Default field settings. TODO: make it editable for user
MINES_COUNT = 2
LEFT_INDENT, TOP_INDENT, CELL_SIZE = 15, 94, 30
FIELD_INDENT = 5
INDICATOR_SIZE = 50
COUNTER_WIDTH = 82


class Field(pg.sprite.Group):
    def __init__(self, width, height, left_indent, top_indent,
                 cell_size, indicator, counter, *sprites):
        super().__init__(*sprites)
        self.indicator = indicator
        self.counter = counter
        self.w = width
        self.h = height
        self.left = left_indent
        self.top = top_indent
        self.cell_size = cell_size
        self.field = [[Cell(x, y, cell_size, left_indent, top_indent, self)
                       for y in range(width)] for x in range(height)]
        self.first_move = True
        self.mines = set()
        self.playing = True
        self.last_coords = None
        self.marked = set()

    def init_mines(self, exclude_coords, mines_count=MINES_COUNT):
        coords = set(product(range(self.h), range(self.w)))
        coords.remove(exclude_coords)
        for _ in range(mines_count):
            c = choice(list(coords))
            self.mines.add(c)
            self.field[c[0]][c[1]].set_content('mine')
            for row in self.field[max(0, c[0] - 1):min(self.h, c[0] + 2)]:
                for cell in filter(lambda x: x.content != 'mine',
                                   row[max(0, c[1] - 1):min(self.w, c[1] + 2)]):
                    cell.set_content(cell.content + 1)
            coords.remove(c)
        # DEBUG
        # from pprint import pprint
        # pprint(self.field)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        i = (y - self.top) // self.cell_size
        j = (x - self.left) // self.cell_size
        return (i, j) if 0 <= i < self.h and 0 <= j < self.w else None

    def get_click(self):
        if self.playing and self.last_coords:
            cell_coords = self.last_coords
            i, j = cell_coords
            if self.field[i][j].mark is None:
                if self.first_move:
                    self.init_mines(cell_coords)
                    self.first_move = False
                    pg.time.set_timer(pg.USEREVENT, 1000)
                self.field[i][j].open()
                queue = self._get_queue(i, j)
                while queue:
                    cell = queue.pop(0)
                    cell.open()
                    queue.extend(self._get_queue(cell.x, cell.y))
                lose = cell_coords in self.mines
                win = not lose and self._check_win()
                if win or lose:
                    for i, j in self.mines.union(self.marked):
                        if (i, j) != cell_coords:
                            self.field[i][j].open(False)
                    self.playing = False
                    self.indicator.change_state('win' if win else 'lose')
                    # print('You win!' if win else 'You lose!')
            self.last_coords = None

    def hold(self, mouse_pos):
        if self.playing:
            cell_coords = self.get_cell(mouse_pos)
            if cell_coords:
                i, j = cell_coords
                pressed = pg.mouse.get_pressed(3)
                if pressed[0] and self.field[i][j].mark is None:
                    self.indicator.change_state('move')
                    self.last_coords = cell_coords
                    self.field[i][j].hold()
                elif pressed[2] and (self.counter.get_value() > 0 or self.field[i][j].mark is not None):
                    deltas = {'F': -1, 'Q': 1, None: 0}
                    self.field[i][j].set_mark()
                    self.counter.change_value(deltas[self.field[i][j].mark])
                    if self.field[i][j].mark == 'F':
                        self.marked.add((i, j))
                    elif self.field[i][j].mark is None and (i, j) in self.marked:
                        self.marked.remove((i, j))

    def _get_queue(self, x, y):
        q = []
        if self.field[x][y].content == 0:
            for row in self.field[max(0, x - 1):min(self.h, x + 2)]:
                q.extend(list(filter(
                    lambda c: not c.is_opened and c.mark is None, row[max(0, y - 1):min(self.w, y + 2)]
                )))
        return q

    def _check_win(self):
        return all(cell.is_opened or cell.content == 'mine'
                   for row in self.field for cell in row)


if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()

    screen = pg.display.set_mode((LEFT_INDENT * 2 + CELL_SIZE * N, TOP_INDENT + CELL_SIZE * N + LEFT_INDENT))
    pg.display.set_caption('Minesweeper')

    panel_y = LEFT_INDENT - FIELD_INDENT + (TOP_INDENT - 25) / 2 - INDICATOR_SIZE // 2
    indicator = Indicator(LEFT_INDENT + CELL_SIZE * N / 2 - INDICATOR_SIZE // 2, panel_y, INDICATOR_SIZE)
    mine_counter = Counter(LEFT_INDENT * 2 - FIELD_INDENT, panel_y, COUNTER_WIDTH, INDICATOR_SIZE, MINES_COUNT)
    timer = Counter(N * CELL_SIZE + LEFT_INDENT - FIELD_INDENT * 2 - COUNTER_WIDTH,
                    panel_y, COUNTER_WIDTH, INDICATOR_SIZE)

    panel = pg.sprite.Group(indicator, mine_counter, timer)
    field = Field(N, N, LEFT_INDENT, TOP_INDENT, CELL_SIZE, indicator, mine_counter)

    screen.fill(MAIN_GRAY)
    screen.blit(draw_cell(N * CELL_SIZE + FIELD_INDENT * 2, N * CELL_SIZE + FIELD_INDENT * 2, FIELD_INDENT, False),
                (LEFT_INDENT - FIELD_INDENT, TOP_INDENT - FIELD_INDENT))
    screen.blit(draw_cell(N * CELL_SIZE + FIELD_INDENT * 2, TOP_INDENT - 25, convex=False),
                (LEFT_INDENT - FIELD_INDENT, LEFT_INDENT - FIELD_INDENT))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                field.hold(event.pos)
                indicator.click(event.pos)
            if event.type == pg.MOUSEBUTTONUP:
                field.get_click()
                if indicator.release():
                    timer.set_value(0)
                    pg.time.set_timer(pg.USEREVENT, 0)
                    mine_counter.set_value(MINES_COUNT)
                    field.__init__(N, N, LEFT_INDENT, TOP_INDENT, CELL_SIZE, indicator, mine_counter)
            if event.type == pg.USEREVENT:
                timer.change_value(1)
        panel.update()
        field.draw(screen)
        panel.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
