"""3-day weather forecast panel renderer."""

from PIL import Image, ImageDraw
from datetime import datetime
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w
from data.weather import wind_str

DEG = chr(0xb0)


def render(data, fonts, bbox):
    """Render 3-day forecast panel.

    Args:
        data: list of day dicts from fetch_forecast()
        fonts: dict of loaded fonts
        bbox: (width, height) of panel area
    """
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    pad = 10
    y = pad

    # -- Header --
    draw.text((pad, y), "VORHERSAGE", font=fonts[24], fill=BLACK)
    ds = datetime.now().strftime('%d/%m')
    dw = txt_w(fonts[16], ds)
    draw.text((w - dw - pad, y + 4), ds, font=fonts[16], fill=TERTIARY)
    y += 30
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 8

    if not data:
        draw.text((pad, y), "Keine Vorhersage", font=fonts[18], fill=TERTIARY)
        return img

    # -- 3 day cards --
    row_h = (h - y - 20) // 3

    for i, day in enumerate(data[:3]):
        row_y = y + i * row_h

        # Weather icon
        draw.text((pad, row_y), day['icon'], font=fonts['ic'], fill=BLACK)

        # Day + date
        day_str = "{} {}".format(day['day'], day['date'])
        draw.text((pad + 45, row_y + 2), day_str, font=fonts[20], fill=BLACK)

        # Temp range
        temps = "{}{} / {}{}".format(day['tmax'], DEG, day['tmin'], DEG)
        draw.text((pad + 45, row_y + 28), temps, font=fonts[20], fill=BLACK)

        # Description
        desc = day['desc'][:22]
        draw.text((pad + 45, row_y + 54), desc, font=fonts[16], fill=SECONDARY)

        # Wind
        w_text = wind_str(day['wind'])
        ww = txt_w(fonts[16], w_text)
        draw.text((w - ww - pad, row_y + 54), w_text, font=fonts[16], fill=SECONDARY)

        # Separator between days
        if i < 2:
            sep_y = row_y + row_h - 4
            draw.line([(pad + 20, sep_y), (w - pad - 20, sep_y)], fill=SEPARATOR)

    return img
