from sprites import *
from gui_sprites import *
from random import choice
from itertools import product

FPS = 60
LEFT_INDENT, TOP_INDENT, CELL_SIZE = 15, 94, 30
FIELD_INDENT = 5
INDICATOR_SIZE = 50
COUNTER_WIDTH = 82
MENUBAR_HEIGHT = 20

# global variables (sorry for using it)
current_screen = 'main'


def change_screen(to):
    global current_screen
    if to == 'settings':
        pg.time.set_timer(TOGGLECURSOREVENT, 500)
    if to == 'main' and current_screen == 'settings':
        preset_name = get_preset_name()
        current_preset = PRESETS.get(preset_name, {'size': (width_input.get_value(), height_input.get_value()),
                                                   'mines': mines_count_input.get_value()})
        init_screens(**current_preset)
    if to in ('main', 'settings', 'help'):
        current_screen = to


def init_screens(size, mines):
    global screen, screens, field, indicator, timer, panel, mine_counter, settings_layout, \
        mines_count_input, height_input, width_input, menu_bar, help_layout
    field_w, field_h = size
    font = pg.font.Font('data/lcd.ttf', 20)
    w, h = LEFT_INDENT * 2 + CELL_SIZE * field_w, TOP_INDENT + CELL_SIZE * field_h + LEFT_INDENT + MENUBAR_HEIGHT
    screens = {name: pg.Surface((w, h)) for name in ['main', 'settings', 'help']}
    screen = pg.display.set_mode((w, h))
    pg.display.set_caption('Minesweeper')

    panel_y = LEFT_INDENT - FIELD_INDENT + (TOP_INDENT - 25) / 2 - INDICATOR_SIZE // 2 + MENUBAR_HEIGHT
    indicator = Indicator(LEFT_INDENT + CELL_SIZE * field_w / 2 - INDICATOR_SIZE // 2, panel_y, INDICATOR_SIZE)
    mine_counter = Counter(LEFT_INDENT * 2 - FIELD_INDENT, panel_y, COUNTER_WIDTH, INDICATOR_SIZE, mines)
    timer = Counter(field_w * CELL_SIZE + LEFT_INDENT - FIELD_INDENT * 2 - COUNTER_WIDTH,
                    panel_y, COUNTER_WIDTH, INDICATOR_SIZE)

    panel = pg.sprite.Group(indicator, mine_counter, timer)
    field = Field(field_w, field_h, LEFT_INDENT, TOP_INDENT + MENUBAR_HEIGHT,
                  CELL_SIZE, indicator, mine_counter, mines)

    button_font = pg.font.Font('data/lcd.ttf', 16)
    settings_button = MenuButton(0, 0, MENUBAR_HEIGHT, 'Settings', button_font,
                                 on_click=lambda: change_screen('settings'))
    help_button = MenuButton(settings_button.rect.w, 0, MENUBAR_HEIGHT, 'Help', button_font,
                             on_click=lambda: change_screen('help'))
    menu_bar = pg.sprite.Group(settings_button, help_button)

    screens['main'].fill(MAIN_GRAY)
    screens['main'].blit(
        draw_cell(field_w * CELL_SIZE + FIELD_INDENT * 2, field_h * CELL_SIZE + FIELD_INDENT * 2, FIELD_INDENT, False),
        (LEFT_INDENT - FIELD_INDENT, TOP_INDENT - FIELD_INDENT + MENUBAR_HEIGHT))
    screens['main'].blit(draw_cell(field_w * CELL_SIZE + FIELD_INDENT * 2, TOP_INDENT - 25, convex=False),
                         (LEFT_INDENT - FIELD_INDENT, LEFT_INDENT - FIELD_INDENT + MENUBAR_HEIGHT))
    pg.draw.rect(screens['main'], 'white', (0, 0, w, MENUBAR_HEIGHT))
    if settings_layout is not None:
        values = [i.get_value(str) for i in settings_layout if type(i) == TextInput]
    else:
        values = [''] * 3
    settings_layout = pg.sprite.Group()
    r = 8
    x0 = w / 2 - 150
    y0 = h / 2 - 200
    x = x0 + FIELD_INDENT + 2 * r + 5
    header_font = pg.font.Font('data/lcd.ttf', 24)
    header = Label(x0 + LEFT_INDENT, y0 + LEFT_INDENT, 'Difficulty', header_font, settings_layout)
    y = header.rect.y + header.rect.h + 10
    if len(radio_group) > 0:
        checked_buttons = [b.checked for b in radio_group.sprites()]
    else:
        checked_buttons = [True] + [False] * len(PRESETS)
    radio_group.empty()
    for (name, preset), checked in zip(PRESETS.items(), checked_buttons):
        button = RadioButton(x0 + FIELD_INDENT, y, r, settings_layout, checked=checked)
        Label(x, y, f'{name.title()} ({"×".join(map(str, preset["size"]))}, {preset["mines"]} mines)',
              font, settings_layout, assigned_item=button)
        y += r * 2 + 10

    button = RadioButton(x0 + FIELD_INDENT, y, r, settings_layout, checked=checked_buttons[-1])
    Label(x, y, 'Custom', font, settings_layout, assigned_item=button)
    y += r * 2 + 10

    sep, shift = 70, 10
    width_input = TextInput(x + sep, y, 60, 30, font, IntValidator(9, 24),
                            settings_layout, on_value_change=handle_change)
    width_input.set_value(values[0])
    Label(x, y + shift, 'Width:', font, settings_layout, assigned_item=width_input)
    height_input = TextInput(x + sep, y + 40, 60, 30, font, IntValidator(9, 24),
                             settings_layout, on_value_change=handle_change)
    height_input.set_value(values[1])
    Label(x, y + 40 + shift, 'Height:', font, settings_layout, assigned_item=height_input)
    mines_count_input = TextInput(x + sep, y + 80, 60, 30, font, IntValidator(10, 99), settings_layout)
    mines_count_input.set_value(values[2])
    Label(x, y + 80 + shift, 'Mines:', font, settings_layout, assigned_item=mines_count_input)

    Button(x0 + 200, y + 150, 75, 30, 'OK', font, settings_layout,
           on_click=lambda: change_screen('main'))
    screens['settings'].fill(MAIN_GRAY)

    screens['help'].fill(MAIN_GRAY)
    help_layout = pg.sprite.Group()
    help_header = Label(x0 + LEFT_INDENT, y0 + LEFT_INDENT, 'Help', header_font, help_layout)
    y = y0 + LEFT_INDENT + help_header.rect.h + 15
    with open('docs/help.txt') as f:
        for line in f.read().split('\n'):
            label = Label(x0 + LEFT_INDENT, y, line, font, help_layout)
            y += label.rect.h + 5
    y += 30
    little_font = pg.font.Font('data/lcd.ttf', 16)
    Label(x0 + LEFT_INDENT, y, '© dQw4w9WgXcQ Games, 2021', little_font, help_layout)
    y += 20
    Label(x0 + LEFT_INDENT, y, 'Original game made by Microsoft', little_font, help_layout)
    Button(w - x0 - 150 - LEFT_INDENT, y0 + LEFT_INDENT - FIELD_INDENT, 150, 30, 'Back to game →', font,
           help_layout, on_click=lambda: change_screen('main'))


class Field(pg.sprite.Group):
    def __init__(self, width, height, left_indent, top_indent,
                 cell_size, state_indicator, counter, mines_count, *sprites):
        super().__init__(*sprites)
        self.mines_count = mines_count
        self.indicator = state_indicator
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
        self.opened = [[False] * width for _ in range(height)]

    def init_mines(self, exclude_coords):
        coords = set(product(range(self.h), range(self.w)))
        coords.remove(exclude_coords)
        for _ in range(self.mines_count):
            c = choice(list(coords))
            self.mines.add(c)
            self.field[c[0]][c[1]].set_content('*')
            for row in self.field[max(0, c[0] - 1):min(self.h, c[0] + 2)]:
                for cell in filter(lambda x: x.content != '*',
                                   row[max(0, c[1] - 1):min(self.w, c[1] + 2)]):
                    cell.set_content(cell.content + 1)
            coords.remove(c)

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
                self.opened[i][j] = True
                queue = self._get_queue(i, j)
                while queue:
                    x, y = queue.pop(0)
                    self.field[x][y].open()
                    queue.extend(self._get_queue(x, y))
                lose = self.field[i][j].content == '*'
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
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                nx, ny = max(min(x + dx, self.h - 1), 0), max(min(y + dy, self.w - 1), 0)
                if not self.opened[nx][ny]:
                    q.append((nx, ny))
                    self.opened[nx][ny] = True
        return q

    def _check_win(self):
        return all(cell.is_opened or cell.content == '*'
                   for row in self.field for cell in row)


if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()
    (screen, screens, field, indicator, timer, panel, mine_counter, settings_layout,
     mines_count_input, height_input, width_input, menu_bar, help_layout) = [None] * 13
    init_screens(**PRESETS[list(PRESETS.keys())[0]])
    # change_screen('settings')
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
                        mine_counter.set_value(field.mines_count)
                        field.__init__(field.w, field.h, field.left, field.top,
                                       field.cell_size, indicator, mine_counter, field.mines_count)
                if event.type == pg.USEREVENT:
                    timer.change_value(1)
                menu_bar.update(event)
            elif current_screen == 'settings':
                if event.type == UPDATEBOUNDSEVENT:
                    mines_count_input.validator.update_bounds(
                        max_val=height_input.get_value() * width_input.get_value() - 1
                    )
                settings_layout.update(event)
            else:
                help_layout.update(event)
        panel.update()
        field.draw(screens['main'])
        panel.draw(screens['main'])
        menu_bar.draw(screens['main'])
        settings_layout.draw(screens['settings'])
        help_layout.draw(screens['help'])
        screen.blit(screens[current_screen], (0, 0))
        pg.display.flip()
        clock.tick(FPS)
