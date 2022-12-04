import itertools
import typing
import igraph as ig
import torch

from classes.const import PLAYER1_SEL, PLAYER2_SEL, BLUE, WHITE, BLACK, PLAYER1, PLAYER2, HEX_RADIUS, HEX_INNER_OUTER_SPACING

PieceType = int
PIECE_TYPES = [QUEEN, BEETLE, GRASSHOPPER, SPIDER, ANT] = range(1,6)

PIECE_SYMBOLS = ["q", "b", "g", "s", "a"]
PIECE_NAMES = ["queen", "beetle", "grasshopper", "spider", "ant"]

PIECES_PER_PLAYER = ["q","b","b","b"]






def piece_symbol(piece_type: PieceType) -> str:
    return typing.cast(str, PIECE_SYMBOLS[piece_type])

def piece_name(piece_type: PieceType) -> str:
    return typing.cast(str, PIECE_NAMES[piece_type])

def piece_id(piece_type: PieceType) -> int:
    return PIECE_SYMBOLS.index(piece_type)

class Piece:
    """A piece with type and color."""

    def __init__(self, white:bool, piece_type:int, x:int,y: int):
        self.level = 0
        self.x = x
        self.y = y
        self.in_play = False
        self.white = white
        self.piece_type = piece_type
        self.moves = None
        self._calculate_moves = eval(f"self._moves_{piece_name(piece_type)}")
        self.pieces_under = 0

        self.ui_hex_radius = HEX_RADIUS
        self.ui_hex_ios = HEX_INNER_OUTER_SPACING-1
        self.ui_color_fill = PLAYER1 if self.white else PLAYER2
        self.ui_color_inner_edge = BLACK
        self.ui_color_outer_edge = BLACK
        self._ui_color_fill = PLAYER1 if self.white else PLAYER2
        self._ui_color_inner_edge = BLACK
        self._ui_color_outer_edge = BLACK
        self.ui_color_text = BLACK
        self.ui_color_text_bg = BLUE

        return

    def pos(self):
        return self.x,self.y

    def calculate_moves(self,boardstate):
        self.moves = self._calculate_moves(boardstate)
        return self.moves

    def move(self,x,y):
        self.x = x
        self.y = y
        self.in_play = True

    def symbol(self) -> str:
        symbol = piece_symbol(self.piece_type)
        return symbol.upper() if self.white else symbol

    def __repr__(self) -> str:
        return f"{self.symbol()!r}"

    def __str__(self) -> str:
        return self.symbol()

    def ui_reset_color(self):
        self.ui_color_fill = self._ui_color_fill
        self.ui_color_inner_edge = self._ui_color_inner_edge
        self.ui_color_outer_edge = self._ui_color_outer_edge

    def _moves_queen(self, board_all):
        bs = board_all.shape[0]
        if self.level == 0:
            moves = self.bitmap(bs,self.y+1,self.x+1)
            moves = self.bitmap_get_neighbors(moves)
            board_connected = self.bitmap_of_connected_graph_positions(board_all)
            moves = moves & board_connected # Only moves next to other pieces
            moves = moves & ~board_all # Not allowed to move onto other pieces
            moves = self.remove_chokepoint_moves(moves,self.y+1,self.x+1,board_all)
        else:
            moves = None
        return moves

    def _moves_beetle(self, board_all):
        bs = board_all.shape[0]
        if self.level == 0:
            moves = self.bitmap(bs,self.y+1,self.x+1)
            moves = self.bitmap_get_neighbors(moves)
            if self.pieces_under == 0:
                board_connected = self.bitmap_of_connected_graph_positions(board_all)
                moves = moves & board_connected # Only moves next to other pieces
        else:
            moves = None
        return moves

    def bitmap(self,size,row,col):
        """
        Creates a Tensor bitmap board and inserts True on the (row,col) position
        :param size:
        :param row:
        :param col:
        :return:
        """
        board_state = torch.zeros(size,size,dtype=torch.bool)
        board_state[row,col] = True
        return board_state
    def bitmap_get_neighbors(self, board):
        board1 = torch.roll(board,1,dims=0)
        board2 = torch.roll(board,1,dims=1)
        board3 = torch.roll(board,-1,dims=0)
        board4 = torch.roll(board,-1,dims=1)
        board5 = torch.roll(board1,-1,dims=1)
        board6 = torch.roll(board3,1,dims=1)
        board_nn = board1 | board2 | board3 | board4 | board5 | board6
        return board_nn

    def remove_chokepoint_moves(self,moves,row,col,board_all):
        bs = board_all.shape[0]
        bit_nn_piece = self.bitmap_get_neighbors(self.bitmap(bs,row,col))
        move_indices = moves.nonzero().tolist()
        for row_move, col_move in move_indices:
            bit_nn_move = self.bitmap_get_neighbors(self.bitmap(bs, row_move, col_move))
            bit_choke_pos = bit_nn_piece & bit_nn_move
            bit_colisions = board_all & bit_choke_pos
            if bit_colisions.sum() == 2:
                moves[row_move,col_move] = False
        return moves

    def bitmap_of_connected_graph_positions(self,board_all):
        board_all_except_piece = board_all.clone()
        board_all_except_piece[self.y + 1, self.x + 1] = False
        board_nn = self.bitmap_get_neighbors(board_all_except_piece) | board_all_except_piece
        return board_nn



class Hive():
    """
    Creates a single hive containing all the pieces for 1 player.
    """
    def __init__(self, white):
        self.pieces = []
        for i,piece in enumerate(PIECES_PER_PLAYER):
            x = -2 + (not white) * (2*len(PIECES_PER_PLAYER)+5)
            self.pieces.append(Piece(white, piece_id(piece),x,i))
        self.played_piece = False
        self.played_queen = False
        self.played_all_pieces = False
        self.ui_color_fill = PLAYER1_SEL if white else PLAYER2_SEL
        self.white = white
        self.lost = False
        return

    def __repr__(self) -> str:
        return f"{'white' if self.white else 'black'!r}"

    def __str__(self) -> str:
        return f"{'white' if self.white else 'black'}"


    def __iter__(self):
        yield from self.pieces

    def __len__(self):
        return len(self.pieces)

    def __getitem__(self, item):
        return self.pieces[item]

    def check_played_all(self):
        self.played_all_pieces = True
        for piece in self.pieces:
            if not piece.in_play:
                self.played_all_pieces = False
                break

    def move_piece(self,idx:int,x:int,y:int):
        piece = self.pieces[idx]
        if piece.in_play:
            check_played_all=False
        else:
            check_played_all=True
        piece.move(x,y)
        self.played_piece = True
        if check_played_all:
            self.check_played_all()
        if piece.symbol().lower() == 'q':
            self.played_queen = True

    def ui_reset_color(self):
        for piece in self.pieces:
            piece.ui_reset_color()

    def ui_set_color_fill(self,idx):
        self.pieces[idx].ui_color_fill = self.ui_color_fill


class HiveGame:
    def __init__(self):
        self.hive_white = Hive(white=True)
        self.hive_black = Hive(white=False)
        self.hives = [self.hive_white, self.hive_black]
        self.turn = 1
        self.whites_turn = True
        self.board_size = len(self.hive_white) + len(self.hive_black) + 2
        self.ui_active = False
        self.ui_selected = None
        self.ui_hovered = None
        self.ui_update = False
        self.winner = None
        return

    def __iter__(self):
        yield from self.hives

    def __len__(self):
        return len(self.hives)

    def __getitem__(self, item):
        return self.hives[item]


    def hive_player(self):
        return self.hive_white if self.whites_turn else self.hive_black

    def hive_opp(self):
        return self.hive_black if self.whites_turn else self.hive_white

    def shift_pieces_from_edges(self):
        hive = self.hive_player()
        end = self.board_size - 1
        dx = 0
        dy = 0
        piece = hive[self.ui_selected]
        if piece.in_play:
            if piece.x == 0:
                dx += 1
            elif piece.x == end:
                dx -= 1
            if piece.y == 0:
                dy += 1
            elif piece.y == end:
                dy -= 1
        if dx != 0 or dy != 0:
            for piece in self.hive_white:
                if piece.in_play:
                    piece.x += dx
                    piece.y += dy
            for piece in self.hive_black:
                if piece.in_play:
                    piece.x += dx
                    piece.y += dy
        return

    def next_player(self):
        self.generate_board_state()
        game_over = self.check_winners()
        if game_over:
            if self.hive_white.lost and self.hive_black.lost:
                self.winner = 'Draw'
            else:
                self.winner = 'Black' if self.hive_white.lost else 'White'
            return
        self.shift_pieces_from_edges()
        self.whites_turn = not self.whites_turn
        if self.whites_turn:
            self.turn += 1

    def check_winners(self):
        game_over = False
        for hive in self.hives:
            for piece in hive:
                if str(piece).lower() == 'q' and piece.in_play:
                    qmap = self.bitmap(piece.y+1,piece.x+1)
                    nn_qmap = self.bitmap_get_neighbors(qmap)
                    bitmap_overlaps = nn_qmap & self.board_state
                    if len(bitmap_overlaps.nonzero()) == 6:
                        hive.lost = True
                        game_over = True
        return game_over


    def level_pieces(self, x_org, y_org, x_dst, y_dst):
        """
        This routine shifts all piece levels up 1 in (x_org,y_org) to a maximum of 0,
        and shifts every level down 1 in (x_dst,y_dst).
        This routine should be called whenever a beetle is about to move, from (x_org,y_org)->(x_dst,y_dst),
        but before it has actually moved.
        :param x_org:
        :param y_org:
        :param x_dst:
        :param y_dst:
        :return:
        """
        pieces_lowered = 0
        for hive in self.hives:
            for piece in hive:
                if piece.x == x_org and piece.y == y_org and piece.level < 0:
                    piece.level += 1
                elif piece.x == x_dst and piece.y == y_dst:
                    piece.level -= 1
                    pieces_lowered += 1
        return pieces_lowered

    def move_piece(self,idx:int,x:int,y:int):
        hive = self.hive_player()
        piece = hive[idx]
        if str(piece).lower() == 'b':
            piece.pieces_under = self.level_pieces(piece.x,piece.y,x,y)
        hive.move_piece(idx,x,y)
        self.next_player()

    def moves(self,idx:int):
        hive = self.hive_player()
        return hive[idx].moves

    def ui_hover(self, idx: int):
        hive = self.hive_player()
        if idx == self.ui_hovered:  # Nothing has changed
            return
        if self.ui_hovered is not None:  # Remove old hovered hex
            hive.pieces[self.ui_hovered].ui_color_inner_edge = hive.pieces[self.ui_hovered]._ui_color_inner_edge
            self.ui_hovered = None
        if idx is not None:  # Set new hovered hex
            hive.pieces[idx].ui_color_inner_edge = BLUE
            self.ui_hovered = idx
        self.ui_update = True

    def ui_reset_board(self):
        for hive in self.hives:
            hive.ui_reset_color()
        self.ui_selected = None
        self.ui_hovered = None
        self.ui_update = True

    def ui_reset_color(self):
        hive = self.hive_player()
        hive.ui_reset_color()

    def ui_set_color_fill(self,idx:int):
        hive = self.hive_player()
        hive.ui_set_color_fill(idx)

    def ui_unselect_piece(self):
        self.ui_reset_color()
        self.ui_selected = None
        self.ui_update = True

    def ui_select_piece(self, idx: int):
        self.ui_set_color_fill(idx)
        self.ui_selected = idx
        # self.ui_highlight_pieces()
        self.ui_update = True

    def generate_board_state(self):
        self.board_state = self.generate_bitmap_board_state()
        for hive in self.hives:
            for piece in hive:
                if piece.in_play and piece.level == 0:
                    self.board_state[piece.y+1, piece.x+1] = True

    def generate_legal_moves(self):
        hive_player = self.hive_player()
        hive_opp = self.hive_opp()

        # board_state_player = self.generate_clean_board_state()
        board_state_player = self.generate_bitmap_board_state()
        board_state_opp = self.generate_bitmap_board_state()
        #First we generate a list of pieces already on the board
        for piece in hive_player:
            if piece.in_play and piece.level == 0:
                board_state_player[piece.y+1, piece.x+1] = True
        for piece in hive_opp:
            if piece.in_play and piece.level == 0:
                board_state_opp[piece.y+1, piece.x+1] = True
        self.board_state = board_state_player | board_state_opp

        if hive_player.played_all_pieces: # Generate list of spawn locations
            spawn_locations = None
        else:
            if hive_player.played_piece:
                board1 = self.get_neighboring_pos(board_state_player)
                board2 = self.get_neighboring_pos(board_state_opp)
                spawn_locations = board1 & (~ (board2 | board_state_opp))
            else:
                if hive_opp.played_piece:
                    spawn_locations = self.get_neighboring_pos(board_state_opp)
                else:
                    spawn_locations = self.generate_bitmap_board_state(default_state=True)

        #Then we go through each piece and see where it can move to
        if not hive_player.played_queen and self.turn >= 4:
            for piece in hive_player:
                if str(piece).lower() == 'q':
                    piece.moves = spawn_locations
                else:
                    piece.moves = None
        else:
            g, nodes = self.generate_graph(self.board_state[1:-1,1:-1])
            moveable_node_indices = self.find_moveable_nodes(g)
            moveable_positions = nodes[moveable_node_indices].tolist()
            has_moveable_pieces = False
            for piece in hive_player:
                if piece.in_play is False:
                    piece.moves = spawn_locations
                elif piece.level == 0  and ([piece.y,piece.x] in moveable_positions or piece.pieces_under > 0):
                    piece.moves = piece.calculate_moves(self.board_state)
                else:
                    piece.moves = None
                if piece.moves is not None and not has_moveable_pieces:
                    if len(piece.moves.nonzero()) > 0:
                        has_moveable_pieces = True
            if not has_moveable_pieces:
                self.next_player()
                self.generate_legal_moves()
        return

    def generate_clean_board_state(self):
        board_state = torch.zeros(self.board_size+2,self.board_size+2,dtype=torch.int8)
        return board_state

    def generate_bitmap_board_state(self,default_state=False):
        if default_state:
            board_state = torch.ones(self.board_size+2,self.board_size+2,dtype=torch.bool)
            board_state[0,:] = False
            board_state[-1,:] = False
            board_state[:,0] = False
            board_state[:,-1] = False
        else:
            board_state = torch.zeros(self.board_size+2,self.board_size+2,dtype=torch.bool)
        return board_state


    def get_neighboring_pos(self, board):
        board1 = torch.roll(board,1,dims=0)
        board2 = torch.roll(board,1,dims=1)
        board3 = torch.roll(board,-1,dims=0)
        board4 = torch.roll(board,-1,dims=1)
        board5 = torch.roll(board1,-1,dims=1)
        board6 = torch.roll(board3,1,dims=1)
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

    def generate_graph(self,board_state):
        node_indices = board_state.nonzero()
        nodes = len(node_indices)
        # node_indices_axial = self.offset_to_axial(node_indices)
        node_pairs = list(itertools.combinations(node_indices, 2))
        distances = self.axial_distance(node_pairs)
        M = distances < 1.1
        node_combinations = torch.combinations(torch.arange(nodes),2)
        edges = node_combinations[M]
        g = ig.Graph(nodes,edges.tolist())

        return g,node_indices

    def find_moveable_nodes(self,g):
        edges = torch.as_tensor(g.get_edgelist())
        nodes = g.vcount()
        bridges = g.bridges()
        degrees = g.degree()
        bridge_nodes = edges[bridges].unique().tolist()
        leaf_nodes = [i for i,degree in enumerate(degrees) if degree==1]
        moveable_node_indices = set(range(nodes)).difference(bridge_nodes)
        moveable_node_indices.update(leaf_nodes)
        return list(moveable_node_indices)


    def offset_to_axial(self,hexes:torch.Tensor):
        n_nodes,_ = hexes.shape
        cols = hexes[:,0]
        rows = hexes[:,1]
        axial = torch.empty_like(hexes)
        axial[:,0] = cols - (rows - (rows&1)) / 2
        axial[:,1] = rows
        return axial

    def axial_distance(self,hexes_pair:torch.Tensor):
        dists = []
        for a,b in hexes_pair:
            dist = (torch.abs(a[0]-b[0]) + torch.abs(a[0] + a[1] - b[0] - b[1]) + torch.abs(a[1] - b[1])) / 2
            dists.append(dist)
        dists = torch.as_tensor(dists)
        return dists

    def bitmap(self,row,col):
        """
        Creates a Tensor bitmap board and inserts True on the (row,col) position
        :param size:
        :param row:
        :param col:
        :return:
        """
        board_state = torch.zeros(self.board_size+2,self.board_size+2,dtype=torch.bool)
        board_state[row,col] = True
        return board_state
    def bitmap_get_neighbors(self, board):
        board1 = torch.roll(board,1,dims=0)
        board2 = torch.roll(board,1,dims=1)
        board3 = torch.roll(board,-1,dims=0)
        board4 = torch.roll(board,-1,dims=1)
        board5 = torch.roll(board1,-1,dims=1)
        board6 = torch.roll(board3,1,dims=1)
        board_nn = board1 | board2 | board3 | board4 | board5 | board6
        return board_nn


def generate_bitmap_board_state(size,default_state=False):
    if default_state:
        board_state = torch.ones(size,size,dtype=torch.bool)
        board_state[0,:] = False
        board_state[-1,:] = False
        board_state[:,0] = False
        board_state[:,-1] = False
    else:
        board_state = torch.zeros(size,size,dtype=torch.bool)
    return board_state

def viz_graph():
    print(bridges)
    print(degrees)
    g['title'] = 'test'
    names = list(range(nodes))
    names = [str(i) for i in names]
    g.vs["name"] = names

    # import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 5))
    ig.plot(
        g,
        target=ax,
        layout="circle",  # print nodes in a circular layout
        vertex_size=0.1,
        # vertex_color=["steelblue" if gender == "M" else "salmon" for gender in g.vs["gender"]],
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        vertex_label=g.vs["name"],
        # vertex_label_size=7.0,
        # edge_width=[2 if married else 1 for married in g.es["married"]],
        # edge_color=["#7142cf" if married else "#AAA" for married in g.es["married"]]
    )

    plt.show()

