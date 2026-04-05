"""Famous person of the day panel renderer."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "PERSON DES TAGES", font=fonts[14], fill=TERTIARY)
    y = pad + 18

    # Name
    name = data.get('name', '')
    draw.text((pad, y), name, font=fonts[20], fill=BLACK)
    nw = txt_w(fonts[20], name)

    # Years + country
    years = data.get('years', '')
    country = data.get('country', '')
    meta = "({}, {})".format(years, country) if country else "({})".format(years)
    draw.text((pad + nw + 8, y + 4), meta, font=fonts[14], fill=SECONDARY)
    y += 28

    # Known for (word-wrapped)
    known = data.get('known_for', '')
    max_lines = (h - y - 4) // 20
    lines = word_wrap(known, fonts[16], w - 2 * pad)
    for line in lines[:max_lines]:
        draw.text((pad, y), line, font=fonts[16], fill=SECONDARY)
        y += 20

    return img
