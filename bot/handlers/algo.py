"""Handler for /algo (screening otomatis & berulang)."""


def handle_algo() -> str:
    return (
        "🤖 /algo (Screening Otomatis & Berulang)\n"
        "Cara kerja: seperti alert, tapi berulang terus-menerus.\n"
        "Sifat: 🔁 jalan otomatis sepanjang jam bursa, setiap saham masuk kriteria → notif.\n"
        "Kapan dipakai: strategi harian / pantauan berkelanjutan (breakout, inflow, volume).\n\n"
        "📌 Contoh:\n"
        "/algo gain > 3 + vol > ma20vol title saham momentum harian\n"
        "→ Bot memantau gain > 3% dan volume > rata-rata 20 hari, update selama bursa."
    )
