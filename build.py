#!/usr/bin/env python3
"""Build the subscribable calendar feed from events.json + digests.json.

Subscribed calendars (Google/iOS) ignore embedded alarms, so every reminder is
its own all-day event. Set ONE default notification on the subscribed calendar
(e.g. "on the day at 09:00") and each reminder becomes a phone push.

stdlib only: python3 build.py
"""
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent
FEED = ROOT / "feed" / "563254d75c3512ab.ics"

# Reminder offsets in days before start, by relevance + whether travel is needed.
OFFSETS = {
    (3, True): [56, 42, 28, 14, 7, 1],
    (3, False): [21, 7, 1],
    (2, True): [42, 21, 7],
    (2, False): [7, 1],
    (1, True): [21],
    (1, False): [3],
}
HOME_CITY = "Paris"
STARS = {3: "★★★", 2: "★★", 1: "★"}


def esc(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    raw = line.encode("utf-8")
    out = []
    while len(raw) > 74:
        cut = 74
        while (raw[cut] & 0xC0) == 0x80:  # don't split a UTF-8 char
            cut -= 1
        out.append(raw[:cut].decode())
        raw = b" " + raw[cut:]
    out.append(raw.decode())
    return "\r\n".join(out)


def d(s):
    return date.fromisoformat(s)


def vevent(uid, summary, start, end_inclusive, description="", location="", url=""):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@event-radar",
        f"DTSTAMP:{stamp}",
        f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
        f"DTEND;VALUE=DATE:{end_inclusive + timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{esc(summary)}",
        "TRANSP:TRANSPARENT",
    ]
    if description:
        lines.append(f"DESCRIPTION:{esc(description)}")
    if location:
        lines.append(f"LOCATION:{esc(location)}")
    if url:
        lines.append(f"URL:{url}")
    lines.append("END:VEVENT")
    return [fold(l) for l in lines]


def describe(e):
    price = "kostenlos" if e.get("price_eur") == 0 else (
        f"~€{e['price_eur']}" if e.get("price_eur") is not None else "Preis unbekannt")
    parts = [
        f"{STARS[e['relevance']]} {e['category']} · {e['city']} · {price}",
        "",
        e.get("why", ""),
    ]
    if e.get("cheap_access"):
        parts += ["", f"Günstig rein: {e['cheap_access']}"]
    if e.get("deadlines"):
        parts += ["", "Deadlines:"] + [f"• {x['date']}: {x['label']}" for x in e["deadlines"]]
    if not e.get("confirmed", True):
        parts += ["", "⚠ Datum noch nicht offiziell bestätigt."]
    parts += ["", e.get("url", "")]
    return "\n".join(parts)


def build():
    events = json.loads((ROOT / "events.json").read_text())
    digests = json.loads((ROOT / "digests.json").read_text())
    today = date.today()
    out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//event-radar//DE",
           "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Event Radar",
           "X-WR-TIMEZONE:Europe/Paris", "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
           "X-PUBLISHED-TTL:PT12H"]

    for e in events:
        if e.get("dismissed") or not e.get("start"):  # no date yet = watchlist only
            continue
        start, end = d(e["start"]), d(e.get("end") or e["start"])
        if end < today - timedelta(days=7):
            continue
        desc = describe(e)
        loc = f"{e['city']}, {e.get('country', '')}".strip(", ")
        flag = "" if e.get("confirmed", True) else " (?)"
        out += vevent(e["id"], f"{STARS[e['relevance']]} {e['title']}{flag}",
                      start, end, desc, loc, e.get("url", ""))

        travel = e["city"] != HOME_CITY
        for days in OFFSETS[(e["relevance"], travel)]:
            when = start - timedelta(days=days)
            if when < today:
                continue
            label = ("1 Woche" if days == 7 else f"{days // 7} Wochen") if days % 7 == 0 else ("1 Tag" if days == 1 else f"{days} Tagen")
            hint = " – Reise/Ticket klären" if travel and days >= 14 else ""
            out += vevent(f"{e['id']}-r{days}", f"⏰ {e['title']} in {label}{hint}",
                          when, when, desc, loc, e.get("url", ""))

        for dl in e.get("deadlines", []):
            when = d(dl["date"])
            if when < today:
                continue
            uid = f"{e['id']}-dl-" + hashlib.sha1(dl["label"].encode()).hexdigest()[:8]
            out += vevent(uid, f"🎟 {dl['label']} – {e['title']}", when, when,
                          desc, loc, e.get("url", ""))
            pre = when - timedelta(days=5)
            if pre >= today:
                out += vevent(uid + "-pre", f"⏰ in 5 Tagen: {dl['label']} – {e['title']}",
                              pre, pre, desc, loc, e.get("url", ""))

    for g in digests[-6:]:
        out += vevent(f"digest-{g['date']}", f"📬 Event-Radar: {g['headline']}",
                      d(g["date"]), d(g["date"]), g["body"])

    out.append("END:VCALENDAR")
    FEED.parent.mkdir(exist_ok=True)
    FEED.write_text("\r\n".join(out) + "\r\n", encoding="utf-8")
    print(f"wrote {FEED.relative_to(ROOT)}: {sum(1 for l in out if l == 'BEGIN:VEVENT')} entries")


if __name__ == "__main__":
    build()
