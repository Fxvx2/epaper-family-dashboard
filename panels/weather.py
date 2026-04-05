"""Weather panel renderer -- adapts layout based on panel height."""

import time as _time
from PIL import Image, ImageDraw
from datetime import datetime
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w
from data.weather import wind_str, wind_dir

DEG = chr(0xb0)


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    compact = h < 250  # compact mode for smaller panels (e.g. Cartagena 400x200)
    name = data.get('display_name', data.get('location', ''))
    pad = 10
    y = pad
    fmt = lambda ts: _time.strftime('%H:%M', _time.localtime(ts))

    # -- Header --
    draw.text((pad, y), name, font=fonts[24], fill=BLACK)
    date_str = datetime.now().strftime('%d/%m')
    dw = txt_w(fonts[16], date_str)
    draw.text((w - dw - pad, y + 4), date_str, font=fonts[16], fill=TERTIARY)

    # -- Weather icon --
    icon = data.get('icon', ')')
    if compact:
        iw = txt_w(fonts['ic'], icon)
        draw.text((w - iw - pad, y), icon, font=fonts['ic'], fill=BLACK)
    else:
        iw = txt_w(fonts['ic_big'], icon)
        draw.text((w - iw - pad, y + 28), icon, font=fonts['ic_big'], fill=BLACK)

    y += 30

    # -- Description --
    desc = data['description'].capitalize()
    draw.text((pad, y), desc, font=fonts[16] if compact else fonts[18], fill=SECONDARY)
    y += 20 if compact else 24
    draw.line([(pad, y), (w - 80, y)], fill=SEPARATOR)
    y += 4

    if compact:
        # -- Compact: temp big, info dense --
        temp_str = "{}{}C".format(data['temp'], DEG)
        draw.text((pad, y), temp_str, font=fonts[36], fill=BLACK)
        tw = txt_w(fonts[36], temp_str)
        col2 = tw + 20
        if data.get('feels_like') is not None:
            draw.text((col2, y + 2), "Feels {}{}".format(
                int(round(data['feels_like'])), DEG), font=fonts[14], fill=SECONDARY)
        draw.text((col2, y + 18), "{}% RH".format(data['humidity']),
                  font=fonts[14], fill=BLACK)
        y += 44

        # Pressure + Wind
        draw.text((pad, y), "{} hPa".format(data['pressure']),
                  font=fonts[14], fill=SECONDARY)
        draw.text((pad + 100, y), "{} {}".format(
            wind_str(data['wind_speed']), wind_dir(data['wind_deg'])),
                  font=fonts[14], fill=SECONDARY)
        y += 18

        # Clouds + Rain
        cloud_rain = "Wolken {}%".format(data['clouds'])
        if data.get('rain') and data['rain'] > 0:
            cloud_rain += "  Regen {:.1f}mm".format(data['rain'])
        draw.text((pad, y), cloud_rain, font=fonts[14], fill=SECONDARY)
        y += 18

        # Sunrise/sunset
        draw.text((pad, y), "A", font=fonts['ic_sm'], fill=EMPHASIS)
        draw.text((pad + 26, y + 2), fmt(data['sunrise']), font=fonts[14], fill=BLACK)
        draw.text((pad + 100, y), "J", font=fonts['ic_sm'], fill=EMPHASIS)
        draw.text((pad + 126, y + 2), fmt(data['sunset']), font=fonts[14], fill=BLACK)

        # Updated
        draw.text((pad, h - 16), "Updated: {}".format(fmt(data['reftime'])),
                  font=fonts[14], fill=TERTIARY)
    else:
        # -- Full: standard layout --
        temp_str = "{}{}C".format(data['temp'], DEG)
        draw.text((pad, y), temp_str, font=fonts[56], fill=BLACK)
        if data.get('feels_like') is not None:
            draw.text((pad + 200, y + 20), "Feels {}{}".format(
                int(round(data['feels_like'])), DEG), font=fonts[18], fill=SECONDARY)
        y += 68

        # Min/Max + Humidity
        draw.text((pad, y), "Lo {}{} Hi {}{}".format(
            data['temp_min'], DEG, data['temp_max'], DEG), font=fonts[18], fill=BLACK)
        draw.text((w // 2 + 10, y), "{}% RH".format(data['humidity']),
                  font=fonts[18], fill=BLACK)
        y += 26
        draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
        y += 6

        # Pressure + Wind
        draw.text((pad, y), "{} hPa".format(data['pressure']), font=fonts[18], fill=BLACK)
        w_text = "{} {}".format(wind_str(data['wind_speed']), wind_dir(data['wind_deg']))
        draw.text((w // 2 + 10, y), w_text, font=fonts[16], fill=BLACK)
        y += 24

        # Clouds + Rain
        draw.text((pad, y), "Wolken {}%".format(data['clouds']), font=fonts[16], fill=SECONDARY)
        if data.get('rain') and data['rain'] > 0:
            draw.text((w // 2 + 10, y), "Regen {:.1f} mm".format(data['rain']),
                      font=fonts[16], fill=SECONDARY)
        y += 22
        draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
        y += 6

        # Sunrise / Sunset
        draw.text((pad, y), "A", font=fonts['ic_sm'], fill=EMPHASIS)
        draw.text((pad + 30, y + 2), fmt(data['sunrise']), font=fonts[16], fill=BLACK)
        draw.text((w // 2 + 10, y), "J", font=fonts['ic_sm'], fill=EMPHASIS)
        draw.text((w // 2 + 40, y + 2), fmt(data['sunset']), font=fonts[16], fill=BLACK)
        y += 26

        # Updated
        draw.text((pad, h - 20), "Updated: {}".format(fmt(data['reftime'])),
                  font=fonts[14], fill=TERTIARY)

    return img
