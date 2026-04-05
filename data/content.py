"""Daily content loader: quotes, famous persons, science concepts, words."""

import os
import json
import hashlib
from datetime import date

_loaded = {}
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def _load_json(filename):
    """Load a JSON file from the static directory. Cached after first load."""
    if filename in _loaded:
        return _loaded[filename]
    path = os.path.join(STATIC_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _loaded[filename] = data
    return data


def _daily_index(collection, seed='default'):
    """Deterministic daily index: same item all day, changes at midnight."""
    day_str = date.today().isoformat() + seed
    h = int(hashlib.md5(day_str.encode()).hexdigest(), 16)
    return h % len(collection)


def get_daily_content():
    """Return today's daily content for all 4 panels.

    Returns dict with keys: 'quote', 'famous_person', 'science', 'word_of_day'
    """
    result = {}

    # Quote
    quotes = _load_json('quotes_de.json')
    if quotes:
        result['quote'] = quotes[_daily_index(quotes, 'quote')]

    # Famous person
    persons = _load_json('persons.json')
    if persons:
        result['famous_person'] = persons[_daily_index(persons, 'person')]

    # Science concept
    science = _load_json('science_de.json')
    if science:
        concept = science[_daily_index(science, 'science')]
        # Try LLM-generated analogy (falls back to static)
        try:
            from data.llm_analogy import generate_analogy
            llm_analogy = generate_analogy(concept.get('term', ''),
                                            concept.get('definition', ''))
            if llm_analogy:
                concept = dict(concept)  # don't mutate original
                concept['analogy'] = llm_analogy
                concept['analogy_source'] = 'llm'
        except Exception:
            pass
        result['science'] = concept

    # Word of the day
    words = _load_json('words_de.json')
    if words:
        result['word_of_day'] = words[_daily_index(words, 'word')]

    # BJJ move
    bjj = _load_json('bjj_moves.json')
    if bjj:
        result['bjj'] = bjj[_daily_index(bjj, 'bjj')]

    # Joke
    jokes = _load_json('jokes_de.json')
    if jokes:
        result['joke'] = jokes[_daily_index(jokes, 'joke')]

    # Raetsel
    raetsel = _load_json('raetsel_de.json')
    if raetsel:
        result['raetsel'] = raetsel[_daily_index(raetsel, 'raetsel')]

    return result
