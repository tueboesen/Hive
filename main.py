import logging

from rich import print
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])
logging.getLogger().setLevel(logging.INFO)
from classes.tournament import Tournament


def main(args):
    arena = Tournament(args)

    if MODE=="cpu_vs_cpu":
        arena.championship()
    if MODE=="man_vs_cpu":
        arena.single_game()


if __name__ == "__main__":
    BOARD_SIZE = 22
    ITERMAX = 500
    MODE = "man_vs_cpu"
    GAME_COUNT, N_GAMES = 0, 200

    if MODE == "man_vs_cpu":
        log = logging.getLogger("rich")

        log.info("You will be playing as the white player!")
        print()

    args = BOARD_SIZE, ITERMAX, MODE, GAME_COUNT, N_GAMES
    main(args)

