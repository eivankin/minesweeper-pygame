from random import choice
from itertools import product
from dataclasses import dataclass
from typing import Optional

import pygame as pg

from sprites.game_elements import Cell, Counter, Indicator
from sprites.gui_sprites import Label, TextInput, RadioButton, Button, MenuButton, RADIO_GROUP
from misc.components import GamePreset, LayoutPreset, Screens, GameStates
from misc.constants import TOGGLECURSOREVENT, MAIN_GRAY
from misc.util import draw_cell, handle_change, get_preset_name
from misc.input_validators import IntValidator


class Field(pg.sprite.Group):
    def __init__(self, width: int, height: int, left_indent: int, top_indent: int,
                 cell_size: int, state_indicator: Indicator, counter: Counter, mines_count: int,
                 *sprites):
        super().__init__(*sprites)
        self.mines_count = mines_count
        self.indicator = state_indicator
        self.mine_counter = counter
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
                    self.indicator.change_state(GameStates.WIN if win else GameStates.LOSE)
            self.last_coords = None

    def hold(self, mouse_pos):
        if self.playing:
            cell_coords = self.get_cell(mouse_pos)
            if cell_coords:
                i, j = cell_coords
                pressed = pg.mouse.get_pressed(3)
                if pressed[0] and self.field[i][j].mark is None:
                    self.indicator.change_state(GameStates.MOVE)
                    self.last_coords = cell_coords
                    self.field[i][j].hold()
                elif pressed[2] and (
                        self.mine_counter.get_value() > 0 or self.field[i][j].mark is not None):
                    deltas = {'F': -1, 'Q': 1, None: 0}
                    self.field[i][j].set_mark()
                    self.mine_counter.change_value(deltas[self.field[i][j].mark])
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


@dataclass
class Game:
    layout: LayoutPreset
    game_preset: GamePreset
    presets: dict[str, GamePreset]
    current_screen: Screens = Screens.MAIN
    settings_layout: Optional[pg.sprite.Group] = None
    help_layout: Optional[pg.sprite.Group] = None
    panel: Optional[pg.sprite.Group] = None
    menu_bar: Optional[pg.sprite.Group] = None
    screen: Optional[pg.Surface] = None
    field: Optional[Field] = None
    screens: Optional[dict[Screens, pg.Surface]] = None
    timer: Optional[Counter] = None
    height_input: Optional[TextInput] = None
    width_input: Optional[TextInput] = None
    mines_count_input: Optional[TextInput] = None

    def init_screens(self):
        field_w, field_h = self.game_preset.field_size
        font = pg.font.Font('assets/lcd.ttf', 20)

        w = self.layout.left_indent * 2 + self.layout.cell_size * field_w

        h = self.layout.top_indent + self.layout.cell_size * field_h + \
            self.layout.left_indent + self.layout.menubar_height

        self.screen = pg.display.set_mode((w, h))
        self.screens = {name: pg.Surface((w, h)) for name in Screens}
        pg.display.set_caption('Minesweeper')

        panel_y = \
            self.layout.left_indent - self.layout.field_indent + (
                    self.layout.top_indent - 25) / 2 - self.layout.indicator_size // 2 + \
            self.layout.menubar_height

        indicator = Indicator(
            self.layout.left_indent + self.layout.cell_size * field_w / 2 -
            self.layout.indicator_size // 2,
            panel_y,
            self.layout.indicator_size)

        mine_counter = Counter(self.layout.left_indent * 2 - self.layout.field_indent, panel_y,
                               self.layout.counter_width,
                               self.layout.indicator_size, self.game_preset.mines_count)

        self.timer = Counter(
            field_w * self.layout.cell_size + self.layout.left_indent -
            self.layout.field_indent * 2 - self.layout.counter_width,
            panel_y, self.layout.counter_width, self.layout.indicator_size)

        self.panel = pg.sprite.Group(indicator, mine_counter, self.timer)
        self.field = Field(field_w, field_h, self.layout.left_indent,
                           self.layout.top_indent + self.layout.menubar_height,
                           self.layout.cell_size, indicator, mine_counter,
                           self.game_preset.mines_count)

        button_font = pg.font.Font('assets/lcd.ttf', 16)
        settings_button = MenuButton(0, 0, self.layout.menubar_height, 'Settings', button_font,
                                     on_click=lambda: self.change_screen(Screens.SETTINGS))
        help_button = MenuButton(settings_button.rect.w, 0, self.layout.menubar_height, 'Help',
                                 button_font,
                                 on_click=lambda: self.change_screen(Screens.HELP))
        self.menu_bar = pg.sprite.Group(settings_button, help_button)

        self.screens[Screens.MAIN].fill(MAIN_GRAY)
        self.screens[Screens.MAIN].blit(
            draw_cell(field_w * self.layout.cell_size + self.layout.field_indent * 2,
                      field_h * self.layout.cell_size + self.layout.field_indent * 2,
                      self.layout.field_indent, False),
            (self.layout.left_indent - self.layout.field_indent,
             self.layout.top_indent - self.layout.field_indent + self.layout.menubar_height))
        self.screens[Screens.MAIN].blit(
            draw_cell(field_w * self.layout.cell_size + self.layout.field_indent * 2,
                      self.layout.top_indent - 25, convex=False),
            (self.layout.left_indent - self.layout.field_indent,
             self.layout.left_indent - self.layout.field_indent + self.layout.menubar_height))
        pg.draw.rect(self.screens[Screens.MAIN], 'white', (0, 0, w, self.layout.menubar_height))
        if self.settings_layout is not None:
            values = [i.get_value(str) for i in self.settings_layout if isinstance(i, TextInput)]
        else:
            values = [''] * 3
        self.settings_layout = pg.sprite.Group()
        r = 8
        x0 = w / 2 - 150
        y0 = h / 2 - 200
        x = x0 + self.layout.field_indent + 2 * r + 5
        header_font = pg.font.Font('assets/lcd.ttf', 24)
        header = Label(x0 + self.layout.left_indent, y0 + self.layout.left_indent, 'Difficulty',
                       header_font,
                       self.settings_layout)
        y = header.rect.y + header.rect.h + 10
        if len(RADIO_GROUP) > 0:
            checked_buttons = [b.checked for b in RADIO_GROUP.sprites()]
        else:
            checked_buttons = [True] + [False] * len(self.presets)
        RADIO_GROUP.empty()
        for (name, preset), checked in zip(self.presets.items(), checked_buttons):
            button = RadioButton(x0 + self.layout.field_indent, y, r, self.settings_layout,
                                 checked=checked)
            Label(x, y,
                  f'{name.title()} ({"×".join(map(str, preset.field_size))}, '
                  f'{preset.mines_count} mines)',
                  font, self.settings_layout, assigned_item=button)
            y += r * 2 + 10

        button = RadioButton(x0 + self.layout.field_indent, y, r, self.settings_layout,
                             checked=checked_buttons[-1])
        Label(x, y, 'Custom', font, self.settings_layout, assigned_item=button)
        y += r * 2 + 10

        sep, shift = 70, 10
        self.width_input = TextInput(x + sep, y, 60, 30, font, IntValidator(9, 24), handle_change,
                                     self.settings_layout)
        self.width_input.set_value(values[0])
        Label(x, y + shift, 'Width:', font, self.settings_layout, assigned_item=self.width_input)
        self.height_input = TextInput(x + sep, y + 40, 60, 30, font, IntValidator(9, 24),
                                      handle_change,
                                      self.settings_layout)
        self.height_input.set_value(values[1])
        Label(x, y + 40 + shift, 'Height:', font, self.settings_layout,
              assigned_item=self.height_input)
        self.mines_count_input = TextInput(x + sep, y + 80, 60, 30, font, IntValidator(10, 99),
                                           lambda: None,
                                           self.settings_layout)
        self.mines_count_input.set_value(values[2])
        Label(x, y + 80 + shift, 'Mines:', font, self.settings_layout,
              assigned_item=self.mines_count_input)

        Button(x0 + 200, y + 150, 75, 30, 'OK', font, self.settings_layout,
               on_click=lambda: self.change_screen(Screens.MAIN))
        self.screens[Screens.SETTINGS].fill(MAIN_GRAY)

        self.screens[Screens.HELP].fill(MAIN_GRAY)
        self.help_layout = pg.sprite.Group()
        help_header = Label(x0 + self.layout.left_indent, y0 + self.layout.left_indent, 'Help',
                            header_font, self.help_layout)
        y = y0 + self.layout.left_indent + help_header.rect.h + 15
        with open('docs/help.txt') as f:
            for line in f.read().split('\n'):
                label = Label(x0 + self.layout.left_indent, y, line, font, self.help_layout)
                y += label.rect.h + 5
        y += 30
        little_font = pg.font.Font('assets/lcd.ttf', 16)
        Label(x0 + self.layout.left_indent, y, '© dQw4w9WgXcQ Games, 2021', little_font,
              self.help_layout)
        y += 20
        Label(x0 + self.layout.left_indent, y, 'Original game made by Microsoft', little_font,
              self.help_layout)
        Button(w - x0 - 150 - self.layout.left_indent,
               y0 + self.layout.left_indent - self.layout.field_indent, 150, 30,
               'Back to game →', font,
               self.help_layout, on_click=lambda: self.change_screen(Screens.MAIN))

    def change_screen(self, to: Screens):
        if to == Screens.SETTINGS:
            pg.time.set_timer(TOGGLECURSOREVENT, 500)

        elif to == Screens.MAIN and self.current_screen == Screens.SETTINGS:
            preset_name = get_preset_name(RADIO_GROUP)

            new_preset = self.presets.get(preset_name,
                                          GamePreset(field_size=(self.width_input.get_value(int),
                                                                 self.height_input.get_value(int)),
                                                     mines_count=self.mines_count_input.get_value(
                                                         int)))
            if new_preset != self.game_preset:
                self.game_preset = new_preset
                self.init_screens()

        self.current_screen = to

    def draw(self):
        for screen in Screens:
            if screen == Screens.MAIN:
                self.field.draw(self.screens[Screens.MAIN])
                self.panel.draw(self.screens[Screens.MAIN])
                self.menu_bar.draw(self.screens[Screens.MAIN])

            elif screen == Screens.SETTINGS:
                self.settings_layout.draw(self.screens[Screens.SETTINGS])

            elif screen == Screens.HELP:
                self.help_layout.draw(self.screens[Screens.HELP])

        self.screen.blit(self.screens[self.current_screen], (0, 0))
