"""BVG transport departures panel renderer."""

from PIL import Image, ImageDraw
from datetime import datetime
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w


def render(data, fonts, bbox):
    """Render BVG departures panel.

    Args:
        data: dict with 'bus' and 'ubahn' lists from fetch_departures()
        fonts: dict of loaded fonts
        bbox: (width, height) of panel area
    """
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    pad = 10
    y = pad

    # -- Header --
    draw.text((pad, y), "BVG", font=fonts[24], fill=BLACK)
    draw.text((pad + 60, y + 4), "Abfahrten", font=fonts[16], fill=SECONDARY)
    now_str = datetime.now().strftime('%H:%M')
    nw = txt_w(fonts[16], now_str)
    draw.text((w - nw - pad, y + 4), now_str, font=fonts[16], fill=TERTIARY)
    y += 30
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 6

    bus = data.get('bus', [])
    ubahn = data.get('ubahn', [])
    sbahn = data.get('sbahn', [])

    if not bus and not ubahn and not sbahn:
        draw.text((pad, y + 20), "Keine Abfahrten", font=fonts[18], fill=TERTIARY)
        return img

    col_line = pad
    col_dir = pad + 40
    col_mins = w - 110
    col_time = w - 55

    # -- M43 Bus --
    if bus:
        import config
        bus_label = "{} {}".format(
            getattr(config, 'BVG_BUS_LINE', 'Bus'),
            getattr(config, 'BVG_BUS_STOP_NAME', ''))
        draw.text((pad, y), bus_label, font=fonts[14], fill=SECONDARY)
        y += 18
        for dep in bus:
            draw.text((col_line, y), dep['line'], font=fonts[16], fill=BLACK)
            draw.text((col_dir, y), dep['direction'], font=fonts[14], fill=BLACK)
            draw.text((col_mins, y), "{}min".format(dep['mins']), font=fonts[16], fill=EMPHASIS)
            draw.text((col_time, y), dep['time'], font=fonts[14], fill=TERTIARY)
            if dep.get('delay') and dep['delay'] > 0:
                draw.text((col_time + 35, y), "+{}".format(dep['delay']),
                          font=fonts[14], fill=EMPHASIS)
            y += 20
        y += 2

    # -- Separator --
    if bus and (ubahn or sbahn):
        draw.line([(pad + 10, y), (w - pad - 10, y)], fill=SEPARATOR)
        y += 4

    # -- U7 --
    if ubahn:
        ubahn_label = "{} -> {} (>{}min)".format(
            getattr(config, 'BVG_UBAHN_LINE', 'U'),
            getattr(config, 'BVG_UBAHN_DIRECTION', ''),
            getattr(config, 'BVG_UBAHN_MIN_MINUTES', 15))
        draw.text((pad, y), ubahn_label, font=fonts[14], fill=SECONDARY)
        y += 18
        for dep in ubahn:
            draw.text((col_line, y), dep['line'], font=fonts[16], fill=BLACK)
            draw.text((col_dir, y), dep['direction'], font=fonts[14], fill=BLACK)
            draw.text((col_mins, y), "{}min".format(dep['mins']), font=fonts[16], fill=EMPHASIS)
            draw.text((col_time, y), dep['time'], font=fonts[14], fill=TERTIARY)
            if dep.get('delay') and dep['delay'] > 0:
                draw.text((col_time + 35, y), "+{}".format(dep['delay']),
                          font=fonts[14], fill=EMPHASIS)
            y += 20
        y += 2

    # -- Separator --
    if (bus or ubahn) and sbahn:
        draw.line([(pad + 10, y), (w - pad - 10, y)], fill=SEPARATOR)
        y += 4

    # -- S9 Treptower -> Savignyplatz --
    if sbahn:
        sbahn_label = "{} journey".format(getattr(config, 'BVG_SBAHN_LINE', 'S'))
        draw.text((pad, y), sbahn_label, font=fonts[14], fill=SECONDARY)
        y += 18
        for dep in sbahn:
            draw.text((col_line, y), dep['line'], font=fonts[16], fill=BLACK)
            dep_arr = "{} -> {}".format(dep['dep_time'], dep['arr_time'])
            draw.text((col_dir, y), dep_arr, font=fonts[16], fill=BLACK)
            draw.text((col_mins, y), "{}min".format(dep['mins']), font=fonts[16], fill=EMPHASIS)
            dur_str = "{}m ride".format(dep['duration'])
            draw.text((col_time - 10, y), dur_str, font=fonts[14], fill=TERTIARY)
            if dep.get('delay') and dep['delay'] > 0:
                draw.text((col_time + 35, y), "+{}".format(dep['delay']),
                          font=fonts[14], fill=EMPHASIS)
            y += 20

    return img
