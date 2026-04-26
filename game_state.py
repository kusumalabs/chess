"""
game_state.py — Session state management for the Streamlit chess app.
"""
from __future__ import annotations

import time
from typing import Optional

import chess
import streamlit as st

from chess_engine import ELO_PRESETS, StockfishEngine, find_stockfish


def init_state() -> None:
    """
    Initialize all session_state keys on first load.
    Idempotent — safe to call on every rerun.
    """
    defaults: dict = {
        "board": chess.Board(),
        "selected_square": None,
        "legal_moves": [],
        "last_move": None,
        "flipped": False,
        "elo_label": "⚔️ Menengah (1200)",
        "engine": None,
        "stockfish_path": find_stockfish(),
        "game_over": False,
        "thinking": False,
        # Timer state
        "white_time": 600.0,   # 10 minutes default
        "black_time": 600.0,
        "last_tick": time.time(),
        "timer_active": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_engine() -> Optional[StockfishEngine]:
    """
    Return cached engine or create a new one.
    Returns None if Stockfish is not found.
    """
    if st.session_state.stockfish_path is None:
        return None

    if st.session_state.engine is None:
        elo = ELO_PRESETS[st.session_state.elo_label]
        try:
            st.session_state.engine = StockfishEngine(
                st.session_state.stockfish_path, elo=elo
            )
        except Exception:
            st.session_state.stockfish_path = None
            return None

    return st.session_state.engine


def new_game() -> None:
    """Reset board and all transient state for a fresh game."""
    if st.session_state.engine:
        st.session_state.engine.quit()
        st.session_state.engine = None

    st.session_state.board = chess.Board()
    st.session_state.selected_square = None
    st.session_state.legal_moves = []
    st.session_state.last_move = None
    st.session_state.game_over = False
    st.session_state.thinking = False
    st.session_state.white_time = 600.0
    st.session_state.black_time = 600.0
    st.session_state.last_tick = time.time()
    st.session_state.timer_active = False


def undo_move() -> None:
    """
    Undo the last two half-moves (player + AI response).
    If only one move made, undo just that one.
    """
    board: chess.Board = st.session_state.board
    if len(board.move_stack) == 0:
        return

    board.pop()  # Undo AI move
    if len(board.move_stack) > 0:
        board.pop()  # Undo player move

    st.session_state.selected_square = None
    st.session_state.legal_moves = []
    st.session_state.last_move = board.peek() if board.move_stack else None
    st.session_state.game_over = False


def handle_square_click(square: chess.Square) -> Optional[chess.Move]:
    """
    Handle player click on a board square.
    Returns the move if one was completed, else None.

    State machine:
        1. No selection → select piece (if player's piece)
        2. Square selected → try to move to clicked square
           a. Legal move → execute and return move
           b. Own piece clicked → re-select
           c. Empty/illegal → deselect
    """
    board: chess.Board = st.session_state.board

    # Player always plays White
    if board.turn != chess.WHITE or st.session_state.game_over:
        return None

    selected = st.session_state.selected_square

    if selected is None:
        # First click: select piece
        piece = board.piece_at(square)
        if piece and piece.color == chess.WHITE:
            st.session_state.selected_square = square
            st.session_state.legal_moves = [
                m for m in board.legal_moves if m.from_square == square
            ]
    else:
        # Second click: attempt move
        move = _find_move(board, selected, square)
        if move:
            board.push(move)
            st.session_state.last_move = move
            st.session_state.selected_square = None
            st.session_state.legal_moves = []
            return move
        else:
            # Re-select if clicked another own piece
            piece = board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                st.session_state.selected_square = square
                st.session_state.legal_moves = [
                    m for m in board.legal_moves if m.from_square == square
                ]
            else:
                st.session_state.selected_square = None
                st.session_state.legal_moves = []

    return None


def _find_move(
    board: chess.Board,
    from_sq: chess.Square,
    to_sq: chess.Square,
) -> Optional[chess.Move]:
    """
    Find a legal move from from_sq to to_sq.
    Handles pawn promotion (auto-promotes to Queen).
    """
    for move in board.legal_moves:
        if move.from_square == from_sq and move.to_square == to_sq:
            # Auto-promote pawn to queen
            if move.promotion is not None:
                return chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
            return move
    return None


def tick_timer() -> None:
    """Update the active player's clock based on elapsed wall time."""
    if not st.session_state.timer_active or st.session_state.game_over:
        return

    now = time.time()
    elapsed = now - st.session_state.last_tick
    st.session_state.last_tick = now

    board: chess.Board = st.session_state.board
    if board.turn == chess.WHITE:
        st.session_state.white_time = max(0.0, st.session_state.white_time - elapsed)
    else:
        st.session_state.black_time = max(0.0, st.session_state.black_time - elapsed)


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS string."""
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins:02d}:{secs:02d}"
