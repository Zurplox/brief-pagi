#!/usr/bin/env python3
"""Kirim data/brief_message.txt via WhatsApp (CallMeBot). Opsional Telegram.
Judul pesan sudah jelas & beda dari repo lain (lihat config.brief_title).
Secret: WA_PHONE, WA_APIKEY. Opsional TG_TOKEN, TG_CHAT_ID. FORCE_SEND=1 paksa.
Kirim maks 1x/hari (data/last_sent.json). Hanya pustaka standar Python.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAST = os.path.join(ROOT, "data", "last_sent.json")
ENC_LIMIT = 1300


def load(p, d=None):
    if not os.path.exists(p):
        return d
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def wa_send(phone, apikey, text):
    chunks, cur = [], ""
    for line in text.split("\n"):
        cand = (cur + "\n" + line) if cur else line
        if len(urllib.parse.quote(cand)) > ENC_LIMIT and cur:
            chunks.append(cur)
            cur = line
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    for c in chunks:
        q = urllib.parse.urlencode({"phone": phone, "text": c, "apikey": apikey})
        urllib.request.urlopen("https://api.callmebot.com/whatsapp.php?" + q,
                               timeout=45)


def tg_send(token, chat, text):
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    urllib.request.urlopen("https://api.telegram.org/bot%s/sendMessage" % token,
                           data=data, timeout=45)


def main():
    cfg = load(os.path.join(ROOT, "config.json"), {}) or {}
    msg_path = os.path.join(ROOT, "data", "brief_message.txt")
    if not os.path.exists(msg_path):
        print("Belum ada brief_message.txt")
        return
    with open(msg_path, encoding="utf-8") as f:
        msg = f.read().strip()
    off = timezone(timedelta(hours=cfg.get("utc_offset_hours", 8)))
    now = datetime.now(off)
    if os.environ.get("FORCE_SEND") != "1":
        st = load(LAST, {}) or {}
        try:
            if st.get("date") and datetime.fromisoformat(st["date"]).date() == now.date():
                print("Sudah kirim hari ini, lewati.")
                return
        except ValueError:
            pass
    phone = os.environ.get("WA_PHONE", "").strip()
    apikey = os.environ.get("WA_APIKEY", "").strip()
    tgt = os.environ.get("TG_TOKEN", "").strip()
    tgc = os.environ.get("TG_CHAT_ID", "").strip()
    sent = False
    if phone and apikey:
        try:
            wa_send(phone, apikey, msg)
            sent = True
            print("WhatsApp terkirim.")
        except Exception as e:
            print("WhatsApp gagal:", e)
    if tgt and tgc:
        try:
            tg_send(tgt, tgc, msg)
            sent = True
            print("Telegram terkirim.")
        except Exception as e:
            print("Telegram gagal:", e)
    if not (phone or tgt):
        print("Tidak ada channel notifikasi. Pesan hanya tersimpan di file.")
    if sent:
        with open(LAST, "w", encoding="utf-8") as f:
            json.dump({"date": now.isoformat(timespec="minutes")}, f)


if __name__ == "__main__":
    main()
