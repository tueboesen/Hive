from math import cos, sin, pi, radians

import numpy as np
import pygame
import torch
from pygame import gfxdraw
from pygame import time

from classes.ui_hex import Hexes


class UI:
    def __init__(self, board_size: int, pieces_white, pieces_black,turn=1,whites_turn=True):
        self.board_size = board_size
        assert 1 < self.board_size <= 26
        self.next_player = False
        self.clock = time.Clock()
        self.hex_radius = 20
        self.offset = 3
        self.x_offset, self.y_offset = 120, 60
        self.text_offset = 45
        self.screen = pygame.display.set_mode(
            (1.5*self.x_offset + (2 * self.hex_radius) * self.board_size + self.hex_radius * self.board_size,
             round(self.y_offset + (1.75 * self.hex_radius) * self.board_size)))

        # Colors
        self.red = (222, 29, 47)
        self.blue = (0, 121, 251)
        self.green = (0, 255, 0)
        self.white = (200, 200, 200)
        self.color_highlight = (0, 255, 0)
        self.color_hover = (0, 121, 251)
        self.white_selected = (255, 255, 255)
        self.black = (40, 40, 40)
        # self.black_highlight = (50, 50, 50)
        self.black_selected = (60, 60, 60)
        self.gray = (70, 70, 70)
        self.brown = (164,116,73)
        # self.brown_highlight = (180,128,80)
        self.gold = (255,215,0)
        self.board_color = self.brown

        self.screen.fill(self.gray)
        self.fonts = pygame.font.SysFont("Sans", 20)
        self.hexes_board = Hexes(self.screen, self.offset, self.hex_radius, self.brown, self.color_hover, None, self.color_highlight)
        self.hexes_white = Hexes(self.screen, self.offset, self.hex_radius, self.white, self.color_hover, self.white_selected, self.color_highlight)
        self.hexes_black = Hexes(self.screen, self.offset, self.hex_radius, self.black, self.color_hover, self.black_selected, self.color_highlight)
        # self.hex_indices_lookup = {}
        # self.hex_ids = torch.ones(board_size,board_size,dtype=torch.int16)

        # self.piece_lookup = {} #A dict of all pieces on and off the board
        # self.rects_board = [] #A list of all rectangles on the board that we check for mouse-movement
        # self.rects_white = [] # A list of all rectangles for the white pieces
        # self.rects_black = [] # A list of all rectangles for the black pieces

        self.turn = turn
        self.whites_turn = whites_turn

        self.piece_white = pieces_white
        self.piece_black = pieces_black

        # self.rects_player = self.rects_white if self.whites_turn else self.rects_black
        self.hexes_player = self.hexes_white if self.whites_turn else self.hexes_black
        self.piece_player = self.piece_white if self.whites_turn else self.piece_black
        self.draw_initial_board()

    def advance_to_next_player(self):
        #TODO this method already exist in game.py and should be made smarter, such that it depends on that. Perhaps a shared class method?
        self.whites_turn = not self.whites_turn
        if self.whites_turn:
            self.turn += 1
        self.hexes_board.reset_color_hexes()
        self.hexes_player.reset_color_hexes()
        self.hexes_player.hex_selected = None
        self.hexes_player = self.hexes_white if self.whites_turn else self.hexes_black
        self.next_player = False


    def convert_idx_to_row_col(self,idx):
        row = idx // self.board_size
        col = idx % self.board_size
        return row, col

    def convert_bitboard_to_indices(self,bitboard:torch.Tensor) -> list:
        bitboard = bitboard[1:-1,1:-1]
        indices = torch.flatten(bitboard).nonzero()
        return indices.squeeze().tolist()


    def draw_initial_board(self):
        self.draw_text_summary()
        for row in range(self.board_size):
            for column in range(self.board_size):
                x,y = self.get_coordinates(row, column)
                self.hexes_board.create_hex(x,y)
        self.hexes_board.draw_hexes()

        for i, piece in enumerate(self.piece_white):
            x,y = self.get_coordinates_starting_pieces(True, i)
            self.hexes_white.create_hex(x,y,symbol=str(piece))
        self.hexes_white.draw_hexes()

        for i, piece in enumerate(self.piece_black):
            x,y = self.get_coordinates_starting_pieces(False, i)
            self.hexes_black.create_hex(x,y,symbol=str(piece))
        self.hexes_black.draw_hexes()
        self.hexes_board.draw_highlights()
        return

    def redraw_board(self):
        self.screen.fill(self.gray)
        self.draw_text_summary()
        self.hexes_board.draw_hexes()
        self.hexes_white.draw_hexes()
        self.hexes_black.draw_hexes()
        self.hexes_board.draw_highlights()


    def draw_text_summary(self):
        txt = f"Turn: {self.turn},   Players turn: {'White' if self.whites_turn else 'Black'}"
        node_font = pygame.font.SysFont("Sans", 18)
        foreground = self.black
        text = node_font.render(txt, True, foreground, self.white)
        text_rect = text.get_rect()
        text_rect.center = (500,20)
        self.screen.blit(text, text_rect)


    # def highlight_piece(self, piece_idx:int,highlight:bool):
    #     self.piece_idx_highlighted = piece_idx if highlight else None
    #     is_piece_selected = piece_idx == self.piece_idx_selected
    #     if is_piece_selected:
    #         color = self.gold
    #     elif highlight:
    #         color = self.green
    #     else:
    #         color = self.black
    #     # color = self.green if highlight else self.black
    #     piece_pos = self.hexes_player[piece_idx].xy_outer
    #     # gfxdraw.filled_polygon(self.screen,piece_pos,color)
    #     gfxdraw.aapolygon(self.screen,piece_pos,color)
    #
    # def highlight_potential_moves(self):
    #     moves = self.piece_player[self.piece_idx_selected].moves
    #     color = self.color.view(self.board_size,self.board_size)
    #     color[moves] = self.light_brown
    #

    def move_piece(self, piece_idx,hex_idx):
        x, y = self.hexes_board[hex_idx].pos()
        self.hexes_player.move_hex(piece_idx, x, y)
        print("here")
        self.piece_player[piece_idx].in_play = True
        row, col = self.convert_idx_to_row_col(hex_idx)
        self.piece_player[piece_idx].pos = (row,col)
        self.next_player = True


    def click_piece(self, piece_idx,hex_idx):
        piece_sel = self.hexes_player.hex_selected
        if hex_idx is not None and piece_sel is not None and self.piece_player[piece_sel].moves is not None: #Attempt to move hex_sel to hex_idx
            row,col = self.convert_idx_to_row_col(hex_idx)
            if self.piece_player[piece_sel].moves[row+1,col+1]: #Move allowed?
                self.move_piece(piece_sel,hex_idx)


        if piece_idx is not None: # Toggle selection of piece
            self.hexes_player.select_hex(piece_idx)
        if self.hexes_player.hex_selected is None: # Remove highlighted moves
            self.hexes_board.reset_color_hexes()
        else: # Highlight potential moves
            moves = self.piece_player[self.hexes_player.hex_selected].moves
            if moves is not None:
                indices = self.convert_bitboard_to_indices(moves)
                self.hexes_board.highlight_hex(indices)
                

    def get_coordinates(self, row: int, column: int):
        x = self.x_offset + (2 * self.hex_radius) * column + self.hex_radius * row
        y = self.y_offset + (1.75 * self.hex_radius) * row
        return x, y

    def get_coordinates_starting_pieces(self, left: bool, index: int):
        col = -2 if left else self.board_size+1
        return self.get_coordinates(2*index,col)

    def get_true_coordinates(self, node: int):
        return int(node / self.board_size), node % self.board_size

    def get_node_hover(self):
        """
        Determines which hex and piece the mouse is hovering over
        :return:
        """
        mouse_pos = pygame.mouse.get_pos()
        piece_index = None
        for i, hex in enumerate(self.hexes_player):
            if hex.rect.collidepoint(mouse_pos):
                piece_index = i
                break

        board_index = None
        for i, hex in enumerate(self.hexes_board):
            if hex.rect.collidepoint(mouse_pos):
                board_index = i
                break



        # if self.piece_idx_highlighted is not None and self.piece_idx_highlighted != piece_index:
        #     self.highlight_piece(self.piece_idx_highlighted,highlight=False) #Remove highlight of old pieces
        #
        # if type(piece_index) is int:
        #     self.highlight_piece(piece_index,highlight=True)

        return piece_index, board_index

