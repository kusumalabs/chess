"""
chess_engine.py — Stockfish wrapper with ELO-based strength control.
"""
from __future__ import annotations

import subprocess
import threading
import time
from typing import Optional

import chess

# ELO presets mapped to Stockfish UCI parameters
ELO_PRESETS: dict[str, int] = {
    "🐣 Pemula (400)": 400,
    "🌱 Dasar (800)": 800,
    "⚔️ Menengah (1200)": 1200,
    "🏆 Mahir (1600)": 1600,
    "🔥 Expert (2000)": 2000,
    "💎 Master (2400)": 2400,
    "🤖 Stockfish Max (2800+)": 2850,
}

STOCKFISH_PATHS = [
    "/usr/games/stockfish",
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    "stockfish",
]


def find_stockfish() -> Optional[str]:
    """Detect Stockfish binary path across platforms."""
    for path in STOCKFISH_PATHS:
        try:
            result = subprocess.run(
                [path], input="quit\n", capture_output=True,
                text=True, timeout=3
            )
            if result.returncode == 0 or "Stockfish" in (result.stdout + result.stderr):
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


class StockfishEngine:
    """
    Manages a persistent Stockfish subprocess.
    Supports ELO limiting via UCI_LimitStrength / UCI_Elo.
    """

    def __init__(self, path: str, elo: int = 1200) -> None:
        self._path = path
        self._elo = elo
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._start()

    def _start(self) -> None:
        self._proc = subprocess.Popen(
            [self._path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._send("uci")
        self._wait_for("uciok")
        self._apply_elo(self._elo)
        self._send("isready")
        self._wait_for("readyok")

    def _send(self, cmd: str) -> None:
        if self._proc and self._proc.stdin:
            self._proc.stdin.write(cmd + "\n")
            self._proc.stdin.flush()

    def _wait_for(self, token: str, timeout: float = 5.0) -> list[str]:
        lines: list[str] = []
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._proc and self._proc.stdout:
                line = self._proc.stdout.readline().strip()
                if line:
                    lines.append(line)
                if token in line:
                    break
        return lines

    def _apply_elo(self, elo: int) -> None:
        if elo >= 2800:
            # Full strength — no limiting
            self._send("setoption name UCI_LimitStrength value false")
            self._send("setoption name Skill Level value 20")
        else:
            self._send("setoption name UCI_LimitStrength value true")
            self._send(f"setoption name UCI_Elo value {elo}")

    def set_elo(self, elo: int) -> None:
        """Dynamically update engine strength."""
        with self._lock:
            self._elo = elo
            self._apply_elo(elo)

    def get_best_move(self, board: chess.Board, movetime_ms: int = 1500) -> Optional[chess.Move]:
        """
        Ask Stockfish for the best move given board position.
        Returns a chess.Move or None if engine fails.
        """
        with self._lock:
            fen = board.fen()
            self._send(f"position fen {fen}")
            self._send(f"go movetime {movetime_ms}")
            lines = self._wait_for("bestmove", timeout=movetime_ms / 1000 + 3)

        for line in reversed(lines):
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2 and parts[1] != "(none)":
                    try:
                        return chess.Move.from_uci(parts[1])
                    except ValueError:
                        return None
        return None

    def quit(self) -> None:
        """Gracefully terminate the engine subprocess."""
        try:
            self._send("quit")
            if self._proc:
                self._proc.wait(timeout=3)
        except Exception:
            if self._proc:
                self._proc.kill()
