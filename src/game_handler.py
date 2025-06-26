# File: src/game_handler.py
import chess
from engine import MyEngine
from lichess_client.client import LichessBotClient
from lichess_client.models.base import GameColor
from lichess_client.models.game import GameFullEvent, GameStateEvent

class GameHandler:
    def __init__(self, lichess: LichessBotClient, engine: MyEngine):
        self.lichess = lichess
        self.engine = engine
        self.username = "vdntmakesabot"

    def handle_game(self, game_id: str):
        print("Handling game:", game_id)
        board = chess.Board()
        my_color: GameColor | None = None

        with self.lichess.get_game_stream(game_id) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                event = self.lichess._parse_ndjson_line(line)
                if isinstance(event, GameFullEvent):
                    moves = event.state.moves.split()
                    for move in moves:
                        board.push_uci(move)

                    my_color = (
                        GameColor.white
                        if event.white["id"] == self.username
                        else GameColor.black
                    )

                    if my_color == GameColor.white and board.turn == chess.WHITE:
                        self.play_move(game_id, board)

                elif isinstance(event, GameStateEvent):
                    board = chess.Board()
                    moves = event.moves.split()
                    for move in moves:
                        board.push_uci(move)

                    if my_color:
                        is_my_turn = (
                            my_color == GameColor.white and board.turn == chess.WHITE
                        ) or (my_color == GameColor.black and board.turn == chess.BLACK)
                        if is_my_turn:
                            self.play_move(game_id, board)

    def play_move(self, game_id: str, board: chess.Board):
        move = self.engine.best_move(board)
        if not bool(move):
            print(f"[{game_id}] No legal move found, game finished")
            return

        uci_move = move.uci()
        print(f"[{game_id}] Playing move {uci_move}")
        self.lichess.make_move(game_id, uci_move)
