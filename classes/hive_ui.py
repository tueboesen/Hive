from math import cos, sin, pi, radians

from classes.const import WHITE, BLACK, BLUE, ICON_SIZE
from classes.hive import Hive, Piece, HiveGame
import pygame
from pygame import gfxdraw



def color_fill(self):
    return WHITE if self.white else BLACK


def x_pixel(self):
    return self.ui_x_offset + (2 * self.ui_hex_radius) * self.x + self.ui_hex_radius * self.y

def y_pixel(self):
    return self.ui_y_offset + (1.75 * self.ui_hex_radius) * self.y

def calculate_xy_outer(self):
    return [(self.ui_x() + (self.ui_hex_radius + self.ui_hex_ios) * cos(radians(90) + 2 * pi * _ / 6),
             self.ui_y() + (self.ui_hex_radius + self.ui_hex_ios) * sin(radians(90) + 2 * pi * _ / 6))
                     for _ in range(6)]

def calculate_xy_inner(self):
    return [(self.ui_x() + self.ui_hex_radius * cos(radians(90) + 2 * pi * _ / 6),
                      self.ui_y() + self.ui_hex_radius * sin(radians(90) + 2 * pi * _ / 6))
                     for _ in range(6)]

def calculate_xy_rect(self):
    # return (self.ui_x() - self.ui_hex_radius + self.ui_offset, self.ui_y() - (self.ui_hex_radius / 2),
    #                 (self.ui_hex_radius * 2) - (2 * self.ui_offset), self.ui_hex_radius)
    return (self.ui_x() - self.ui_hex_radius + 3 * self.ui_hex_ios, self.ui_y() - (self.ui_hex_radius / 2),
            (self.ui_hex_radius * 2) - (6 * self.ui_hex_ios), self.ui_hex_radius)

def reset_color(self):
    self.ui_color_fill = self._ui_color_fill
    self.ui_color_inner_edge = self._ui_color_inner_edge
    self.ui_color_outer_edge = self._ui_color_outer_edge

def draw(self):
    if self.level == 0:
        # gfxdraw.aapolygon(self.screen, self.xy_outer, self.color_edge) # Outer hexagon edge
        self.ui_draw_rect()
        gfxdraw.filled_polygon(self.ui_screen, self.ui_xy_inner(), self.ui_color_fill) # Inner filled hexagon
        gfxdraw.aapolygon(self.ui_screen, self.ui_xy_inner(), self.ui_color_inner_edge) # Inner hexagon edge

        if self.icon is not None:
            rect = self.icon.get_rect()
            pieces = len(self.pieces_under)
            if pieces > 0:
                icons_to_draw = pieces + 1
                dx = ICON_SIZE[0] / icons_to_draw/2
                for i,piece in enumerate(self.pieces_under):
                    icon = piece.icon
                    icon = pygame.transform.scale(icon, (ICON_SIZE[0]/2,ICON_SIZE[1]/2))
                    rect_under = icon.get_rect()
                    rect_under.center = (self.ui_x()+int(ICON_SIZE[0]/4 - i*dx), self.ui_y())
                    self.ui_screen.blit(icon, rect_under)

                icon = pygame.transform.scale(self.icon, (ICON_SIZE[0]/2,ICON_SIZE[1]/2))
                rect.center = (self.ui_x()-int(ICON_SIZE[0]/4), self.ui_y())
                self.ui_screen.blit(icon, rect)


            else:
                rect.center = (self.ui_x(), self.ui_y())
                self.ui_screen.blit(self.icon, rect)
        elif self.symbol() is not None:
            text = pygame.font.SysFont("Sans", 18).render(f"{self.symbol() if len(self.pieces_under)==0 else self.symbol()+'+'+str(self.pieces_under)}", True, self.ui_color_text) #, self.ui_color_text_bg
            text_rect = text.get_rect()
            text_rect.center = (self.ui_x(), self.ui_y())
            self.ui_screen.blit(text, text_rect)
    else: #
        self.ui_rect = None

def draw_rect(self):
    self.ui_rect = pygame.draw.rect(self.ui_screen, self.ui_color_fill, pygame.Rect(self.ui_xy_rect()))


def hover(self, idx: int):
    if idx == self.ui_hovered: # Nothing has changed
        return
    if self.ui_hovered is not None: # Remove old hovered hex
        self.pieces[self.ui_hovered].ui_color_inner_edge = self.pieces[self.ui_hovered]._ui_color_inner_edge
        self.ui_hovered = None
    if idx is not None: # Set new hovered hex
        self.pieces[idx].ui_color_inner_edge = BLUE
        self.ui_hovered = idx
        self.ui_update = True


def extend_hive():
    # HiveGame.ui_selected = None
    # HiveGame.ui_hovered = None
    # HiveGame.ui_update = False
    # HiveGame.ui_hover = hover
    Piece.ui_reset_color = reset_color
    Piece.ui_x = x_pixel
    Piece.ui_y = y_pixel
    Piece.ui_xy_outer = calculate_xy_outer
    Piece.ui_xy_inner = calculate_xy_inner
    Piece.ui_xy_rect = calculate_xy_rect
    Piece.ui_draw_rect = draw_rect
    Piece.ui_draw = draw




