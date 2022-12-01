from math import cos, sin, pi, radians

import numpy as np
import pygame
from pygame import gfxdraw
from pygame import time


class UI:
    def __init__(self, board_size: int, pieces_white, pieces_black):
        self.board_size = board_size
        assert 1 < self.board_size <= 26

        self.clock = time.Clock()
        self.hex_radius = 20
        self.x_offset, self.y_offset = 160, 60
        self.text_offset = 45
        self.screen = pygame.display.set_mode(
            (self.x_offset + (2 * self.hex_radius) * self.board_size + self.hex_radius * self.board_size,
             round(self.y_offset + (1.75 * self.hex_radius) * self.board_size)))

        # Colors
        self.red = (222, 29, 47)
        self.blue = (0, 121, 251)
        self.green = (0, 255, 0)
        self.white = (255, 255, 255)
        self.black = (40, 40, 40)
        self.gray = (70, 70, 70)
        self.brown = (164,116,73)
        self.gold = (255,215,0)
        self.board_color = self.brown


        self.screen.fill(self.black)
        self.fonts = pygame.font.SysFont("Sans", 20)

        self.hex_lookup = {}
        self.piece_lookup = {}
        self.rects_board, self.color, self.node = [], [self.board_color] * (self.board_size ** 2), None
        self.color_pieces = []
        self.rects_pieces = []
        self.turn = 1
        self.whites_turn = True

        self.pieces_white = pieces_white
        self.pieces_black = pieces_black
        self.piece = None
        self.piece_selected = None

    def draw_hexagon_piece(self, surface: object, color: tuple, position: tuple, node: int, icon: str):
        # Vertex count and radius
        n = 6
        x, y = position
        offset = 3

        # Outline
        self.piece_lookup[node] = [(x + (self.hex_radius + offset) * cos(radians(90) + 2 * pi * _ / n),
                                  y + (self.hex_radius + offset) * sin(radians(90) + 2 * pi * _ / n))
                                 for _ in range(n)]
        gfxdraw.aapolygon(surface,
                          self.piece_lookup[node],
                          color)
        self.color_pieces.append(color)

        # Shape
        gfxdraw.filled_polygon(surface,
                               [(x + self.hex_radius * cos(radians(90) + 2 * pi * _ / n),
                                 y + self.hex_radius * sin(radians(90) + 2 * pi * _ / n))
                                for _ in range(n)],
                               color)

        # Antialiased shape outline
        gfxdraw.aapolygon(surface,
                          [(x + self.hex_radius * cos(radians(90) + 2 * pi * _ / n),
                            y + self.hex_radius * sin(radians(90) + 2 * pi * _ / n))
                           for _ in range(n)],
                          self.black)

        # Placeholder
        rect = pygame.draw.rect(surface,
                                color,
                                pygame.Rect(x - self.hex_radius + offset, y - (self.hex_radius / 2),
                                            (self.hex_radius * 2) - (2 * offset), self.hex_radius))
        self.rects_pieces.append(rect)

        node_font = pygame.font.SysFont("Sans", 18)
        foreground = self.black
        # foreground = self.black if self.color[self.node] is self.white else self.white
        text = node_font.render('Q', True, foreground, self.blue)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text, text_rect)

    def highlight_piece(self, piece_idx:int,highlight:bool):
        self.piece = piece_idx if highlight else None
        color = self.green if highlight else self.black
        piece = self.piece_lookup[piece_idx]
        gfxdraw.aapolygon(self.screen,
                          piece,
                          color)

    def select_piece(self,piece_idx:int):
        self.piece_selected = piece_idx if self.piece_selected is None else None
        piece = self.piece_lookup[piece_idx]
        color = self.board_color if self.piece_selected is None else self.gold
        self.color_pieces[piece_idx] = color
        gfxdraw.filled_polygon(self.screen, piece, color)


    def move_piece(self, piece_idx,location):
        pass

    def click_piece(self, piece_idx):
        if self.piece_selected is None or self.piece_selected == piece_idx: #Toggle piece
            self.select_piece(piece_idx)
        elif piece_idx in self.legal_moves:
            self.move_piece(self.piece_selected,piece_idx)



    def draw_hexagon(self, surface: object, color: tuple, position: tuple, node: int):
        # Vertex count and radius
        n = 6
        x, y = position
        offset = 3

        # Outline
        self.hex_lookup[node] = [(x + (self.hex_radius + offset) * cos(radians(90) + 2 * pi * _ / n),
                                  y + (self.hex_radius + offset) * sin(radians(90) + 2 * pi * _ / n))
                                 for _ in range(n)]
        gfxdraw.aapolygon(surface,
                          self.hex_lookup[node],
                          color)

        # Shape
        gfxdraw.filled_polygon(surface,
                               [(x + self.hex_radius * cos(radians(90) + 2 * pi * _ / n),
                                 y + self.hex_radius * sin(radians(90) + 2 * pi * _ / n))
                                for _ in range(n)],
                               self.color[node])

        # Antialiased shape outline
        gfxdraw.aapolygon(surface,
                          [(x + self.hex_radius * cos(radians(90) + 2 * pi * _ / n),
                            y + self.hex_radius * sin(radians(90) + 2 * pi * _ / n))
                           for _ in range(n)],
                          self.black)

        # Placeholder
        rect = pygame.draw.rect(surface,
                                self.color[node],
                                pygame.Rect(x - self.hex_radius + offset, y - (self.hex_radius / 2),
                                            (self.hex_radius * 2) - (2 * offset), self.hex_radius))
        self.rects_board.append(rect)

    def draw_text_summary(self):
        # x, y = self.get_true_coordinates(self.node)
        # x, y = self.get_coordinates(x, y)
        txt = f"Turn: {self.turn},   Players turn: {'White' if self.whites_turn else 'Black'}"
        node_font = pygame.font.SysFont("Sans", 18)
        # foreground = self.black if self.color[self.node] is self.white else self.white
        foreground = self.black
        text = node_font.render(txt, True, foreground, self.color[4])
        text_rect = text.get_rect()
        # text_rect.center = (x, y)
        text_rect.center = (500,20)
            # (self.text_offset / 4 + self.hex_radius * _, self.y_offset + (1.75 * self.hex_radius) * _))

        self.screen.blit(text, text_rect)

    # def draw_text(self):
    #     alphabet = list(map(chr, range(97, 123)))
    #
    #     for _ in range(self.board_size):
    #         # Columns
    #         text = self.fonts.render(alphabet[_].upper(), True, self.white, self.black)
    #         text_rect = text.get_rect()
    #         text_rect.center = (self.x_offset + (2 * self.hex_radius) * _, self.text_offset / 2)
    #         self.screen.blit(text, text_rect)
    #
    #         # Rows
    #         text = self.fonts.render(str(_), True, self.white, self.black)
    #         text_rect = text.get_rect()
    #         text_rect.center = (
    #             (self.text_offset / 4 + self.hex_radius * _, self.y_offset + (1.75 * self.hex_radius) * _))
    #         self.screen.blit(text, text_rect)

    def draw_board(self, show_mcts_predictions: bool = False):
        counter = 0
        for row in range(self.board_size):
            for column in range(self.board_size):
                self.draw_hexagon(self.screen, self.black, self.get_coordinates(row, column), counter)
                counter += 1
        self.draw_text_summary()

        # Filled polygons gradient-coloured based on MCTS predictions
        # (i.e. normalized #visits per node)
        if show_mcts_predictions:
            try:
                n = 6
                for (row, column) in mcts_predictions.keys():
                    x, y = self.get_coordinates(row, column)
                    gfxdraw.filled_polygon(self.screen,
                                           [(x + self.hex_radius * cos(radians(90) + 2 * pi * _ / n),
                                             y + self.hex_radius * sin(radians(90) + 2 * pi * _ / n))
                                            for _ in range(n)],
                                           self.green + (mcts_predictions[(row, column)],))
            except NameError:
                pass
        counter_piece = 0
        for i, piece in enumerate(self.pieces_white):
            self.draw_hexagon_piece(self.screen, self.white, self.get_coordinates_starting_pieces(True,i), counter_piece,piece)
            counter_piece += 1

        return


    def get_coordinates(self, row: int, column: int):
        x = self.x_offset + (2 * self.hex_radius) * column + self.hex_radius * row
        y = self.y_offset + (1.75 * self.hex_radius) * row

        return x, y

    def get_coordinates_starting_pieces(self, color: bool, index: int):
        x = (1 - color) * (self.board_size+2) * self.hex_radius + (2 * color - 1) * 50
        y = self.y_offset + (1.75 * self.hex_radius) * index
        return x,y

    def get_true_coordinates(self, node: int):
        return int(node / self.board_size), node % self.board_size

    def get_node_hover(self):
        # Source: https://bit.ly/2Wl5Grz
        mouse_pos = pygame.mouse.get_pos()
        mouse_index = None
        for i, rect in enumerate(self.rects_pieces):
            if rect.collidepoint(mouse_pos):
                mouse_index = i
                break
        if self.piece is not None and self.piece != mouse_index:
            self.highlight_piece(self.piece,highlight=False)

        if type(mouse_index) is int:
            self.highlight_piece(mouse_index,highlight=True)
            # self.piece_lookup[self.piece]
            # # Node
            # row, column = int(self.node / self.board_size), self.node % self.board_size
            # self.draw_hexagon(self.screen, self.green, self.get_coordinates(row, column), self.node)

            # Text
            # x, y = self.get_true_coordinates(self.node)
            # x, y = self.get_coordinates(x, y)
            # alphabet = list(map(chr, range(97, 123)))
            # txt = alphabet[column].upper() + str(row)
            # node_font = pygame.font.SysFont("Sans", 18)
            # foreground = self.black if self.color[self.node] is self.white else self.white
            # text = node_font.render(txt, True, foreground, self.color[self.node])
            # text_rect = text.get_rect()
            # text_rect.center = (x, y)
            # self.screen.blit(text, text_rect)

        return self.piece

    def show_mcts_predictions(self, output: list, available_pos: list):
        global mcts_predictions
        # Remove position played by MCTS player
        visits = [node[1] for node in output]
        output.pop(np.argmax(visits))
        # Get normalized visits
        normalized_visits = self.get_normalized_visits([node[1] for node in output])
        mcts_predictions = {(row, column): alpha_value for ((row, column), alpha_value) in
                            zip(available_pos, normalized_visits)}

    def get_normalized_visits(self, visits: list):
        normalized_visits = [node_visits - min(visits) for node_visits in visits]
        # Maximum set to 200 instead of 255 (RGBA)
        return [int(node_visits / max(normalized_visits) * 200) for node_visits in normalized_visits]
