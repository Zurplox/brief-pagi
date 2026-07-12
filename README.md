# 📰 brief-pagi

Satu pesan **WhatsApp tiap pagi**: berita sawit & agri Indonesia + kutipan pasar
(ETF/saham + kurs), diringkas AI (opsional). Pola sama seperti `kebun-sawit-cuaca`,
tapi **judul & isi beda** biar tidak tertukar.

> Judul pesan: **📰 BRIEF PAGI — <tanggal>** &nbsp; (cuaca = 🌦️, panen = 🌴)

## Alur (GitHub Actions, tiap pagi 07:00 WIB)
1. `scripts/fetch_news.py` — berita via **RSS langsung** (infosawit, sawitindonesia, elaeis) + **Google News RSS** ID (tanpa API key) → `data/news.json`
2. `scripts/fetch_markets.py` — harga & kurs via **Yahoo Finance** (tanpa key; fallback FX ke exchangerate.host) → `data/markets.json`
3. `scripts/build_brief.py` — rakit brief; kalau ada `GEMINI_API_KEY`, ringkas dengan AI → `data/brief.json` + `data/brief_message.txt`
4. `scripts/notify.py` — kirim ke WhatsApp (maks 1×/hari)
5. commit `data/`; `index.html` (GitHub Pages) menampilkan brief terakhir

Hanya **pustaka standar Python** (tanpa `pip install`).

## Secrets (Settings → Secrets and variables → Actions)

| Secret | Wajib? | Untuk |
|---|---|---|
| `WA_PHONE` | notif | nomor WhatsApp tujuan (mis. `628xxxxxxxxxx`) |
| `WA_APIKEY` | notif | apikey CallMeBot |
| `GEMINI_API_KEY` | opsional | ringkasan AI (Google AI Studio, ada **free tier**). Tanpa ini tetap jalan sebagai digest rapi. |
| `TG_TOKEN`, `TG_CHAT_ID` | opsional | Telegram |

**CallMeBot:** kirim `I allow callmebot to send me messages` ke **+34 644 51 95 23**, simpan apikey balasannya.
**Gemini gratis:** aistudio.google.com → *Get API key*.

## Atur di `config.json`
- `news.extra_feeds` — RSS situs sawit (default: infosawit / sawitindonesia / elaeis)
- `news.queries` — kata kunci Google News ID (harga TBS Riau, CPO, MPOB, GAPKI)
- `markets.tickers` — symbol **Yahoo Finance** (default VOO / QQQ / VEU). Ganti sesukamu.
- `markets.fx` — pasangan kurs (default USD/SGD, USD/IDR, SGD/IDR); otomatis jadi symbol `USDIDR=X` dll di Yahoo.
- `brief_title`, `emoji` — judul & ikon pesan

## Catatan
- **Kurs pakai Yahoo Finance** (lebih akurat & update). Kalau Yahoo error untuk FX, otomatis fallback ke exchangerate.host.
- **CPO futures (Bursa Malaysia FCPO) tidak punya API gratis/resmi.** Jadi CPO dibahas lewat **berita + harga MPOB**, bukan feed futures live.
- Jalankan lokal: `python scripts/fetch_news.py && python scripts/fetch_markets.py && python scripts/build_brief.py` (butuh internet).
