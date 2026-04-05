"""Family calendar panel renderer."""

from PIL import Image, ImageDraw
from datetime import datetime
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w


def render(data, fonts, bbox):
    """Render calendar events panel.

    Args:
        data: list of event dicts from fetch_events()
        fonts: dict of loaded fonts
        bbox: (width, height) of panel area
    """
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    pad = 10
    y = pad

    # -- Header --
    draw.text((pad, y), "KALENDER", font=fonts[24], fill=BLACK)
    ds = datetime.now().strftime('%d/%m')
    dw = txt_w(fonts[16], ds)
    draw.text((w - dw - pad, y + 4), ds, font=fonts[16], fill=TERTIARY)
    y += 30
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 6

    if not data:
        draw.text((pad, y + 10), "Keine Termine", font=fonts[18], fill=TERTIARY)
        return img

    # -- Events list --
    for i, event in enumerate(data):
        if y > h - 30:
            break

        is_today = event.get('is_today', False)
        fill = BLACK if is_today else SECONDARY

        # Date + time
        if event['all_day']:
            dt_str = "{} (ganztaegig)".format(event['date_str'])
        else:
            dt_str = "{} {}".format(event['date_str'], event['time_str'])

        draw.text((pad, y), dt_str, font=fonts[14], fill=EMPHASIS if is_today else TERTIARY)
        y += 16

        # Event title
        draw.text((pad + 5, y), event['summary'], font=fonts[18], fill=fill)

        # Location (if any, on same line right-aligned)
        if event.get('location'):
            lw = txt_w(fonts[14], event['location'])
            draw.text((w - lw - pad, y + 2), event['location'],
                      font=fonts[14], fill=TERTIARY)
        y += 22

        # Separator
        if i < len(data) - 1:
            draw.line([(pad + 10, y), (w - pad - 10, y)], fill=SEPARATOR + 20)
            y += 4

    return img
