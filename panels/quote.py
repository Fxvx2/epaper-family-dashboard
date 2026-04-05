"""Quote/wisdom panel: German text + English translation below."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "WEISHEIT", font=fonts[14], fill=TERTIARY)
    y = pad + 18

    # German quote
    text = data.get('text', '')
    lines = word_wrap(text, fonts[16], w - 2 * pad)
    for line in lines[:3]:
        draw.text((pad, y), line, font=fonts[16], fill=BLACK)
        y += 19

    # English translation (lighter, smaller)
    en = data.get('en', '')
    if en:
        y += 1
        lines = word_wrap(en, fonts[14], w - 2 * pad)
        for line in lines[:2]:
            draw.text((pad, y), line, font=fonts[14], fill=TERTIARY)
            y += 16

    # Author + bio
    author = data.get('author', '')
    bio = data.get('bio', '')
    if author:
        y += 2
        attr = "-- {} ({})".format(author, bio) if bio else "-- {}".format(author)
        lines = word_wrap(attr, fonts[14], w - 2 * pad - 10)
        for line in lines[:1]:
            draw.text((pad + 10, y), line, font=fonts[14], fill=SECONDARY)

    return img
