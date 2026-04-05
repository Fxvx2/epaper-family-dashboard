"""BJJ move of the day panel renderer."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    # Header
    draw.text((pad, pad), "BJJ MOVE", font=fonts[14], fill=TERTIARY)

    # Belt level tag (right)
    level = data.get('level', '')
    if level:
        lw = txt_w(fonts[14], level)
        draw.text((w - lw - pad, pad), level, font=fonts[14], fill=SECONDARY)

    y = pad + 18

    # Move name
    name = data.get('name', '')
    draw.text((pad, y), name, font=fonts[18], fill=BLACK)
    y += 24

    # Category
    category = data.get('category', '')
    if category:
        draw.text((pad, y), category, font=fonts[14], fill=TERTIARY)
        y += 18

    # Description (word-wrapped)
    desc = data.get('description', '')
    max_lines = (h - y - 4) // 17
    lines = word_wrap(desc, fonts[14], w - 2 * pad)
    for line in lines[:max_lines]:
        draw.text((pad, y), line, font=fonts[14], fill=SECONDARY)
        y += 17

    return img
