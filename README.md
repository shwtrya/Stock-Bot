# Stock-Bot

Bot Telegram untuk screening saham manual, alert sekali pakai, dan screening otomatis berulang.

## Struktur Proyek

```
.
├── bot/
│   ├── core/
│   │   ├── engine.py
│   │   ├── filters.py
│   │   ├── indicators.py
│   │   ├── market_data.py
│   │   └── tickers.py
│   ├── handlers/
│   │   ├── alert.py
│   │   ├── algo.py
│   │   └── screening.py
│   ├── config.py
│   └── main.py
│   └── telegram_bot.py
├── data/
│   └── bei_tickers.txt
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
BEI_TICKERS_FILE=data/bei_tickers.txt
POLL_INTERVAL_SECONDS=15
YFINANCE_SUFFIX=.JK
```

Instal dependensi:

```bash
pip install python-telegram-bot yfinance pandas
```

## Menjalankan

Mode CLI demo (untuk cek dispatcher):

```bash
python -m bot.main "/scr price < 1000 + rsi < 30 title saham murah oversold"
```

Jika `TELEGRAM_BOT_TOKEN` tersedia, bot akan langsung menjalankan Telegram polling.
Jika tanpa argumen dan tanpa token, bot akan menampilkan daftar command yang tersedia.

## Command

### `/scr` (Screening Manual)
- Manual sekali jalan, hasil statis.
- Cocok dipakai malam hari atau sebelum bursa buka untuk nyiapin watchlist.
- Realtime: screening semua ticker BEI.

Contoh:
```
/scr price < 1000 + rsi < 30 title saham murah oversold
```

### `/alert` (Alarm Sekali Pakai)
- Bot memantau otomatis selama jam bursa.
- Sekali tembak: notif dikirim saat kondisi terpenuhi lalu selesai.
- Realtime: memantau semua ticker BEI.

Contoh:
```
/alert bren price > 9000
```

### `/algo` (Screening Otomatis & Berulang)
- Bot memantau otomatis sepanjang jam bursa.
- Berulang: tiap saham masuk kriteria → notif dikirim.
- Realtime: memantau semua ticker BEI.

### `/stop`
- Menghentikan alert/algo yang sedang aktif.

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

## Data Ticker BEI

Daftar ticker BEI dibaca dari `data/bei_tickers.txt` atau endpoint publik yang diset lewat
`BEI_TICKERS_URL` (support `txt`, `csv`, `json`). Format file: satu ticker per baris
dan harus berisi seluruh kode saham BEI agar realtime screening mencakup semuanya.
Bot mengambil data intraday (interval 1 menit) via `yfinance` untuk kebutuhan realtime.
