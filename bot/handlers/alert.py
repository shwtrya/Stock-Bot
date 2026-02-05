"""Handler for /alert (alarm sekali pakai)."""


def handle_alert() -> str:
    return (
        "⏰ /alert (Alarm Sekali Pakai)\n"
        "Cara kerja: bot pantau otomatis selama jam bursa.\n"
        "Sifat: 🎯 sekali tembak → kondisi ketemu, notif dikirim, alert selesai.\n"
        "Kapan dipakai: trigger spesifik (mis. harga tembus level tertentu).\n"
        "Realtime: memantau semua ticker BEI.\n\n"
        "📌 Contoh:\n"
        "/alert bren price > 9000\n"
        "→ Bot pantau BREN, saat tembus Rp9000 notif dikirim lalu alert berakhir."
    )
