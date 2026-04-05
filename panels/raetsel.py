"""Raetsel (riddle/mind game) panel renderer."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "RAETSEL", font=fonts[14], fill=TERTIARY)
    y = pad + 20

    question = data.get('question', '')
    answer = data.get('answer', '')

    # Question
    lines = word_wrap(question, fonts[16], w - 2 * pad)
    for line in lines[:4]:
        draw.text((pad, y), line, font=fonts[16], fill=BLACK)
        y += 20

    # Answer (very light — needs effort to read)
    y += 8
    lines = word_wrap(answer, fonts[14], w - 2 * pad)
    for line in lines[:2]:
        draw.text((pad, y), line, font=fonts[14], fill=SEPARATOR + 20)
        y += 18

    return img
