import typing


PieceType = int
PIECE_TYPES = [QUEEN, BEETLE, GRASSHOPPER, SPIDER, ANT] = range(1,6)

PIECE_SYMBOLS = ["q", "b", "g", "s", "a"]
PIECE_NAMES = ["queen", "beetle", "grasshopper", "spider", "ant"]

PIECES_PER_PLAYER = ["q","b"]

def moves_queen(boardstate,level,position):
    if level == 0:
        moves = get_neighbors(position)
        moves = remove_already_occupied(moves,boardstate)
        moves = remove_too_narrow_passage(moves,boardstate)
        moves = remove_cut_graph_moves(moves)
    else:
        moves = None
    return moves

def moves_beetle(boardstate,level,position):
    if level == 0:
        moves = get_neighbors(position)
        moves = remove_already_occupied(moves,boardstate)
        moves = remove_too_narrow_passage(moves,boardstate)
        moves = remove_cut_graph_moves(moves)
    else:
        moves = None
    return moves



def piece_symbol(piece_type: PieceType) -> str:
    return typing.cast(str, PIECE_SYMBOLS[piece_type])

def piece_name(piece_type: PieceType) -> str:
    return typing.cast(str, PIECE_NAMES[piece_type])

def piece_id(piece_type: PieceType) -> int:
    return PIECE_SYMBOLS.index(piece_type)

class Piece:
    """A piece with type and color."""

    def __init__(self,color:bool ,piece_type:int):
        self.level = 0
        self.pos = (-1, -1)
        self.in_play = False
        self.color = color
        self.piece_type = piece_type
        self.moves = None

        self._calculate_moves = eval(f"moves_{piece_name(piece_type)}")
        return

    def calculate_moves(self,boardstate):
        moves = self._calculate_moves(boardstate, self.level, self.pos)
        return moves


    def symbol(self) -> str:
        symbol = piece_symbol(self.piece_type)
        return symbol.upper() if self.color else symbol

    def __repr__(self) -> str:
        return f"{self.symbol()!r}"

    def __str__(self) -> str:
        return self.symbol()


class Hive():
    """
    Creates a single hive containing all the pieces for 1 player.
    """
    def __init__(self,color):
        self.pieces = []
        for piece in PIECES_PER_PLAYER:
            self.pieces.append(Piece(color,piece_id(piece)))
        self.played_piece = False
        self.played_queen = False
        self.played_all_pieces = False
        return

    def __iter__(self):
        yield from self.pieces

    def __len__(self):
        return len(self.pieces)

    def __getitem__(self, item):
        return self.pieces[item]




class HiveGamePieces():
    def __init__(self):
        self.hive_white = Hive(color=True)
        self.hive_black = Hive(color=False)
        return

