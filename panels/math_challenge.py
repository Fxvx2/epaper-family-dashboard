"""Math challenge panel renderer for Screen 2."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 15

    draw.text((pad, pad), "MATHE-CHALLENGE", font=fonts[20], fill=BLACK)
    y = pad + 28

    problems = data.get('problems', [])
    if not problems:
        return img

    for i, p in enumerate(problems):
        level = p.get('level', '')
        question = p.get('question', '')
        answer = p.get('answer', '')

        # Level label
        level_fills = {'leicht': SECONDARY, 'mittel': EMPHASIS, 'schwer': BLACK}
        draw.text((pad, y), level.upper(), font=fonts[14], fill=level_fills.get(level, SECONDARY))
        y += 18

        # Question (large)
        draw.text((pad + 10, y), question, font=fonts[24], fill=BLACK)

        # Answer (upside-down text hint, small, right-aligned)
        ans_str = "Antwort: {}".format(answer)
        aw = txt_w(fonts[14], ans_str)
        draw.text((w - aw - pad, y + 8), ans_str, font=fonts[14], fill=SEPARATOR + 30)

        y += 35

        if i < len(problems) - 1:
            draw.line([(pad, y - 5), (w - pad, y - 5)], fill=SEPARATOR)

    return img
