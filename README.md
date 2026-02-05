# Stock-Bot

Bot Telegram untuk screening saham manual, alert sekali pakai, dan screening otomatis berulang.

## Struktur Proyek

```
.
├── bot/
│   ├── core/
│   │   └── filters.py
│   ├── handlers/
│   │   ├── alert.py
│   │   ├── algo.py
│   │   └── screening.py
│   ├── config.py
│   └── main.py
└── .env.example
```

## Instalasi

1. Pastikan Python 3.10+ terpasang.
2. (Opsional) Buat virtual environment.
3. Salin file env contoh lalu isi token bot Telegram.

```bash
cp .env.example .env
```

Isi `.env`:

```
TELEGRAM_BOT_TOKEN=isi_token_telegram
```

## Menjalankan

Mode CLI demo (untuk cek dispatcher):

```bash
python -m bot.main "/scr price < 1000 + rsi < 30 title saham murah oversold"
```

Jika tanpa argumen, bot akan menampilkan daftar command yang tersedia.

## Command

### `/scr` (Screening Manual)
- Manual sekali jalan, hasil statis.
- Cocok dipakai malam hari atau sebelum bursa buka untuk nyiapin watchlist.

Contoh:
```
/scr price < 1000 + rsi < 30 title saham murah oversold
```

### `/alert` (Alarm Sekali Pakai)
- Bot memantau otomatis selama jam bursa.
- Sekali tembak: notif dikirim saat kondisi terpenuhi lalu selesai.

Contoh:
```
/alert bren price > 9000
```

### `/algo` (Screening Otomatis & Berulang)
- Bot memantau otomatis sepanjang jam bursa.
- Berulang: tiap saham masuk kriteria → notif dikirim.

Contoh:
```
/algo gain > 3 + vol > ma20vol title saham momentum harian
```

## Format Filter

Filter dipisahkan dengan tanda `+` dan memakai operator perbandingan.

Contoh:
```
price < 1000
rsi < 30
vol > ma20vol
```

Parser ada di `bot/core/filters.py` dan mendukung operator `<`, `<=`, `>`, `>=`, `=`, `==`.
