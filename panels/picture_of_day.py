"""Picture of the day panel renderer with legend."""

from PIL import Image, ImageDraw
from datetime import date
from layout import BLACK, SECONDARY, TERTIARY, SEPARATOR, WHITE, txt_w, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    if not data or not data.get('image'):
        draw.text((w // 2 - 80, h // 2), "Kein Bild verfuegbar",
                  font=fonts[18], fill=TERTIARY)
        return img

    title = data.get('title', '')
    photo = data['image']

    # Reserve space for legend at bottom
    legend_h = 50
    img_h = h - legend_h

    # Header
    draw.text((pad, pad), "BILD DES TAGES", font=fonts[14], fill=TERTIARY)
    ds = date.today().strftime('%d/%m/%Y')
    dw = txt_w(fonts[14], ds)
    draw.text((w - dw - pad, pad), ds, font=fonts[14], fill=TERTIARY)

    # Scale photo to fit, maintaining aspect ratio
    photo_top = pad + 20
    avail_h = img_h - photo_top
    pw, ph = photo.size
    scale = min((w - 2 * pad) / pw, avail_h / ph)
    new_w = int(pw * scale)
    new_h = int(ph * scale)
    photo_resized = photo.resize((new_w, new_h), Image.LANCZOS)

    # Center the photo
    x_off = (w - new_w) // 2
    y_off = photo_top + (avail_h - new_h) // 2
    img.paste(photo_resized, (x_off, y_off))

    # Legend bar at bottom
    legend_y = h - legend_h
    draw.rectangle([(0, legend_y), (w, h)], fill=WHITE)
    draw.line([(pad, legend_y + 2), (w - pad, legend_y + 2)], fill=SEPARATOR)

    # Title
    y = legend_y + 6
    if title:
        lines = word_wrap(title, fonts[16], w - 2 * pad)
        for line in lines[:1]:
            draw.text((pad, y), line, font=fonts[16], fill=BLACK)
            y += 20

    # Description / location
    description = data.get('description', '')
    if description:
        lines = word_wrap(description, fonts[14], w - 2 * pad - 120)
        for line in lines[:1]:
            draw.text((pad, y), line, font=fonts[14], fill=SECONDARY)

    # Source label
    source = data.get('source', 'Wikimedia Commons')
    draw.text((w - txt_w(fonts[14], source) - pad, legend_y + 8),
              source, font=fonts[14], fill=TERTIARY)

    return img
