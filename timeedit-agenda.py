#!/usr/bin/env python3
"""TimeEdit agenda — fetch an ICS calendar, print today/upcoming, flag important.
Set TIMEEDIT_ICS_URL to your calendar feed.

Source: https://cloud.timeedit.net/shh/web/student/ri669QnQZ67ZZ3Q53180Qbe8yQZ1uY.ics
Local time: Europe/Stockholm.
Important = Inlämning (submissions), examination, muntlig (oral exams), färdighetsträning.
"""
import re, sys, datetime, urllib.request
from zoneinfo import ZoneInfo

import os
ICS_URL = os.environ.get("TIMEEDIT_ICS_URL", "https://example.com/your-calendar.ics")
TZ = ZoneInfo("Europe/Stockholm")
IMPORTANT = re.compile(r"inlämning|examination|examinerande|muntlig|färdighetsträning|tentamen", re.I)


def parse_dt(s):
    m = re.match(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z?", s)
    if not m:
        return None
    y, mo, d, h, mi, se = map(int, m.groups())
    return datetime.datetime(y, mo, d, h, mi, se, tzinfo=datetime.timezone.utc).astimezone(TZ)


def fetch():
    req = urllib.request.Request(ICS_URL, headers={"User-Agent": "agent1-hub/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    try:
        content = fetch()
    except Exception as e:
        print(f"ICS fetch FAILED: {e}")
        sys.exit(1)

    events = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", content, re.S):
        def g(field):
            m = re.search(rf"^{field}:(.*)$", block, re.M)
            return m.group(1).strip() if m else ""

        start, end = parse_dt(g("DTSTART")), parse_dt(g("DTEND"))
        if not start:
            continue
        summary = g("SUMMARY").replace("\\n", " ")
        loc = g("LOCATION").replace("\\n", " ")
        desc = g("DESCRIPTION").replace("\\n", " ").replace("\\,", ",")
        events.append((start, end, summary, loc, desc))

    events.sort(key=lambda e: e[0])
    now = datetime.datetime.now(TZ)
    today = now.date()
    horizon = now + datetime.timedelta(days=7)

    todays = [e for e in events if e[0].date() == today]
    upcoming = [e for e in events if today < e[0].date() <= today + datetime.timedelta(days=2)]
    week = [e for e in events if today < e[0].date() <= horizon.date() and e not in upcoming]

    lines = []
    lines.append(f"📅 TimeEdit — {today.strftime('%A %Y-%m-%d')}")
    if todays:
        for start, end, summary, loc, desc in todays:
            flag = " ⚠️" if IMPORTANT.search(desc or summary) else ""
            t = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}" if end else start.strftime("%H:%M")
            lines.append(f"  {t} {summary}{flag} ({loc})")
    else:
        lines.append("  No scheduled events today.")

    if upcoming:
        lines.append("\nNext 48h:")
        for start, end, summary, loc, desc in upcoming:
            flag = " ⚠️" if IMPORTANT.search(desc or summary) else ""
            lines.append(f"  {start.strftime('%a %H:%M')} {summary}{flag} ({loc})")
            if flag.strip():
                lines.append(f"      {desc[:140]}")

    if week:
        lines.append(f"\nLater this week:")
        for start, end, summary, loc, desc in week:
            lines.append(f"  {start.strftime('%a %H:%M')} {summary} ({loc})")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
