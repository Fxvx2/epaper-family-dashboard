"""Joke panel renderer (Flachwitze for kids)."""

from PIL import Image, ImageDraw
from layout import BLACK, EMPHASIS, SECONDARY, TERTIARY, SEPARATOR, WHITE, word_wrap


def render(data, fonts, bbox):
    w, h = bbox
    img = Image.new('L', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    pad = 10

    draw.text((pad, pad), "WITZ DES TAGES", font=fonts[14], fill=TERTIARY)
    y = pad + 20

    question = data.get('question', '')
    answer = data.get('answer', '')

    # Question
    lines = word_wrap(question, fonts[18], w - 2 * pad)
    for line in lines[:3]:
        draw.text((pad, y), line, font=fonts[18], fill=BLACK)
        y += 22

    # Answer (light gray — readable but not immediately obvious)
    y += 8
    lines = word_wrap(answer, fonts[16], w - 2 * pad)
    for line in lines[:2]:
        draw.text((pad, y), line, font=fonts[16], fill=SEPARATOR + 10)
        y += 20

    return img
