"""Daily content loader: quotes, famous persons, science concepts, words."""

import os
import json
import hashlib
from datetime import date, timedelta

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
    """Sequential daily rotation: every item shown once before any repeat.

    Same item all day, advances by one each midnight. A per-seed offset keeps
    different categories out of lockstep so equal-sized pools don't correlate.
    """
    n = len(collection)
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % n
    return (date.today().toordinal() + offset) % n


def _weekly_index(collection, seed='default'):
    """Sequential weekly rotation: advances by one each Monday, full coverage."""
    n = len(collection)
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_no = monday.toordinal() // 7
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % n
    return (week_no + offset) % n


def get_daily_content():
    """Return today's daily content for all 4 panels.

    Returns dict with keys: 'quote', 'famous_person', 'science', 'word_of_day'
    """
    result = {}

    # Quote
    quotes = _load_json('quotes_de.json')
    if quotes:
        result['quote'] = quotes[_daily_index(quotes, 'quote')]

    # Famous person (Wikipedia "On this day" API, fallback to static list)
    try:
        from data.onthisday import fetch_person_of_day
        person = fetch_person_of_day()
        if person:
            result['famous_person'] = person
    except Exception:
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

    # Joke (pick 2 for the day)
    jokes = _load_json('jokes_de.json')
    if jokes:
        idx1 = _daily_index(jokes, 'joke')
        idx2 = _daily_index(jokes, 'joke2')
        if idx2 == idx1:
            idx2 = (idx1 + 1) % len(jokes)
        result['joke'] = {
            'primary': jokes[idx1],
            'secondary': jokes[idx2],
        }

    # Raetsel (pick 2 for the day)
    raetsel = _load_json('raetsel_de.json')
    if raetsel:
        idx1 = _daily_index(raetsel, 'raetsel')
        idx2 = _daily_index(raetsel, 'raetsel2')
        if idx2 == idx1:
            idx2 = (idx1 + 1) % len(raetsel)
        result['raetsel'] = {
            'primary': raetsel[idx1],
            'secondary': raetsel[idx2],
        }

    # Buchzitat
    buchzitate = _load_json('buchzitate.json')
    if buchzitate:
        result['buchzitat'] = buchzitate[_daily_index(buchzitate, 'buchzitat')]

    # Fun fact
    funfacts = _load_json('funfacts_de.json')
    if funfacts:
        result['funfact'] = funfacts[_daily_index(funfacts, 'funfact')]

    # Weltrekord
    weltrekorde = _load_json('weltrekorde.json')
    if weltrekorde:
        result['weltrekord'] = weltrekorde[_daily_index(weltrekorde, 'weltrekord')]

    # Cheese of the day
    try:
        cheeses = _load_json('cheeses.json')
        if cheeses:
            result['cheese'] = cheeses[_daily_index(cheeses, 'cheese')]
    except Exception:
        pass

    # KW label for weekly panels
    today = date.today()
    kw = "KW{}".format(today.isocalendar()[1])

    # Vegetarian recipe of the week
    recipes = _load_json('recipes_veggie.json')
    if recipes:
        r = dict(recipes[_weekly_index(recipes, 'recipe')])
        r['kw'] = kw
        result['recipe'] = r

    # Dessert of the week (to cook with kids)
    desserts = _load_json('desserts_kids.json')
    if desserts:
        d = dict(desserts[_weekly_index(desserts, 'dessert')])
        d['kw'] = kw
        result['dessert'] = d

    return result
