# timeedit-agenda

Fetch a TimeEdit ICS calendar feed and print today's / upcoming events,
flagging the important ones (submissions, exams, oral exams, training).

```
export TIMEEDIT_ICS_URL="https://your-instance.timeedit.net/.../feed.ics"
python3 timeedit-agenda.py            # today + next 48h
python3 timeedit-agenda.py --week     # whole week
```

## Why

TimeEdit is the standard scheduling system for Swedish universities and
colleges. Its ICS feed lets you script your academic calendar: this tool
summarizes what's due, filters out noise, and shouts when something
important (exam, submission) is within 48 hours.

## Important-event detection

Events whose names match any of (localizable, edit the `IMPORTANT` list):

- `Inlämning` (submissions)
- `examination` / exams
- `muntlig` (oral exams)
- `färdighetsträning` (skills training)

## Requirements

- Python 3.8+ (stdlib only)

## Config

- `TIMEEDIT_ICS_URL` — your calendar feed URL (required, see above)
- Timezone: Europe/Stockholm (edit `TZ` at top of script)
