"""Daily words of the day: synonyms for DE word + new ES and FR words via Gemini."""

import os
import json
import hashlib
from datetime import date

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'multilingual_words.json')


# Curated Spanish & French word lists (fallback if Gemini fails)
SPANISH_WORDS = [
    'madrugada', 'sobremesa', 'desvelado', 'duende', 'friolero', 'empalagar',
    'pundonor', 'merendar', 'trasnochar', 'apapachar', 'entrecejo', 'tocayo',
    'vergueenza', 'estrenar', 'anteayer', 'lampino', 'manco', 'tuerto',
    'canoso', 'zurdo', 'tartamudo', 'pichon', 'aguila', 'mariposa',
    'crepusculo', 'alborada', 'tenue', 'vidrioso', 'saltamontes', 'relampago',
]

FRENCH_WORDS = [
    'fleurir', 'emerveiller', 'flaneur', 'depaysement', 'retrouvailles',
    'chatoyer', 'effleurer', 'bruissement', 'serein', 'chuchoter',
    'scintiller', 'arpenter', 'esquisser', 'melancolique', 'frissonner',
    'cascade', 'aurore', 'ecume', 'bourgeonner', 'carillon',
    'voluptueux', 'luminescent', 'ephemere', 'vertige', 'murmure',
    'clairiere', 'velours', 'fougere', 'libellule', 'brume',
]


def _daily_index(seq, seed):
    """Sequential daily rotation: every word shown once before any repeat."""
    n = len(seq)
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % n
    return (date.today().toordinal() + offset) % n


def get_multilingual():
    """Return {'synonyms_de': [...], 'word_es': {...}, 'word_fr': {...}}."""
    cached = _load_cache()
    today = date.today().isoformat()
    if cached.get('date') == today:
        return cached

    es_word = SPANISH_WORDS[_daily_index(SPANISH_WORDS, 'es')]
    fr_word = FRENCH_WORDS[_daily_index(FRENCH_WORDS, 'fr')]

    # Get German word of day (same index as content.py uses)
    de_word = _get_de_word()

    from data.gemini import call_gemini

    # Spanish word: definitions in ES + FR + EN + translation to DE
    es_result = call_gemini(
        "Fuer dieses spanische Wort: " + es_word + "\n\n"
        "Antworte NUR in JSON (ASCII, ae/oe/ue/ss, keine Akzente) mit:\n"
        "- 'definition_es' (Definition auf Spanisch, 1 Satz)\n"
        "- 'definition_fr' (Definition auf Franzoesisch, 1 Satz)\n"
        "- 'definition_de' (Definition auf Deutsch, 1 Satz)\n"
        "- 'definition_en' (Definition in English, 1 sentence)\n"
        "- 'translation_de' (Deutsche Uebersetzung, 1-3 Woerter)\n"
        "- 'translation_fr' (Franzoesische Uebersetzung, 1-3 Woerter)\n"
        "- 'translation_en' (English translation, 1-3 words)\n"
        "- 'example_es' (1 kurzer Beispielsatz auf Spanisch)",
        max_tokens=2500,
    )
    word_es = {
        'word': es_word,
        'lang': 'ES',
        'definition_es': (es_result or {}).get('definition_es', ''),
        'definition_fr': (es_result or {}).get('definition_fr', ''),
        'definition_de': (es_result or {}).get('definition_de', ''),
        'definition_en': (es_result or {}).get('definition_en', ''),
        'translation_de': (es_result or {}).get('translation_de', ''),
        'translation_fr': (es_result or {}).get('translation_fr', ''),
        'translation_en': (es_result or {}).get('translation_en', ''),
        'example_es': (es_result or {}).get('example_es', ''),
    }

    # French word: definitions in FR + ES + EN + translation to DE
    fr_result = call_gemini(
        "Fuer dieses franzoesische Wort: " + fr_word + "\n\n"
        "Antworte NUR in JSON (ASCII, ae/oe/ue/ss, keine Akzente) mit:\n"
        "- 'definition_fr' (Definition auf Franzoesisch, 1 Satz)\n"
        "- 'definition_es' (Definition auf Spanisch, 1 Satz)\n"
        "- 'definition_de' (Definition auf Deutsch, 1 Satz)\n"
        "- 'definition_en' (Definition in English, 1 sentence)\n"
        "- 'translation_de' (Deutsche Uebersetzung, 1-3 Woerter)\n"
        "- 'translation_es' (Spanische Uebersetzung, 1-3 Woerter)\n"
        "- 'translation_en' (English translation, 1-3 words)\n"
        "- 'example_fr' (1 kurzer Beispielsatz auf Franzoesisch)",
        max_tokens=2500,
    )
    word_fr = {
        'word': fr_word,
        'lang': 'FR',
        'definition_fr': (fr_result or {}).get('definition_fr', ''),
        'definition_es': (fr_result or {}).get('definition_es', ''),
        'definition_de': (fr_result or {}).get('definition_de', ''),
        'definition_en': (fr_result or {}).get('definition_en', ''),
        'translation_de': (fr_result or {}).get('translation_de', ''),
        'translation_es': (fr_result or {}).get('translation_es', ''),
        'translation_en': (fr_result or {}).get('translation_en', ''),
        'example_fr': (fr_result or {}).get('example_fr', ''),
    }

    # Synonyms + translations for the German word
    synonyms_de = []
    de_translation_es = ''
    de_translation_fr = ''
    de_translation_en = ''
    de_example_es = ''
    de_example_fr = ''
    if de_word:
        syn_result = call_gemini(
            "Fuer dieses deutsche Wort: \"" + de_word + "\"\n"
            "Antworte NUR in JSON (ASCII, ae/oe/ue/ss, keine Akzente) mit:\n"
            "- 'synonyme' (Liste von 3 deutschen Synonymen, kurz)\n"
            "- 'translation_es' (spanische Uebersetzung, 1-3 Woerter)\n"
            "- 'translation_fr' (franzoesische Uebersetzung, 1-3 Woerter)\n"
            "- 'translation_en' (English translation, 1-3 words)\n"
            "- 'example_es' (Beispielsatz mit dem Wort auf Spanisch)\n"
            "- 'example_fr' (Beispielsatz mit dem Wort auf Franzoesisch)",
            max_tokens=3000,
        )
        synonyms_de = (syn_result or {}).get('synonyme', []) or []
        de_translation_es = (syn_result or {}).get('translation_es', '')
        de_translation_fr = (syn_result or {}).get('translation_fr', '')
        de_translation_en = (syn_result or {}).get('translation_en', '')
        de_example_es = (syn_result or {}).get('example_es', '')
        de_example_fr = (syn_result or {}).get('example_fr', '')

    out = {
        'date': today,
        'synonyms_de': synonyms_de,
        'de_translation_es': de_translation_es,
        'de_translation_fr': de_translation_fr,
        'de_translation_en': de_translation_en,
        'de_example_es': de_example_es,
        'de_example_fr': de_example_fr,
        'word_es': word_es,
        'word_fr': word_fr,
    }
    # Only cache if we got real content
    if synonyms_de or word_es.get('definition_es') or word_fr.get('definition_fr'):
        _save_cache(out)
    return out


def _get_de_word():
    """Get today's German word (same logic as content.py)."""
    try:
        from data.content import _load_json, _daily_index as _cdi
        words = _load_json('words_de.json')
        if words:
            w = words[_cdi(words, 'word')]
            return w.get('word', '')
    except Exception:
        pass
    return ''


def _load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_cache(data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass
