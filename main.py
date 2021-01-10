from sprites import *
from gui_sprites import *
from random import choice
from itertools import product

FPS = 60
LEFT_INDENT, TOP_INDENT, CELL_SIZE = 15, 94, 30
FIELD_INDENT = 5
INDICATOR_SIZE = 50
COUNTER_WIDTH = 82

# global variables (sorry for using it)
current_screen = 'main'
mines_count = 10
current_preset = PRESETS['newbie']


def change_screen(to):
    global current_screen
    if to == 'settings':
        pg.time.set_timer(TOGGLECURSOREVENT, 500)
    if to == 'main' and current_screen == 'settings':
        preset_name = get_preset_name()
        # DEBUG
        print(PRESETS.get(preset_name, {'size': (width_input.get_value(), height_input.get_value()),
                                        'mines': mines_count_input.get_value()}))
    if to in ('main', 'settings', 'help'):
        current_screen = to


def init_screens(size, mines):
    global screen, screens, field, indicator, timer, panel, mine_counter, settings_layout, \
        mines_count_input, height_input, width_input, mines_count

    field_w, field_h = size
    mines_count = mines
    w, h = LEFT_INDENT * 2 + CELL_SIZE * field_w, TOP_INDENT + CELL_SIZE * field_h + LEFT_INDENT
    screens = {name: pg.Surface((w, h)) for name in ['main', 'settings', 'help']}
    screen = pg.display.set_mode((w, h))
    pg.display.set_caption('Minesweeper')

    panel_y = LEFT_INDENT - FIELD_INDENT + (TOP_INDENT - 25) / 2 - INDICATOR_SIZE // 2
    indicator = Indicator(LEFT_INDENT + CELL_SIZE * field_w / 2 - INDICATOR_SIZE // 2, panel_y, INDICATOR_SIZE)
    mine_counter = Counter(LEFT_INDENT * 2 - FIELD_INDENT, panel_y, COUNTER_WIDTH, INDICATOR_SIZE, mines_count)
    timer = Counter(field_w * CELL_SIZE + LEFT_INDENT - FIELD_INDENT * 2 - COUNTER_WIDTH,
                    panel_y, COUNTER_WIDTH, INDICATOR_SIZE)

    panel = pg.sprite.Group(indicator, mine_counter, timer)
    field = Field(field_w, field_h, LEFT_INDENT, TOP_INDENT, CELL_SIZE, indicator, mine_counter)

    screens['main'].fill(MAIN_GRAY)
    screens['main'].blit(
        draw_cell(field_w * CELL_SIZE + FIELD_INDENT * 2, field_h * CELL_SIZE + FIELD_INDENT * 2, FIELD_INDENT, False),
        (LEFT_INDENT - FIELD_INDENT, TOP_INDENT - FIELD_INDENT))
    screens['main'].blit(draw_cell(field_w * CELL_SIZE + FIELD_INDENT * 2, TOP_INDENT - 25, convex=False),
                         (LEFT_INDENT - FIELD_INDENT, LEFT_INDENT - FIELD_INDENT))

    font = pg.font.Font('data/lcd.ttf', 20)
    settings_layout = pg.sprite.Group()
    r = 8
    x = FIELD_INDENT + 2 * r + 5
    header = Label(LEFT_INDENT, LEFT_INDENT, 'Difficulty', pg.font.Font('data/lcd.ttf', 24), settings_layout)
    y = header.rect.y + header.rect.h + 10

    for name, preset in PRESETS.items():
        a, b, mines = *preset['size'], preset['mines']
        button = RadioButton(FIELD_INDENT, y, r, settings_layout, checked=(name == 'newbie'))
        label = Label(x, y, f'{name.title()} ({a}×{b}, {mines} mines)', font, settings_layout)
        y += r * 2 + 10

    custom_button = RadioButton(FIELD_INDENT, y, r, settings_layout)
    custom_label = Label(x, y, 'Custom', font, settings_layout)
    y += r * 2 + 10

    sep, shift = 70, 10
    width_label = Label(x, y + shift, 'Width:', font, settings_layout)
    width_input = TextInput(x + sep, y, 60, 30, font, IntValidator(1, 30),
                            settings_layout, on_value_change=handle_change)
    height_label = Label(x, y + 40 + shift, 'Height:', font, settings_layout)
    height_input = TextInput(x + sep, y + 40, 60, 30, font, IntValidator(1, 30),
                             settings_layout, on_value_change=handle_change)
    mines_count_label = Label(x, y + 80 + shift, 'Mines:', font, settings_layout)
    mines_count_input = TextInput(x + sep, y + 80, 60, 30, font, IntValidator(1, 99), settings_layout)

    ok_button = Button(w - 100, y + 150, 75, 30, 'OK', font, settings_layout,
                       on_click=lambda: change_screen('main'))
    screens['settings'].fill(MAIN_GRAY)


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

    def init_mines(self, exclude_coords, mines_count=mines_count):
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
                    pg.time.set_timer(pg.USEREVENT, 0)
                    queue = self.marked if win else self.mines.union(self.marked)
                    for i, j in queue:
                        if (i, j) != cell_coords:
                            self.field[i][j].open(False)
                    if win:
                        for i, j in self.mines:
                            self.field[i][j].mark = None
                            self.field[i][j].set_mark()
                    self.playing = False
                    self.indicator.change_state('win' if win else 'lose')
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
    (screen, screens, field, indicator, timer, panel, mine_counter, settings_layout,
     mines_count_input, height_input, width_input) = [None] * 11
    init_screens(**current_preset)
    change_screen('settings')
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if current_screen == 'main':
                if event.type == pg.MOUSEBUTTONDOWN:
                    field.hold(event.pos)
                    indicator.click(event.pos)
                if event.type == pg.MOUSEBUTTONUP:
                    field.get_click()
                    if indicator.release():
                        timer.set_value(0)
                        pg.time.set_timer(pg.USEREVENT, 0)
                        mine_counter.set_value(mines_count)
                        field.__init__(*current_preset['size'], LEFT_INDENT, TOP_INDENT,
                                       CELL_SIZE, indicator, mine_counter)
                if event.type == pg.USEREVENT:
                    timer.change_value(1)
            elif current_screen == 'settings':
                if event.type == UPDATEBOUNDSEVENT:
                    mines_count_input.validator.update_bounds(
                        max_val=height_input.get_value() * width_input.get_value() - 1
                    )
                settings_layout.update(event)
        panel.update()
        field.draw(screens['main'])
        panel.draw(screens['main'])
        settings_layout.draw(screens['settings'])
        screen.blit(screens[current_screen], (0, 0))
        pg.display.flip()
        clock.tick(FPS)
