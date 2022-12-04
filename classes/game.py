import sys
import pygame
import torch
import igraph as ig
from rich.console import Console
from rich.table import Table

from classes.hive import HiveGame, Hive
from classes.hive_ui import extend_hive
from classes.ui import UI

GAME_MODES = ["cpu_vs_cpu",'man_vs_cpu','man_vs_man']

class Game:
    def __init__(self, mode):
        if mode not in GAME_MODES:
            raise NotImplementedError(f"{mode} game mode not implemented yet.")
        self.mode = mode
        self.hives = HiveGame()
        self.hive_white = self.hives.hive_white
        self.hive_black = self.hives.hive_black
        self.winner = None
        if mode == 'man_vs_cpu' or mode == 'man_vs_man':
            extend_hive()
        if mode == 'man_vs_cpu' or mode == 'man_vs_man':
            self.ui = UI(self.hives)

        self.hives.generate_legal_moves()

    def get_game_info(self, args):
        console = Console()

        table = Table(title="Hive Game", show_header=True, header_style="bold magenta")
        table.add_column("Parameters", justify="center")
        table.add_column("Value", justify="right")
        table.add_row("Mode", str(args[0]))
        table.add_row("Game", str(args[1]))
        console.print(table)

    def play(self):

        if self.mode=="man_vs_cpu" or self.mode=='man_vs_man':
            piece_index,hex_index = self.ui.get_node_hover()
            # self.ui.hexes_player.hover_hex(piece_index)
            self.hives.ui_hover(piece_index)
            self.ui.hexes_board.hover_hex(hex_index)

        pygame.display.update()
        self.ui.clock.tick(30)
        self.handle_events(piece_index,hex_index)

        # if self.ui.next_player:
        #     self.next_player()



        if self.hives.ui_update or self.ui.hexes_board.update_board:
            self.ui.redraw_board()

        if self.hives.winner is not None:
            pygame.display.update()
            self.ui.clock.tick(30)
            self.winner = self.hives.winner


    # def next_player(self):
    #     self.whites_turn = not self.whites_turn
    #     if self.whites_turn:
    #         self.turn += 1
    #     self.ui.advance_to_next_player()


    def handle_events(self,piece_index,hex_index):
        if self.mode=="man_vs_cpu" or self.mode=="man_vs_man":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONUP:
                    if piece_index is not None or hex_index is not None:
                        self.ui.click_piece(piece_index,hex_index)



