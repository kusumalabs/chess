"""
app.py — Main Streamlit entry point for the Chess application.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import time

import chess
import streamlit as st

from board_renderer import (
    format_move_history,
    get_captured_pieces,
    get_game_status,
    render_board,
)
from chess_engine import ELO_PRESETS
from game_state import (
    format_time,
    get_engine,
    handle_square_click,
    init_state,
    new_game,
    tick_timer,
    undo_move,
)

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Chess Arena",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --gold: #c9a84c;
    --gold-light: #e8c97a;
    --dark-bg: #0f0e0c;
    --panel-bg: #1a1815;
    --card-bg: #231f1a;
    --border: #3a3228;
    --text: #e8dcc8;
    --text-muted: #8a7a68;
    --green: #4caf50;
    --red: #ef5350;
    --orange: #ff9800;
    --yellow: #ffeb3b;
}

html, body, [data-testid="stApp"] {
    background-color: var(--dark-bg) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stSidebar"] {
    background: var(--panel-bg) !important;
    border-right: 1px solid var(--border) !important;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
}

.stButton > button {
    background: var(--card-bg) !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.4rem 0.8rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: var(--gold) !important;
    color: var(--dark-bg) !important;
    transform: translateY(-1px) !important;
}

.stSelectbox > div > div {
    background: var(--card-bg) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

.stSelectbox label, .stMarkdown {
    color: var(--text) !important;
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    margin: 0.5rem 0;
    border: 1px solid;
    font-family: 'JetBrains Mono', monospace;
}

.status-green  { background:#1a3a1a; color:#4caf50; border-color:#4caf50; }
.status-red    { background:#3a1a1a; color:#ef5350; border-color:#ef5350; }
.status-orange { background:#3a2a0a; color:#ff9800; border-color:#ff9800; }
.status-yellow { background:#2a2a0a; color:#ffeb3b; border-color:#ffeb3b; }
.status-gray   { background:#2a2a2a; color:#888;    border-color:#555;    }

.timer-display {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    text-align: center;
    padding: 0.4rem;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--card-bg);
}

.timer-active {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
    box-shadow: 0 0 8px rgba(201,168,76,0.3);
}

.move-history-box {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.75rem;
    max-height: 300px;
    overflow-y: auto;
    font-size: 0.8rem;
    line-height: 1.8;
}

.captured-display {
    font-size: 1.3rem;
    letter-spacing: 2px;
    min-height: 2rem;
    padding: 0.3rem;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    text-align: center;
}

.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--text-muted) !important;
    margin: 1rem 0 0.4rem 0;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.3rem;
}

.sq-btn button {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    height: 60px !important;
    min-height: 60px !important;
    font-size: 1.8rem !important;
    color: var(--text) !important;
}

.logo-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--gold);
    text-align: center;
    letter-spacing: 1px;
    padding: 0.5rem 0 0.2rem 0;
}

.logo-sub {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 4px;
    color: var(--text-muted);
    text-align: center;
    margin-bottom: 1rem;
}

.no-stockfish {
    background: #3a1a0a;
    border: 1px solid #ff6b35;
    border-radius: 8px;
    padding: 1rem;
    color: #ff9e6b;
    font-size: 0.85rem;
    line-height: 1.6;
}

[data-testid="stHorizontalBlock"] { gap: 0 !important; }

div[data-testid="column"] { padding: 0 !important; }

/* Board click grid */
.board-grid-row {
    display: flex;
    justify-content: center;
}

/* Hide streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── Init ─────────────────────────────────────────────────────────────────────

init_state()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="logo-title">♟ Chess Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="logo-sub">vs Stockfish Engine</div>', unsafe_allow_html=True)

    # Stockfish warning
    if st.session_state.stockfish_path is None:
        st.markdown("""
        <div class="no-stockfish">
        ⚠️ <strong>Stockfish tidak ditemukan!</strong><br><br>
        Install via:<br>
        • Ubuntu/Debian: <code>sudo apt install stockfish</code><br>
        • macOS: <code>brew install stockfish</code><br>
        • Windows: Download dari <a href="https://stockfishchess.org" style="color:#ff9e6b">stockfishchess.org</a><br><br>
        Restart app setelah install.
        </div>
        """, unsafe_allow_html=True)
    else:
        # ELO selector
        st.markdown('<p class="section-header">Level Musuh</p>', unsafe_allow_html=True)
        elo_options = list(ELO_PRESETS.keys())
        selected_elo = st.selectbox(
            "ELO Level",
            elo_options,
            index=elo_options.index(st.session_state.elo_label),
            label_visibility="collapsed",
        )
        if selected_elo != st.session_state.elo_label:
            st.session_state.elo_label = selected_elo
            engine = get_engine()
            if engine:
                engine.set_elo(ELO_PRESETS[selected_elo])

        elo_val = ELO_PRESETS[st.session_state.elo_label]
        st.markdown(
            f'<p style="color:var(--text-muted);font-size:0.75rem;text-align:center;">Rating: '
            f'<span style="color:var(--gold);font-weight:600;">{elo_val}</span> ELO</p>',
            unsafe_allow_html=True,
        )

    # Controls
    st.markdown('<p class="section-header">Kontrol</p>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🆕 Baru", use_container_width=True):
            new_game()
            st.rerun()
    with col_b:
        if st.button("↩ Undo", use_container_width=True):
            undo_move()
            st.rerun()
    with col_c:
        flip_label = "🔄 Flip"
        if st.button(flip_label, use_container_width=True):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()

    # Timers
    st.markdown('<p class="section-header">Waktu</p>', unsafe_allow_html=True)
    board: chess.Board = st.session_state.board
    tick_timer()

    wt = format_time(st.session_state.white_time)
    bt = format_time(st.session_state.black_time)
    w_active = board.turn == chess.WHITE and st.session_state.timer_active and not st.session_state.game_over
    b_active = board.turn == chess.BLACK and st.session_state.timer_active and not st.session_state.game_over

    st.markdown(
        f'<div class="timer-display {"timer-active" if b_active else ""}">⬛ {bt}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="timer-display {"timer-active" if w_active else ""}">⬜ {wt}</div>',
        unsafe_allow_html=True,
    )

    # Game status
    st.markdown('<p class="section-header">Status</p>', unsafe_allow_html=True)
    status_label, status_color = get_game_status(board)
    st.markdown(
        f'<div class="status-badge status-{status_color}">{status_label}</div>',
        unsafe_allow_html=True,
    )

    # Captured pieces
    st.markdown('<p class="section-header">Dimakan</p>', unsafe_allow_html=True)
    captured = get_captured_pieces(board)
    st.markdown(
        f'<div class="captured-display">{" ".join(captured["white"]) or "–"}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.7rem;color:var(--text-muted);text-align:center;margin:2px 0;">oleh Putih &nbsp;|&nbsp; oleh Hitam</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="captured-display">{" ".join(captured["black"]) or "–"}</div>',
        unsafe_allow_html=True,
    )

    # Move history
    st.markdown('<p class="section-header">Riwayat Langkah</p>', unsafe_allow_html=True)
    history = format_move_history(board)
    if history:
        history_html = "<br>".join(
            f'<span style="color:var(--text-muted)">{row.split(".")[0]}.</span>'
            f'<span style="color:var(--text)"> {".".join(row.split(".")[1:])}</span>'
            for row in history
        )
        st.markdown(
            f'<div class="move-history-box">{history_html}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="move-history-box" style="color:var(--text-muted);text-align:center;">Belum ada langkah</div>',
            unsafe_allow_html=True,
        )

# ─── Main Board Area ──────────────────────────────────────────────────────────

board = st.session_state.board
status_label, status_color = get_game_status(board)

# Check game over conditions
if board.is_game_over() or st.session_state.white_time <= 0 or st.session_state.black_time <= 0:
    st.session_state.game_over = True
    st.session_state.timer_active = False

# ── Board SVG Render ─────────────────────────────────────────────────────────

board_svg = render_board(
    board=board,
    selected_square=st.session_state.selected_square,
    legal_moves=st.session_state.legal_moves,
    last_move=st.session_state.last_move,
    flipped=st.session_state.flipped,
    size=520,
)
st.markdown(board_svg, unsafe_allow_html=True)

# ── Interactive Click Grid ────────────────────────────────────────────────────

st.markdown(
    '<p style="text-align:center;color:var(--text-muted);font-size:0.72rem;'
    'letter-spacing:2px;text-transform:uppercase;margin-top:0.5rem;">'
    'Klik kotak untuk memilih & memindahkan bidak</p>',
    unsafe_allow_html=True,
)

if not st.session_state.game_over and board.turn == chess.WHITE and not st.session_state.thinking:
    # Render 8x8 clickable grid aligned to board
    FILES = "abcdefgh"

    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;gap:0;margin-top:4px;">',
        unsafe_allow_html=True,
    )

    ranks = range(7, -1, -1) if not st.session_state.flipped else range(8)
    files = range(8) if not st.session_state.flipped else range(7, -1, -1)

    for rank in ranks:
        cols = st.columns(8, gap="small")
        for file_idx, file in enumerate(files):
            square = chess.square(file, rank)
            piece = board.piece_at(square)

            symbol = ""
            if piece:
                symbol = piece.unicode_symbol(invert_color=False)

            is_selected = st.session_state.selected_square == square
            is_legal_target = any(m.to_square == square for m in st.session_state.legal_moves)

            if is_selected:
                bg = "#4a90d966"
            elif is_legal_target:
                bg = "#4caf5044"
            elif st.session_state.last_move and square in [
                st.session_state.last_move.from_square,
                st.session_state.last_move.to_square,
            ]:
                bg = "#f6a14033"
            else:
                bg = "transparent"

            btn_style = (
                f"background:{bg}!important;border:none!important;"
                f"width:100%!important;height:40px!important;"
                f"cursor:pointer!important;font-size:1.5rem!important;"
                f"color:transparent!important;padding:0!important;"
            )

            with cols[file_idx]:
                btn_key = f"sq_{square}_{id(board)}"
                if st.button(
                    symbol or " ",
                    key=btn_key,
                    help=f"{FILES[file]}{rank+1}",
                ):
                    move_made = handle_square_click(square)
                    if move_made:
                        st.session_state.timer_active = True
                        st.session_state.thinking = True
                        st.rerun()
                    else:
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─── AI Move Logic ────────────────────────────────────────────────────────────

if (
    st.session_state.thinking
    and not st.session_state.game_over
    and board.turn == chess.BLACK
):
    engine = get_engine()
    if engine:
        with st.spinner("♟ Stockfish sedang berpikir..."):
            elo_val = ELO_PRESETS[st.session_state.elo_label]
            # Scale think time by ELO
            movetime = max(300, min(2500, elo_val // 2))
            ai_move = engine.get_best_move(board, movetime_ms=movetime)

        if ai_move and ai_move in board.legal_moves:
            board.push(ai_move)
            st.session_state.last_move = ai_move

    st.session_state.thinking = False

    if board.is_game_over():
        st.session_state.game_over = True
        st.session_state.timer_active = False

    st.rerun()

# ─── Game Over Banner ─────────────────────────────────────────────────────────

if st.session_state.game_over:
    outcome = board.outcome()
    if outcome:
        if outcome.winner == chess.WHITE:
            msg = "🏆 Kamu Menang! Selamat!"
            color = "#4caf50"
        elif outcome.winner == chess.BLACK:
            msg = "💀 Stockfish Menang. Coba lagi!"
            color = "#ef5350"
        else:
            msg = "🤝 Seri! Pertandingan seimbang."
            color = "#ff9800"
    elif st.session_state.white_time <= 0:
        msg = "⏰ Waktu Habis! Stockfish Menang."
        color = "#ef5350"
    elif st.session_state.black_time <= 0:
        msg = "⏰ Waktu Stockfish Habis! Kamu Menang!"
        color = "#4caf50"
    else:
        msg = "🏁 Permainan Selesai"
        color = "#888"

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:1.2rem;
            margin:1rem auto;
            max-width:500px;
            border-radius:10px;
            border:2px solid {color};
            background:{color}18;
            font-family:'Playfair Display',serif;
            font-size:1.3rem;
            color:{color};
            font-weight:700;
        ">
            {msg}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🆕 Main Lagi", use_container_width=True):
            new_game()
            st.rerun()
