"""Full-screen family calendar week view with one row per family member.

Layout:
+--------+---Mo---+---Di---+---Mi---+---Do---+---Fr---+---Sa---+---So---+
|Familie | event  |        | event  |        |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Papa   |        | event  |        |        | event  |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Mama   | event  |        | event  | event  |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Kids   |        |        | event  |        | event  |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
"""

from PIL import Image, ImageDraw
from datetime import datetime, date, timedelta
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap

from datetime import time as dt_time

DAYS_DE = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']


def _inject_demo_events(data, week_start):
    """Add demo events for calendars with no events (no URL configured yet).
    Remove this function once all calendars have real URLs.
    """
    demo = {
        'Papa': [
            (0, '08:30', 'Standup Team'),
            (1, '10:00', 'Workshop ML'),
            (2, '14:00', 'Zahnarzt'),
            (3, '09:00', 'Review Sprint'),
            (4, '18:00', 'Laufen'),
        ],
        'Mama': [
            (0, '09:00', 'Yoga'),
            (1, '15:00', 'Elternabend'),
            (2, '10:00', 'Arzt'),
            (3, '08:30', 'Pilates'),
            (4, '14:00', 'Cafe Sara'),
            (5, '10:00', 'Markt'),
        ],
        'Kids': [
            (0, '15:30', 'Fussball Leo'),
            (1, '16:00', 'Klavier Mia'),
            (2, '15:30', 'Schwimmen'),
            (3, '16:00', 'Klavier Mia'),
            (4, '15:00', 'Playdate Tom'),
            (5, '', 'Oma & Opa'),
        ],
    }

    for cal in data:
        name = cal.get('name', '')
        if cal.get('events') or name not in demo:
            continue
        events = []
        for day_offset, time_str, summary in demo[name]:
            evt_date = week_start + timedelta(days=day_offset)
            if time_str:
                h, m = map(int, time_str.split(':'))
                start_dt = datetime.combine(evt_date, dt_time(h, m))
            else:
                start_dt = datetime.combine(evt_date, datetime.min.time())
            events.append({
                'summary': summary,
                'time_str': time_str,
                'date_str': '',
                'all_day': not bool(time_str),
                'start': start_dt,
                'is_today': evt_date == date.today(),
            })
        cal['events'] = events
MONTHS_DE = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun',
             'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']


def render(data, fonts, bbox):
    """Render family calendar week view with horizontal rows.

    Args:
        data: list of {'name': str, 'events': [event dicts]} from fetch_family_calendars()
        fonts: dict of loaded fonts
        bbox: (width, height) of panel area (full 1200x825)
    """
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    today = date.today()
    weekday = today.weekday()
    # Show next week if past Thursday
    if weekday >= 4:
        week_start = today + timedelta(days=(7 - weekday))
    else:
        week_start = today - timedelta(days=weekday)

    # Dimensions
    label_w = 90       # width of person name column
    header_h = 50      # height of day header row
    footer_h = 20
    pad = 4

    n_rows = len(data) if data else 1
    col_w = (w - label_w) // 7
    row_h = (h - header_h - footer_h) // max(n_rows, 1)

    # -- Title bar --
    month = MONTHS_DE[week_start.month]
    title = "FAMILIENKALENDER  {} {}  KW{}".format(
        month, week_start.year, week_start.isocalendar()[1])
    draw.rectangle([(0, 0), (w, 28)], fill=235)
    draw.text((pad + 5, 3), title, font=fonts[20], fill=BLACK)

    # -- Day headers --
    for i in range(7):
        day = week_start + timedelta(days=i)
        x = label_w + i * col_w
        is_today = (day == today)
        is_weekend = (i >= 5)

        if is_today:
            draw.rectangle([(x, 28), (x + col_w - 1, header_h)], fill=215)

        day_label = "{} {}".format(DAYS_DE[i], day.day)
        fill = BLACK if is_today else (SECONDARY if is_weekend else BLACK)
        font = fonts[18] if is_today else fonts[16]
        draw.text((x + pad, 30), day_label, font=font, fill=fill)

        if is_today:
            # Underline today
            tw = txt_w(font, day_label)
            draw.line([(x + pad, header_h - 2), (x + pad + tw, header_h - 2)],
                      fill=BLACK, width=2)

    # Horizontal line under headers
    draw.line([(0, header_h), (w, header_h)], fill=SEPARATOR)

    # -- Person rows --
    if not data:
        draw.text((label_w + 20, header_h + 20), "Keine Kalender konfiguriert",
                  font=fonts[18], fill=TERTIARY)
        return img

    # Inject demo events for calendars with no URL (empty events)
    _inject_demo_events(data, week_start)

    # Gray shades per row for visual distinction
    row_fills = [255, 245, 255, 245]  # alternating white/light gray

    for row_idx, cal in enumerate(data):
        ry = header_h + row_idx * row_h
        name = cal.get('name', '')
        events = cal.get('events', [])

        # Row background (alternating)
        bg = row_fills[row_idx % len(row_fills)]
        if bg != 255:
            draw.rectangle([(0, ry), (w, ry + row_h - 1)], fill=bg)

        # Person label (vertical left column)
        draw.rectangle([(0, ry), (label_w - 1, ry + row_h - 1)], fill=230)
        draw.text((pad, ry + pad + 2), name, font=fonts[18], fill=BLACK)

        # Row separator
        draw.line([(0, ry + row_h - 1), (w, ry + row_h - 1)], fill=SEPARATOR)

        # Group events by day
        events_by_day = {}
        for event in events:
            evt_date = event['start'].date() if hasattr(event['start'], 'date') else event['start']
            events_by_day.setdefault(evt_date.isoformat(), []).append(event)

        # Draw events in each day column
        for i in range(7):
            day = week_start + timedelta(days=i)
            x = label_w + i * col_w
            day_key = day.isoformat()
            day_events = events_by_day.get(day_key, [])

            # Column separator
            draw.line([(x, ry), (x, ry + row_h - 1)], fill=SEPARATOR)

            # Draw events
            ey = ry + pad
            for event in day_events:
                if ey > ry + row_h - 18:
                    remaining = len(day_events) - day_events.index(event)
                    draw.text((x + pad, ey), "+{}".format(remaining),
                              font=fonts[14], fill=TERTIARY)
                    break

                # Time
                time_str = event.get('time_str', '')
                if time_str:
                    draw.text((x + pad, ey), time_str, font=fonts[14], fill=TERTIARY)

                # Title (same line after time, or next line if long)
                summary = event.get('summary', '')[:15]
                if time_str:
                    draw.text((x + pad + 38, ey), summary, font=fonts[14], fill=BLACK)
                    ey += 16
                else:
                    # All-day event
                    draw.text((x + pad, ey), summary, font=fonts[14], fill=SECONDARY)
                    ey += 16

                ey += 2  # gap between events

    # -- Today column highlight (vertical line) --
    if week_start <= today <= week_start + timedelta(days=6):
        day_idx = (today - week_start).days
        tx = label_w + day_idx * col_w
        draw.line([(tx, header_h), (tx, h - footer_h)], fill=EMPHASIS, width=2)
        draw.line([(tx + col_w, header_h), (tx + col_w, h - footer_h)], fill=EMPHASIS, width=2)

    # Footer
    draw.text((pad, h - footer_h + 2), "Aktualisiert: {}".format(
        datetime.now().strftime('%H:%M')), font=fonts[14], fill=TERTIARY)

    return img
