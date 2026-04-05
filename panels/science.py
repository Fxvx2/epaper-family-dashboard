"""Science concept panel with domain, scientist, definition, and analogy."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "WISSEN", font=fonts[14], fill=TERTIARY)

    # Domain tag (right-aligned)
    domain = data.get('domain', '')
    if domain:
        dw = txt_w(fonts[14], domain)
        draw.text((w - dw - pad, pad), domain, font=fonts[14], fill=SECONDARY)

    y = pad + 18

    # Term
    term = data.get('term', '')
    draw.text((pad, y), term, font=fonts[20], fill=BLACK)

    # Scientist (next to term, smaller)
    scientist = data.get('scientist', '')
    if scientist:
        tw = txt_w(fonts[20], term)
        avail = w - tw - pad - 20
        if avail > 50:
            draw.text((pad + tw + 8, y + 4), scientist, font=fonts[14], fill=TERTIARY)
    y += 24

    # Definition (compact)
    definition = data.get('definition', '')
    lines = word_wrap(definition, fonts[14], w - 2 * pad)
    for line in lines[:2]:
        draw.text((pad, y), line, font=fonts[14], fill=SECONDARY)
        y += 16

    # Analogy (from LLM or static, emphasized)
    analogy = data.get('analogy', '')
    if analogy and y < h - 20:
        y += 2
        draw.line([(pad, y), (pad + 30, y)], fill=SEPARATOR)
        y += 4
        source = data.get('analogy_source', 'static')
        lines = word_wrap(analogy, fonts[14], w - 2 * pad)
        max_lines = (h - y - 4) // 16
        for line in lines[:max_lines]:
            draw.text((pad, y), line, font=fonts[14], fill=EMPHASIS)
            y += 16

    return img
