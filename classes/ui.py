from math import cos, sin, pi, radians

import numpy as np
import pygame
import torch
from pygame import gfxdraw
from pygame import time

from classes.const import HEX_RADIUS, HEX_INNER_OUTER_SPACING, ICON_SIZE
from classes.hive import Hive, Piece
from classes.ui_hex import Hexes


class UI:
    def __init__(self, hives):
        self.hives = hives
        self.board_size = hives.board_size
        assert 1 < self.board_size <= 26

        self.hive_white = self.hives.hive_white
        self.hive_black = self.hives.hive_black
        self.clock = time.Clock()
        self.hex_radius = HEX_RADIUS
        self.hex_ios = HEX_INNER_OUTER_SPACING
        self.x_offset = 4 * HEX_RADIUS + 60
        self.y_offset = 60 + HEX_RADIUS
        # self.text_offset = 45
        self.screen = pygame.display.set_mode(
            (1.5*self.x_offset + (2 * self.hex_radius) * self.board_size + self.hex_radius * self.board_size,
             round(self.y_offset + (1.75 * self.hex_radius) * self.board_size)))

        Piece.ui_screen = self.screen
        Piece.ui_x_offset = self.x_offset
        Piece.ui_y_offset = self.y_offset


        # Colors
        # self.red = (222, 29, 47)
        # self.blue = (0, 121, 251)
        # self.green = (0, 255, 0)
        self.white = (255, 255, 255)
        self.color_highlight = (0, 255, 0)
        self.color_hover = (0, 121, 251)
        # self.white_selected = (255, 255, 255)
        self.black = (40, 40, 40)
        # self.black_highlight = (50, 50, 50)
        # self.black_selected = (60, 60, 60)
        self.gray = (70, 70, 70)
        self.brown = (164,116,73)
        # self.brown_highlight = (180,128,80)
        self.gold = (255,215,0)
        self.board_color = self.brown

        self.screen.fill(self.gray)
        self.fonts = pygame.font.SysFont("Sans", 20)
        self.hexes_board = Hexes(self.screen, self.hex_ios, self.hex_radius, self.brown, self.color_hover, None, self.color_highlight)
        self.draw_initial_board()

    def hive_player(self):
        return self.hive_white if self.whites_turn() else self.hive_black

    def whites_turn(self):
        return self.hives.whites_turn
        #
        # self.piece_white.ui = Hexes(self.screen, self.offset, self.hex_radius, self.white, self.color_hover, self.white_selected, self.color_highlight)
        #
        # self.hexes_white = Hexes(self.screen, self.offset, self.hex_radius, self.white, self.color_hover, self.white_selected, self.color_highlight)
        # self.hexes_black = Hexes(self.screen, self.offset, self.hex_radius, self.black, self.color_hover, self.black_selected, self.color_highlight)
        # # self.hex_indices_lookup = {}
        # # self.hex_ids = torch.ones(board_size,board_size,dtype=torch.int16)
        #
        # # self.piece_lookup = {} #A dict of all pieces on and off the board
        # # self.rects_board = [] #A list of all rectangles on the board that we check for mouse-movement
        # # self.rects_white = [] # A list of all rectangles for the white pieces
        # # self.rects_black = [] # A list of all rectangles for the black pieces
        #
        # self.turn = turn
        # self.whites_turn = whites_turn
        #
        #
        # # self.rects_player = self.rects_white if self.whites_turn else self.rects_black
        # self.hexes_player = self.hexes_white if self.whites_turn else self.hexes_black
        # self.piece_player = self.piece_white if self.whites_turn else self.piece_black
        # self.draw_initial_board()

    # def advance_to_next_player(self):
    #     self.whites_turn = not self.whites_turn
    #     if self.whites_turn:
    #         self.turn += 1
    #     self.hexes_board.reset_color_hexes()
    #     self.hexes_player.reset_color_hexes()
    #     self.hexes_player.hex_selected = None
    #     self.hexes_player = self.hexes_white if self.whites_turn else self.hexes_black
    #     self.next_player = False


    def convert_idx_to_row_col(self,idx):
        row = idx // self.board_size
        col = idx % self.board_size
        return row, col

    def convert_bitboard_to_indices(self,bitboard:torch.Tensor) -> list:
        bitboard = bitboard[1:-1,1:-1]
        indices = torch.flatten(bitboard).nonzero()
        indices = indices.squeeze().tolist()
        if type(indices) != list:
            indices = [indices]
        return indices


    def draw_initial_board(self):
        self.draw_text_summary()
        for row in range(self.board_size):
            for column in range(self.board_size):
                x,y = self.get_coordinates(row, column)
                self.hexes_board.create_hex(x,y)
        self.hexes_board.draw_hexes()

        for piece in self.hive_black:
            piece.ui_draw()

        for piece in self.hive_white:
            piece.ui_draw()
        self.hexes_board.draw_highlights()
        return

    def redraw_board(self):
        self.screen.fill(self.gray)
        self.draw_text_summary()
        self.hexes_board.draw_hexes()
        for piece in self.hive_black:
            piece.ui_draw()
        for piece in self.hive_white:
            piece.ui_draw()
        self.hexes_board.draw_highlights()
        self.hexes_board.update_board = False
        self.hive_player().ui_update = False
        if self.hives.winner is not None:
            self.draw_text_winner()


    def draw_text_summary(self):
        txt = f"Turn: {self.hives.turn},   Players turn: {'White' if self.hives.whites_turn else 'Black'}"
        node_font = pygame.font.SysFont("Sans", 18)
        foreground = self.black
        text = node_font.render(txt, True, foreground, self.white)
        text_rect = text.get_rect()
        text_rect.center = (self.screen.get_width()/2,20)
        self.screen.blit(text, text_rect)

    def draw_text_winner(self):
        txt = f"Winner: {self.hives.winner} in {self.hives.turn} turns."
        node_font = pygame.font.SysFont("Sans", 36)
        foreground = self.black
        text = node_font.render(txt, True, foreground, self.white)
        text_rect = text.get_rect()
        text_rect.center = (self.screen.get_width()/2,40)
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

    # def move_piece(self, piece_idx,hex_idx):
    #     x, y = self.hexes_board[hex_idx].pos()
    #     self.hexes_player.move_hex(piece_idx, x, y)
    #     print("here")
    #     self.piece_player[piece_idx].in_play = True
    #     row, col = self.convert_idx_to_row_col(hex_idx)
    #     self.piece_player[piece_idx].pos = (row,col)
    #     self.next_player = True


    def click_piece(self, piece_idx,hex_idx):
        # piece_sel = self.hexes_player.hex_selected
        piece_sel = self.hives.ui_selected
        if hex_idx is not None and piece_sel is not None and self.hives.moves(piece_sel) is not None: #Attempt to move hex_sel to hex_idx
            row,col = self.convert_idx_to_row_col(hex_idx)
            if self.hives.moves(piece_sel)[row+1,col+1]: #Move allowed?
                # x, y = self.hexes_board[hex_idx].pos()
                self.hives.move_piece(piece_sel,col,row)
                self.hives.generate_legal_moves()
                self.hives.ui_reset_board()
                self.hexes_board.reset_color_hexes()
                return

        if piece_idx is not None and piece_idx == self.hives.ui_selected: # unselect piece
            self.hives.ui_unselect_piece()
        elif piece_idx is not None and self.hives.ui_selected is None: # select piece
            self.hives.ui_select_piece(piece_idx)
        if self.hives.ui_selected is None: # Remove highlighted moves
            self.hexes_board.reset_color_hexes()
        else: # Highlight potential moves
            moves = self.hives.moves(self.hives.ui_selected)
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
        for i, piece in enumerate(self.hive_player()):
            if piece.ui_rect is not None and piece.ui_rect.collidepoint(mouse_pos):
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

