"""Element of the day -- periodic table with Gemini kid-friendly explanation."""

import os
import json
import hashlib
from datetime import date

from data.gemini import call_gemini

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static', 'elements.json')
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'element_info.json')

_elements = None


def _load_elements():
    global _elements
    if _elements is None:
        with open(STATIC_PATH) as f:
            _elements = json.load(f)
    return _elements


def _daily_index(n, seed='element'):
    """Sequential daily rotation: every item shown once before any repeat."""
    offset = int(hashlib.md5(seed.encode()).hexdigest(), 16) % n
    return (date.today().toordinal() + offset) % n


def get_element_of_day():
    """Return today's element with Gemini-generated descriptions."""
    elements = _load_elements()
    el = elements[_daily_index(len(elements))]

    # Enrich with Gemini (cached per day)
    cached = _load_cache()
    today = date.today().isoformat()
    if cached.get('date') == today and cached.get('symbol') == el['symbol']:
        el = dict(el)
        el['description_de'] = cached.get('description_de', '')
        el['description_en'] = cached.get('description_en', '')
        el['uses'] = cached.get('uses', [])
        el['fun_fact'] = cached.get('fun_fact', '')
        el['molecular_formulas'] = cached.get('molecular_formulas', [])
        el['structural'] = cached.get('structural', '')
        el['period'] = cached.get('period', '')
        el['group'] = cached.get('group', '')
        el['electron_config'] = cached.get('electron_config', '')
        return el

    enrich = _enrich_with_gemini(el)
    el = dict(el)
    el.update(enrich)

    # Only cache if we got real data (at least description present)
    if enrich.get('description_de'):
        _save_cache({
            'date': today,
            'symbol': el['symbol'],
            'description_de': enrich.get('description_de', ''),
            'description_en': enrich.get('description_en', ''),
            'uses': enrich.get('uses', []),
            'fun_fact': enrich.get('fun_fact', ''),
            'molecular_formulas': enrich.get('molecular_formulas', []),
            'structural': enrich.get('structural', ''),
            'period': enrich.get('period', ''),
            'group': enrich.get('group', ''),
            'electron_config': enrich.get('electron_config', ''),
        })
    return el


def _enrich_with_gemini(el, retries=2):
    """Ask Gemini (Claude fallback) for kid-friendly descriptions + facts."""
    prompt = (
        "Explique cet element chimique pour enfants (8-11 ans) en allemand ET anglais. "
        "Reponse UNIQUEMENT en JSON avec ces cles: "
        "'description_de' (2 phrases courtes, allemand, niveau enfant, ae/oe/ue/ss), "
        "'description_en' (2 short sentences, English, kid level), "
        "'uses' (liste de 3 utilisations quotidiennes en allemand, ae/oe/ue/ss), "
        "'fun_fact' (1 fait amusant en allemand, ae/oe/ue/ss), "
        "'molecular_formulas' (liste de 3 molecules connues avec l'element, "
        "format 'formule - nom allemand'. UTILISE LES INDICES UNICODE: "
        "H₂O au lieu de H2O, CO₂, C₆H₁₂O₆, NH₃. "
        "Exemple: 'H₂O - Wasser'), "
        "'structural' (1 representation textuelle simple d'une molecule, "
        "ex pour H: 'H-O-H (Wasser)' ou 'H-H (Wasserstoffgas)'), "
        "'period' (numero de periode), "
        "'group' (numero de groupe), "
        "'electron_config' (configuration electronique avec exposants Unicode, "
        "ex: '1s² 2s² 2p⁴'). "
        "Pour les textes allemands utilise ae/oe/ue/ss, pas d'accents."
        "\n\nElement: {} ({}), numero atomique {}, categorie {}".format(
            el['name_en'], el['symbol'], el['number'], el['category'])
    )
    result = call_gemini(prompt, max_tokens=2000, retries=retries)
    if not result:
        return {}
    return {
        'description_de': result.get('description_de', ''),
        'description_en': result.get('description_en', ''),
        'uses': result.get('uses', []) or [],
        'fun_fact': result.get('fun_fact', ''),
        'molecular_formulas': result.get('molecular_formulas', []) or [],
        'structural': result.get('structural', ''),
        'period': str(result.get('period', '')),
        'group': str(result.get('group', '')),
        'electron_config': result.get('electron_config', ''),
    }


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
