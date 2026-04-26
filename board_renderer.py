"""
board_renderer.py — Generates highlighted SVG chess boards via python-chess.
"""
from __future__ import annotations

from typing import Optional
import chess
import chess.svg


def render_board(
    board: chess.Board,
    selected_square: Optional[chess.Square] = None,
    legal_moves: Optional[list[chess.Move]] = None,
    last_move: Optional[chess.Move] = None,
    flipped: bool = False,
    size: int = 480,
) -> str:
    """
    Render the board as an SVG string with visual highlights.

    Args:
        board: Current chess.Board state.
        selected_square: Square the player has clicked (highlighted in blue).
        legal_moves: Legal destinations for selected piece (green dots).
        last_move: Most recent move (orange highlight).
        flipped: If True, board shown from Black's perspective.
        size: SVG pixel dimensions.

    Returns:
        SVG markup string wrapped in a centered div.
    """
    arrows: list[chess.svg.Arrow] = []
    squares = chess.SquareSet()
    fill: dict[chess.Square, str] = {}

    # Highlight last move
    if last_move:
        fill[last_move.from_square] = "#f6a14044"
        fill[last_move.to_square] = "#f6a14066"

    # Highlight selected square
    if selected_square is not None:
        fill[selected_square] = "#4a90d966"

    # Highlight legal move targets
    if legal_moves:
        for move in legal_moves:
            squares.add(move.to_square)

    svg_str = chess.svg.board(
        board=board,
        squares=squares,
        fill=fill,
        lastmove=last_move,
        flipped=flipped,
        size=size,
        style=_custom_css(),
    )

    return f"""
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        filter: drop-shadow(0 8px 32px rgba(0,0,0,0.6));
    ">
        {svg_str}
    </div>
    """


def _custom_css() -> str:
    """Custom CSS injected into the SVG to style board colors."""
    return """
    .square.light { fill: #f0d9b5; }
    .square.dark  { fill: #b58863; }
    .square.light.lastmove { fill: #f6f66e; }
    .square.dark.lastmove  { fill: #baca2b; }
    .square.light.check    { fill: #ff6b6b; }
    .square.dark.check     { fill: #cc4444; }
    """


def get_captured_pieces(board: chess.Board) -> dict[str, list[str]]:
    """
    Calculate pieces captured by each side based on board state.

    Returns:
        Dict with 'white' and 'black' keys containing lists of piece unicode symbols.
    """
    piece_counts_start = {
        chess.PAWN: 8,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 2,
        chess.QUEEN: 1,
    }

    piece_unicode = {
        chess.WHITE: {
            chess.PAWN: "♙", chess.KNIGHT: "♘", chess.BISHOP: "♗",
            chess.ROOK: "♖", chess.QUEEN: "♕",
        },
        chess.BLACK: {
            chess.PAWN: "♟", chess.KNIGHT: "♞", chess.BISHOP: "♝",
            chess.ROOK: "♜", chess.QUEEN: "♛",
        },
    }

    captured: dict[str, list[str]] = {"white": [], "black": []}

    for piece_type, start_count in piece_counts_start.items():
        white_on_board = len(board.pieces(piece_type, chess.WHITE))
        black_on_board = len(board.pieces(piece_type, chess.BLACK))

        white_captured = start_count - black_on_board  # White captured Black's pieces
        black_captured = start_count - white_on_board  # Black captured White's pieces

        for _ in range(max(0, white_captured)):
            captured["white"].append(piece_unicode[chess.BLACK][piece_type])
        for _ in range(max(0, black_captured)):
            captured["black"].append(piece_unicode[chess.WHITE][piece_type])

    return captured


def format_move_history(board: chess.Board) -> list[str]:
    """
    Generate move history in standard algebraic notation (SAN).

    Returns:
        List of formatted move strings like ['1. e4 e5', '2. Nf3 Nc6', ...].
    """
    moves_san: list[str] = []
    temp_board = chess.Board()

    san_moves: list[str] = []
    for move in board.move_stack:
        san_moves.append(temp_board.san(move))
        temp_board.push(move)

    rows: list[str] = []
    for i in range(0, len(san_moves), 2):
        move_num = i // 2 + 1
        white = san_moves[i]
        black = san_moves[i + 1] if i + 1 < len(san_moves) else "..."
        rows.append(f"{move_num}. {white} {black}")

    return rows


def get_game_status(board: chess.Board) -> tuple[str, str]:
    """
    Determine current game status.

    Returns:
        Tuple of (status_label, color) for UI display.
        color is one of: 'green', 'red', 'orange', 'blue', 'gray'
    """
    if board.is_checkmate():
        winner = "Putih" if board.turn == chess.BLACK else "Hitam"
        return f"♚ Skak Mat! {winner} Menang!", "red"
    elif board.is_stalemate():
        return "🤝 Stalemate — Seri!", "orange"
    elif board.is_insufficient_material():
        return "🤝 Materi Tidak Cukup — Seri!", "orange"
    elif board.is_seventyfive_moves():
        return "🤝 75 Move Rule — Seri!", "orange"
    elif board.is_fivefold_repetition():
        return "🤝 Lima Pengulangan — Seri!", "orange"
    elif board.is_check():
        turn = "Putih" if board.turn == chess.WHITE else "Hitam"
        return f"⚠️ Skak! Giliran {turn}", "yellow"
    else:
        turn = "⬜ Giliran Putih" if board.turn == chess.WHITE else "⬛ Giliran Hitam"
        return turn, "green"
