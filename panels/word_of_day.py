"""Word of the day panel renderer."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 15

    # Title
    draw.text((pad, pad), "WORT DES TAGES", font=fonts[16], fill=TERTIARY)

    # Word + type
    word = data.get('word', '')
    wtype = data.get('type', '')
    y = pad + 24
    draw.text((pad, y), word, font=fonts[28], fill=BLACK)
    ww = txt_w(fonts[28], word)
    if wtype:
        draw.text((pad + ww + 10, y + 8), "({})".format(wtype), font=fonts[14], fill=TERTIARY)

    # Definition
    definition = data.get('definition', '')
    y += 36
    lines = word_wrap(definition, fonts[18], w - 2 * pad)
    for line in lines[:2]:
        draw.text((pad, y), line, font=fonts[18], fill=SECONDARY)
        y += 22

    # Example (italic-style: lighter gray)
    example = data.get('example', '')
    if example and y < h - 25:
        y += 4
        lines = word_wrap('"{}"'.format(example), fonts[16], w - 2 * pad)
        for line in lines[:1]:
            draw.text((pad, y), line, font=fonts[16], fill=TERTIARY)

    return img
