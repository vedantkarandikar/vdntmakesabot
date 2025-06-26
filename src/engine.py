import chess
import chess.polyglot
import concurrent.futures
import time
from typing import Tuple


def _evaluate_move_worker(fen: str, depth: int, move_uci: str) -> Tuple[str, float]:
    """
    Re-creates the board from FEN, pushes the move, then runs a
    depth-(depth-1) negamax.  Returns (uci, score).
    """
    board = chess.Board(fen)
    board.push_uci(move_uci)

    engine = MyEngine()
    score = -engine.negamax(board, depth - 1)
    return move_uci, score


class MyEngine:
    def __init__(self):
        self.transposition_table = {}

    def best_move(
        self,
        board: chess.Board,
        depth: int = 4,
        max_time: float | None = 30,
        workers: int = 8,
    ) -> chess.Move:

        try:
            with chess.polyglot.open_reader("book/openings.bin") as rdr:
                return rdr.find(board).move
        except IndexError:
            pass

        start = time.time()
        deadline = start + (max_time or float("inf"))
        best_move, best_score = None, float("-inf")

        fen = board.fen()
        legal = list(board.legal_moves)

        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
            fut_to_move = {
                ex.submit(_evaluate_move_worker, fen, depth, m.uci()): m for m in legal
            }

            try:
                for fut in concurrent.futures.as_completed(
                    fut_to_move, timeout=max(0.0, deadline - time.time())
                ):
                    move_uci, score = fut.result()
                    move = fut_to_move[fut]

                    if score > best_score:
                        best_move, best_score = move, score

                    if time.time() >= deadline:
                        break

            except concurrent.futures.TimeoutError:
                pass
            finally:
                for fut in fut_to_move:
                    if not fut.done():
                        fut.cancel()

        return best_move or chess.Move.null()

    def negamax(self, board: chess.Board, depth: int) -> float:
        key = chess.polyglot.zobrist_hash(board)
        if key in self.transposition_table:
            cached_d, cached_s = self.transposition_table[key]
            if cached_d >= depth:
                return cached_s

        if depth == 0 or board.is_game_over():
            score = self.eval(board)
            self.transposition_table[key] = (depth, score)
            return score

        best = float("-inf")
        for mv in board.legal_moves:
            board.push(mv)
            best = max(best, -self.negamax(board, depth - 1))
            board.pop()

        self.transposition_table[key] = (depth, best)
        return best

    @staticmethod
    def evaluate_move(board: chess.Board, depth: int, move: chess.Move):
        temp = board.copy()
        temp.push(move)
        score = -MyEngine().negamax(temp, depth - 1)
        return move, score

    def piece_value(self, board: chess.Board, piece: chess.Piece) -> int:
        piece_values = {
            chess.PAWN: 1000,
            chess.KNIGHT: 3200,
            chess.BISHOP: 3300,
            chess.ROOK: 5000,
            chess.QUEEN: 9000,
            chess.KING: 30000,
        }
        return piece_values.get(piece.piece_type, 0) * (
            1 if piece.color == board.turn else -1
        )

    def eval(self, board: chess.Board) -> float:
        valuation = sum(
            self.piece_value(board, piece) for piece in board.piece_map().values()
        )

        if board.is_checkmate():
            return float("-inf") if board.turn == chess.WHITE else float("inf")

        if (
            board.is_stalemate()
            or board.is_insufficient_material()
            or board.is_seventyfive_moves()
            or board.is_fivefold_repetition()
            or board.is_variant_draw()
        ):
            return 0.0

        if board.is_check():
            valuation -= 500

        if board.has_castling_rights(chess.WHITE):
            valuation += 200
        if board.has_castling_rights(chess.BLACK):
            valuation -= 200

        for square, piece in board.piece_map().items():
            mobility = 0
            if piece.piece_type in {chess.BISHOP, chess.ROOK}:
                for attack_square in board.attacks(square):
                    blocker = board.piece_at(attack_square)
                    if blocker:
                        if blocker.color == piece.color or board.is_attacked_by(
                            blocker.color, attack_square
                        ):
                            break
                    mobility += 1
            valuation += mobility * (10 if piece.color == chess.WHITE else -10)

        return valuation / 1000
