import sys
import pygame
import torch
import igraph as ig
from rich.console import Console
from rich.table import Table

from classes.hive import HiveGamePieces
from classes.ui import UI

GAME_MODES = ["cpu_vs_cpu",'man_vs_cpu','man_vs_man']
BOARD_SIZE = 22


class Game:
    def __init__(self, mode):
        if mode not in GAME_MODES:
            raise NotImplementedError(f"{mode} game mode not implemented yet.")
        self.mode = mode
        self.hive = HiveGamePieces()
        self.pieces_white = self.hive.hive_white
        self.pieces_black = self.hive.hive_black
        self.winner = 0
        self.turn = 1
        self.whites_turn = True
        self.white_queen_played = False
        self.black_queen_played = False
        self.generate_legal_moves()
        self.ui = UI(BOARD_SIZE,self.pieces_white,self.pieces_black)

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
            self.ui.hexes_player.hover_hex(piece_index)
            self.ui.hexes_board.hover_hex(hex_index)

        pygame.display.update()
        self.ui.clock.tick(30)
        self.handle_events(piece_index,hex_index)

        if self.ui.next_player:
            self.next_player()

        if self.ui.hexes_player.update_board or self.ui.hexes_board.update_board:
            self.ui.redraw_board()

    def next_player(self):
        self.whites_turn = not self.whites_turn
        if self.whites_turn:
            self.turn += 1
        self.ui.advance_to_next_player()


    def handle_events(self,piece_index,hex_index):
        if self.mode=="man_vs_cpu":
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

    def generate_clean_board_state(self):
        board_state = torch.zeros(BOARD_SIZE+2,BOARD_SIZE+2,dtype=torch.int8)
        return board_state

    def generate_bitmap_board_state(self,default_state=False):
        if default_state:
            board_state = torch.ones(BOARD_SIZE+2,BOARD_SIZE+2,dtype=torch.bool)
            board_state[0,:] = False
            board_state[-1,:] = False
            board_state[:,0] = False
            board_state[:,-1] = False
        else:
            board_state = torch.zeros(BOARD_SIZE+2,BOARD_SIZE+2,dtype=torch.bool)
        return board_state


    def get_neighboring_pos(self, board):
        board1 = torch.roll(board,1,dims=0)
        board2 = torch.roll(board,1,dims=1)
        board3 = torch.roll(board,-1,dims=0)
        board4 = torch.roll(board,-1,dims=1)
        board5 = torch.roll(board1,1,dims=1)
        board6 = torch.roll(board3,-1,dims=1)
        board_nn = board1 | board2 | board3 | board4 | board5 | board6
        return board_nn



    def get_pieces_that_does_not_cut_graph(self,graph):
        bridges = graph.bridges()
        moveable_nodes = set(graph.nodes)
        for bridge in bridges:
            node1,node2 = get_nodes(bridge)
            moveable_nodes.remove(node1)
            moveable_nodes.remove(node2)
        for node in graph.nodes:
            if n_edges(node) == 1:
                moveable_nodes.add(node)
        return moveable_nodes


    def generate_legal_moves(self):
        pieces_player = self.pieces_white if self.whites_turn else self.pieces_black
        pieces_opp = self.pieces_black if self.whites_turn else self.pieces_white

        # board_state_player = self.generate_clean_board_state()
        board_state_player = self.generate_bitmap_board_state()
        board_state_opp = self.generate_bitmap_board_state()
        #First we generate a list of pieces already on the board
        for piece in pieces_player:
            if piece.in_play and piece.level == 0:
                board_state_player[piece.pos[0], piece.pos[1]] = True
        for piece in pieces_opp:
            if piece.in_play and piece.level == 0:
                board_state_opp[piece.pos[0], piece.pos[1]] = True

        if pieces_player.played_all_pieces: # Generate list of spawn locations
            spawn_locations = None
        else:
            if pieces_player.played_piece:
                board1 = self.get_neighboring_pos(board_state_player)
                board2 = self.get_neighboring_pos(board_state_opp)
                spawn_locations = board1 ^ (not (board2 | board_state_opp))
            else:
                if pieces_opp.played_piece:
                    spawn_locations = self.get_neighboring_pos(board_state_opp)
                else:
                    spawn_locations = self.generate_bitmap_board_state(default_state=True)

        #Then we go through each piece and see where it can move to
        if not pieces_player.played_queen and self.turn >= 4:
            for piece in pieces_player:
                if piece == 'Q':
                    piece.moves = spawn_locations
                else:
                    piece.moves = None
        else:
            for piece in pieces_player:
                if piece.in_play is False:
                    piece.moves = spawn_locations
                elif piece.moveable:
                    piece.moves = piece.calculate_moves(board_state_combined)
                else:
                    piece.moves = None
        return
