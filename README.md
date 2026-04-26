# ♟ Chess Arena — Streamlit vs Stockfish

Aplikasi catur full-featured berbasis Python & Streamlit dengan AI Stockfish yang dapat disesuaikan level ELO-nya.

## Fitur

- **Papan interaktif** — klik piece → highlight legal moves → klik tujuan
- **7 Level ELO** — dari Pemula (400) hingga Stockfish Max (2800+)
- **Move history** — notasi SAN real-time di sidebar
- **Captured pieces** — tampilkan bidak yang sudah dimakan
- **Timer** — clock per player (10 menit default)
- **Deteksi status** — Skak, Skak Mat, Stalemate, Draw (semua varian)
- **Undo move** — batalkan langkah terakhir (player + AI)
- **Flip board** — lihat dari perspektif Hitam

## Instalasi

### 1. Install dependensi Python

```bash
pip install -r requirements.txt
```

### 2. Install Stockfish

**Ubuntu/Debian:**
```bash
sudo apt install stockfish
```

**macOS:**
```bash
brew install stockfish
```

**Windows:**
1. Download binary dari https://stockfishchess.org/download/
2. Tambahkan ke PATH atau letakkan di folder yang sama dengan `app.py`
3. Update `STOCKFISH_PATHS` di `chess_engine.py` jika perlu

### 3. Jalankan aplikasi

```bash
streamlit run app.py
```

## Deploy ke Streamlit Cloud

1. Push ke GitHub repository
2. Di Streamlit Cloud, tambahkan `packages.txt`:
   ```
   stockfish
   ```
3. Deploy seperti biasa

## Struktur Project

```
chess_app/
├── app.py              # Streamlit UI utama
├── chess_engine.py     # Stockfish wrapper + ELO config
├── board_renderer.py   # SVG board + highlight + status
├── game_state.py       # Session state management
├── requirements.txt    # Python dependencies
└── README.md
```

## Cara Bermain

1. **Putih** selalu dikendalikan oleh player (kamu)
2. Klik bidak untuk memilihnya (highlight biru)
3. Kotak hijau menandai langkah legal yang tersedia
4. Klik kotak tujuan untuk memindahkan bidak
5. Stockfish otomatis merespons sebagai **Hitam**
6. Gunakan sidebar untuk mengubah level, undo, atau new game

## Level ELO

| Level | ELO | Setara |
|-------|-----|--------|
| 🐣 Pemula | 400 | Sangat mudah |
| 🌱 Dasar | 800 | Pemain kasual |
| ⚔️ Menengah | 1200 | Club player |
| 🏆 Mahir | 1600 | Tournament player |
| 🔥 Expert | 2000 | National master |
| 💎 Master | 2400 | International master |
| 🤖 Max | 2800+ | Full Stockfish strength |
