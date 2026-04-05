"""Tides panel renderer with SHOM coefficients and tide curve."""

import time
from PIL import Image, ImageDraw
from datetime import datetime
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w


def _draw_tide_curve(draw, sea_level, bbox, fonts):
    """Draw a 24h tide curve in the given bounding box.

    Args:
        draw: ImageDraw context
        sea_level: list of {'epoch', 'height', 'hour'} dicts
        bbox: (x, y, w, h) of the curve area
    """
    cx, cy, cw, ch = bbox
    pad_l = 5   # left padding for labels
    pad_r = 5
    pad_t = 2
    pad_b = 16  # bottom for hour labels

    plot_x = cx + pad_l
    plot_w = cw - pad_l - pad_r
    plot_y = cy + pad_t
    plot_h = ch - pad_t - pad_b

    if not sea_level or len(sea_level) < 3:
        return

    # Filter to ~30h of data from start of today
    now = time.time()
    today_start = now - (now % 86400) - time.timezone  # approximate midnight local
    points = [p for p in sea_level if p['epoch'] >= today_start - 3600]
    if len(points) < 3:
        points = sea_level[:30]

    # Time range
    t_min = points[0]['epoch']
    t_max = points[-1]['epoch']
    t_range = t_max - t_min
    if t_range == 0:
        return

    # Height range
    heights = [p['height'] for p in points]
    h_min = min(heights)
    h_max = max(heights)
    h_range = h_max - h_min
    if h_range == 0:
        h_range = 1

    # Draw grid lines (light)
    for i in range(5):
        gy = plot_y + int(plot_h * i / 4)
        draw.line([(plot_x, gy), (plot_x + plot_w, gy)], fill=SEPARATOR + 30)

    # Draw hour labels at bottom
    for p in points:
        hour = int(p['hour'])
        if hour % 3 == 0:
            x = plot_x + int((p['epoch'] - t_min) / t_range * plot_w)
            if plot_x <= x <= plot_x + plot_w - 15:
                draw.text((x - 5, cy + ch - pad_b + 1), str(hour),
                          font=fonts[14], fill=TERTIARY)

    # Draw the curve
    curve_points = []
    for p in points:
        x = plot_x + int((p['epoch'] - t_min) / t_range * plot_w)
        y = plot_y + plot_h - int((p['height'] - h_min) / h_range * plot_h)
        curve_points.append((x, y))

    if len(curve_points) >= 2:
        # Draw filled area under curve (light gray)
        fill_points = list(curve_points) + [(curve_points[-1][0], plot_y + plot_h),
                                             (curve_points[0][0], plot_y + plot_h)]
        draw.polygon(fill_points, fill=240)

        # Draw curve line (dark)
        draw.line(curve_points, fill=EMPHASIS, width=2)

    # Draw "now" marker
    if t_min <= now <= t_max:
        nx = plot_x + int((now - t_min) / t_range * plot_w)
        draw.line([(nx, plot_y), (nx, plot_y + plot_h)], fill=BLACK, width=1)
        # Small triangle at top
        draw.polygon([(nx - 3, plot_y), (nx + 3, plot_y), (nx, plot_y + 5)], fill=BLACK)


def render(data, fonts, bbox):
    """Render tides panel with table + curve.

    Args:
        data: dict with 'extremes' (tide list) and 'sea_level' (hourly points)
        fonts: dict of loaded fonts
        bbox: (width, height) of panel area
    """
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    import config
    pad = 10
    y = pad

    # Unpack data
    extremes = data.get('extremes', []) if isinstance(data, dict) else data
    sea_level = data.get('sea_level') if isinstance(data, dict) else None

    # -- Header --
    draw.text((pad, y), "GEZEITEN", font=fonts[24], fill=BLACK)
    loc = getattr(config, 'TIDE_LOCATION', '')
    draw.text((pad + 140, y + 4), loc, font=fonts[18], fill=SECONDARY)
    ds = datetime.now().strftime('%d/%m')
    dw = txt_w(fonts[16], ds)
    draw.text((w - dw - pad, y + 4), ds, font=fonts[16], fill=TERTIARY)
    y += 30
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 4

    if not extremes:
        draw.text((pad, y + 10), "Keine Gezeitendaten", font=fonts[18], fill=TERTIARY)
        return img

    # -- Find next upcoming tide --
    now = time.time()
    next_idx = None
    for i, t in enumerate(extremes[:5]):
        if t['epoch'] > now:
            next_idx = i
            break

    # -- Compact tide table (smaller to make room for curve) --
    for i, t in enumerate(extremes[:4]):
        is_high = (t['type'] == 'high')
        label = "H" if is_high else "T"
        height = "{:.1f}m".format(t['height'])
        is_next = (i == next_idx)

        if is_next:
            draw.rectangle([(0, y), (3, y + 17)], fill=EMPHASIS)

        fill = BLACK if is_next or is_high else SECONDARY
        font = fonts[16]

        draw.text((pad, y), label, font=font, fill=fill)
        draw.text((pad + 20, y), t['time'], font=font, fill=fill)
        draw.text((pad + 80, y), height, font=font, fill=fill)

        if t.get('coeff'):
            c_str = "C{}{}".format(t['coeff'], '*' if t.get('coeff_approx') else '')
            draw.text((pad + 145, y), c_str, font=font, fill=fill)

        y += 19

    # -- Next tide countdown --
    y += 2
    if next_idx is not None and next_idx < len(extremes):
        nt = extremes[next_idx]
        mins_until = int((nt['epoch'] - now) / 60)
        hours = mins_until // 60
        mins = mins_until % 60
        type_de = "HOCH" if nt['type'] == 'high' else "TIEF"
        next_str = "Naechste: {} {}h{:02d}".format(type_de, hours, mins)
        draw.text((pad, y), next_str, font=fonts[14], fill=EMPHASIS)
    y += 18

    # -- Tide curve --
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 2
    curve_h = h - y - 4
    if sea_level and curve_h > 40:
        _draw_tide_curve(draw, sea_level, (pad, y, w - 2 * pad, curve_h), fonts)

    return img
