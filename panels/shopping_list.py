"""Shopping list panel — fetches from Bring! app API."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "EINKAUFSLISTE", font=fonts[18], fill=BLACK)
    y = pad + 26
    draw.line([(pad, y), (w - pad, y)], fill=SEPARATOR)
    y += 6

    # Fetch from Bring! API
    try:
        from data.bring_api import fetch_shopping_list
        items = fetch_shopping_list()
    except Exception:
        items = None

    if not items:
        draw.text((pad, y + 10), "Liste leer", font=fonts[16], fill=TERTIARY)
        return img

    for i, item in enumerate(items[:18]):
        if y > h - 20:
            draw.text((pad, y), "... +{}".format(len(items) - i),
                      font=fonts[14], fill=TERTIARY)
            break

        # Checkbox
        draw.rectangle([(pad, y + 2), (pad + 12, y + 14)], outline=SECONDARY)

        # Item
        draw.text((pad + 18, y), item, font=fonts[16], fill=BLACK)
        y += 22

    return img
