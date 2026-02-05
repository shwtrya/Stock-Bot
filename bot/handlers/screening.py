"""Handler for /scr (screening manual)."""


def handle_scr() -> str:
    return (
        "🔎 /scr (Screening Manual)\n"
        "Cara kerja: user ketik manual → bot kasih daftar saham sesuai filter.\n"
        "Sifat: ⚡ sekali jalan (hasil statis).\n"
        "Kapan dipakai: malam hari / sebelum bursa buka untuk nyiapin watchlist.\n"
        "Realtime: data diambil untuk semua ticker BEI.\n\n"
        "📌 Contoh:\n"
        "/scr price < 1000 + rsi < 30 title saham murah oversold\n"
        "→ Bot kasih list saham dengan harga < 1000 dan RSI < 30."
    )
