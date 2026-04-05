"""LLM-generated analogies for science concepts using Google Gemini free tier.

Google AI Studio provides free access to Gemini 2.0 Flash.
- Free tier: 1,500 requests/day, no credit card required
- We use 1 request/day (cached)
- Get a free API key at: https://aistudio.google.com/apikey

If GEMINI_API_KEY is not set in config.py, falls back to the static analogy
from science_de.json.
"""

import os
import json
from datetime import date

import requests

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
_cache = {'date': None, 'analogy': None, 'term': None}


def generate_analogy(term, definition):
    """Generate a kid-friendly analogy for a science concept using Gemini.

    Returns analogy string, or None if unavailable.
    Cached daily in cache/analogy.json.
    """
    today = date.today()

    # Check in-memory cache
    if _cache['date'] == today and _cache.get('term') == term:
        return _cache['analogy']

    # Check file cache
    cache_path = os.path.join(CACHE_DIR, 'analogy.json')
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if cached.get('date') == today.isoformat() and cached.get('term') == term:
                _cache.update({'date': today, 'term': term, 'analogy': cached['analogy']})
                return cached['analogy']
        except Exception:
            pass

    # Need API key
    try:
        import config
        api_key = getattr(config, 'GEMINI_API_KEY', '')
    except ImportError:
        return None

    if not api_key:
        return None

    try:
        prompt = (
            'Du bist ein Wissenschaftserklaerer fuer Kinder (9-11 Jahre). '
            'Erstelle eine kurze, anschauliche Analogie (maximal 1 Satz, '
            'hoechstens 120 Zeichen, auf Deutsch) fuer dieses Konzept. '
            'Verwende etwas aus dem Alltag eines Kindes. '
            'Antworte NUR mit der Analogie, ohne Einleitung.\n\n'
            'Konzept: {}\nDefinition: {}'.format(term, definition)
        )

        resp = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/'
            'gemini-2.5-flash:generateContent?key={}'.format(api_key),
            headers={'Content-Type': 'application/json'},
            json={
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 1500,
                },
            },
            timeout=20,
        )

        data = resp.json()
        analogy = data['candidates'][0]['content']['parts'][0]['text'].strip()

        # Cache it
        _cache.update({'date': today, 'term': term, 'analogy': analogy})
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({
                'date': today.isoformat(),
                'term': term,
                'analogy': analogy,
            }, f, ensure_ascii=False)

        print("Gemini analogy generated for: {}".format(term))
        return analogy

    except Exception as e:
        print("Gemini analogy error: {}".format(e))
        return None
