#!/usr/bin/env python3
"""Susun brief pagi dari data/news.json + data/markets.json.

Kalau ada secret GEMINI_API_KEY -> ringkas pakai AI (Gemini free tier).
Kalau tidak -> digest rapi tanpa AI (tetap jalan, gratis).
Output: data/brief.json + data/brief_message.txt
Hanya pustaka standar Python.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BULAN = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
         "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def load(p, d=None):
    p = os.path.join(ROOT, p)
    if not os.path.exists(p):
        return d
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def today_str(cfg):
    off = timezone(timedelta(hours=cfg.get("utc_offset_hours", 8)))
    d = datetime.now(off).date()
    return "%02d %s %d" % (d.day, BULAN[d.month], d.year)


def fmt_num(n):
    if n is None:
        return "-"
    if abs(n) >= 1000:
        return format(int(round(n)), ",d").replace(",", ".")
    return ("%.4f" % n).rstrip("0").rstrip(".") if abs(n) < 10 else ("%.2f" % n)


def markets_block(markets):
    lines = []
    for t in markets.get("tickers", []):
        pct = t.get("pct")
        arrow = "→"
        if pct is not None:
            arrow = "▲" if pct > 0 else ("▼" if pct < 0 else "→")
        lines.append("  %s %s: %s (%s%s%%)" % (
            arrow, t.get("label"), fmt_num(t.get("last")),
            "+" if (pct or 0) > 0 else "", pct if pct is not None else "?"))
    for f in markets.get("fx", []):
        lines.append("  💱 %s: %s" % (f.get("pair"), fmt_num(f.get("rate"))))
    return "\n".join(lines) if lines else "  (data pasar tidak tersedia)"


def news_block(news):
    lines = []
    for n in news:
        src = (" — " + n["source"]) if n.get("source") else ""
        lines.append("• %s%s" % (n["title"], src))
    return "\n".join(lines) if lines else "(tidak ada berita baru)"


def gemini_summary(payload_text, api_key):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "gemini-1.5-flash:generateContent?key=" + api_key)
    prompt = (
        "Kamu editor brief pagi untuk pemilik kebun sawit di Riau yang juga "
        "investor. Dari data berita & pasar di bawah, tulis ringkasan SINGKAT "
        "dalam Bahasa Indonesia: 3-5 poin peluru paling penting untuk bisnis "
        "sawit & keputusan hari ini, lalu 1 baris sentimen pasar. Padat, tanpa "
        "basa-basi, maksimal ~120 kata. Jangan mengarang; hanya dari data.\n\n"
        + payload_text)
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def main():
    cfg = load("config.json", {})
    news = load("data/news.json", []) or []
    markets = load("data/markets.json", {}) or {}
    title = "%s *%s* — %s" % (cfg.get("emoji", "📰"),
                              cfg.get("brief_title", "BRIEF PAGI"), today_str(cfg))

    payload = "PASAR:\n%s\n\nBERITA:\n%s" % (
        markets_block(markets),
        "\n".join("- %s (%s)" % (n["title"], n.get("source", "")) for n in news))

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    ai_summary = None
    if api_key and news:
        try:
            ai_summary = gemini_summary(payload, api_key)
        except Exception as e:
            print("Gemini gagal, pakai digest biasa:", str(e)[:100])

    parts = [title, ""]
    if ai_summary:
        parts += ["🧠 *Ringkasan:*", ai_summary, ""]
    parts += ["📈 *Pasar:*", markets_block(markets), "",
              "📰 *Berita sawit & agri:*", news_block(news)]
    message = "\n".join(p for p in parts if p is not None)

    with open(os.path.join(ROOT, "data", "brief.json"), "w", encoding="utf-8") as f:
        json.dump({"title": title, "ai_summary": ai_summary, "news": news,
                   "markets": markets, "generated": datetime.now(timezone.utc)
                   .isoformat(timespec="minutes")}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "data", "brief_message.txt"), "w",
              encoding="utf-8") as f:
        f.write(message)
    print("OK -> data/brief.json + data/brief_message.txt")
    print("AI:", "ya" if ai_summary else "tidak (digest biasa)")
    print("\n" + message)


if __name__ == "__main__":
    main()
