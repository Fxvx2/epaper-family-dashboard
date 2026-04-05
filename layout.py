"""Grid layout system for the 1200x825 family dashboard."""

from PIL import Image, ImageDraw, ImageFont

W = 1200
H = 825

# Grayscale style constants
BLACK = 0
EMPHASIS = 50
SECONDARY = 100
TERTIARY = 140
SEPARATOR = 190
WHITE = 255

# Panel definitions: (name, x, y, width, height)
# Layout: 3 columns, calendar spans right column rows 2-4
SCREEN1_PANELS = [
    ('weather_berlin',    0,   0,   400, 340),
    ('forecast_berlin',   400, 0,   400, 340),
    ('tides',             800, 0,   400, 340),
    ('weather_cartagena', 0,   340, 400, 200),
    ('transport',         400, 340, 400, 200),
    ('calendar',          800, 340, 400, 485),
    ('quote',             0,   540, 400, 145),
    ('famous_person',     400, 540, 400, 145),
    ('math_challenge',    0,   685, 400, 140),
    ('word_of_day',       400, 685, 400, 140),
]

SCREEN2_PANELS = [
    ('picture_of_day',   0,   0,   800,  500),
    ('shopping_list',    800, 0,   400,  500),
    ('joke',             0,   500, 300,  325),
    ('bjj',              300, 500, 300,  325),
    ('raetsel',          600, 500, 300,  325),
    ('science',          900, 500, 300,  325),
]

# Screen 3: Family calendar week view
SCREEN3_PANELS = [
    ('calendar_week',    0,   0,   1200, 825),
]


def load_fonts():
    """Load all font sizes for the dashboard."""
    return {
        14: ImageFont.truetype('fonts/arial.ttf', 14),
        16: ImageFont.truetype('fonts/arial.ttf', 16),
        18: ImageFont.truetype('fonts/arial.ttf', 18),
        20: ImageFont.truetype('fonts/arial.ttf', 20),
        24: ImageFont.truetype('fonts/arial.ttf', 24),
        28: ImageFont.truetype('fonts/arial.ttf', 28),
        36: ImageFont.truetype('fonts/arial.ttf', 36),
        56: ImageFont.truetype('fonts/arial.ttf', 56),
        'ic': ImageFont.truetype('fonts/meteocons-webfont.ttf', 36),
        'ic_big': ImageFont.truetype('fonts/meteocons-webfont.ttf', 72),
        'ic_sm': ImageFont.truetype('fonts/meteocons-webfont.ttf', 28),
    }


def txt_w(font, text):
    """Measure text width, compatible with Pillow 9.x and 10+."""
    try:
        b = font.getbbox(text)
        return b[2] - b[0]
    except AttributeError:
        return font.getsize(text)[0]


def txt_h(font, text='Ay'):
    """Measure text height."""
    try:
        b = font.getbbox(text)
        return b[3] - b[1]
    except AttributeError:
        return font.getsize(text)[1]


def word_wrap(text, font, max_width):
    """Wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = (current + ' ' + word).strip()
        if txt_w(font, test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def composite(display, panels_def, rendered_panels):
    """Composite rendered panel images onto the display frame buffer.

    Args:
        display: The display object (frame_buf is PIL Image 'L' mode)
        panels_def: List of (name, x, y, w, h) tuples
        rendered_panels: Dict of {name: PIL Image} for each panel
    """
    # Clear to white
    display.frame_buf.paste(WHITE, box=(0, 0, W, H))

    draw = ImageDraw.Draw(display.frame_buf)

    for name, x, y, w, h in panels_def:
        if name in rendered_panels and rendered_panels[name] is not None:
            display.frame_buf.paste(rendered_panels[name], (x, y))
        # Draw panel border
        draw.rectangle([(x, y), (x + w - 1, y + h - 1)], outline=SEPARATOR)


def render_placeholder(name, w, h, fonts):
    """Render an empty placeholder panel with a title label."""
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)

    # Panel title centered
    title = name.replace('_', ' ').upper()
    tw = txt_w(fonts[18], title)
    x = (w - tw) // 2
    draw.text((x, h // 2 - 10), title, font=fonts[18], fill=TERTIARY)

    return img
