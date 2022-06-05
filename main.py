#!/bin/python3
import pygame as pg

from game import Game, Field
from misc.input_validators import IntValidator
from misc.util import terminate, get_presets
from misc.constants import UPDATEBOUNDSEVENT
from misc.components import Screens, LayoutPreset

FPS = 60

if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()
    presets = get_presets()
    game = Game(LayoutPreset(),
                presets[sorted(presets, key=lambda p: presets[p].mines_count)[0]], presets)
    game.init_screens()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()

            if game.current_screen == Screens.MAIN:
                if event.type == pg.MOUSEBUTTONDOWN:
                    game.field.hold(event.pos)
                    game.field.indicator.click(event.pos)

                if event.type == pg.MOUSEBUTTONUP:
                    game.field.get_click()
                    if game.field.indicator.release():
                        game.timer.set_value(0)
                        pg.time.set_timer(pg.USEREVENT, 0)
                        game.field.mine_counter.set_value(game.field.mines_count)
                        game.field = Field(game.field.w, game.field.h, game.field.left,
                                           game.field.top,
                                           game.field.cell_size, game.field.indicator,
                                           game.field.mine_counter,
                                           game.field.mines_count)

                if event.type == pg.USEREVENT:
                    game.timer.change_value(1)
                game.menu_bar.update(event)

            elif game.current_screen == Screens.SETTINGS:
                if event.type == UPDATEBOUNDSEVENT:
                    assert isinstance(game.mines_count_input.validator, IntValidator)
                    game.mines_count_input.validator.update_bounds(
                        max_val=game.height_input.get_value(int) *
                        game.width_input.get_value(int) - 1
                    )

                game.settings_layout.update(event)
            else:
                game.help_layout.update(event)

        game.panel.update()
        game.draw()
        pg.display.flip()
        clock.tick(FPS)
