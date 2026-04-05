"""Tide data fetching from Stormglass.io + SHOM coefficients."""

import time
from datetime import datetime, timedelta
from calendar import timegm
from collections import defaultdict

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

import os
import json as _json

_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
_tide_cache = {'date': None, 'data': None}
_shom_cache = {'date': None, 'data': None}


def _save_cache(name, data_dict):
    os.makedirs(_CACHE_DIR, exist_ok=True)
    with open(os.path.join(_CACHE_DIR, name), 'w') as f:
        _json.dump(data_dict, f)


def _load_cache(name):
    path = os.path.join(_CACHE_DIR, name)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return _json.load(f)
    return None


def fetch_tides():
    """Fetch tide extremes from Stormglass.io. Cached daily."""
    import config

    today = datetime.now().date()
    if _tide_cache['date'] == today and _tide_cache['data']:
        return _tide_cache['data']

    if not getattr(config, 'STORMGLASS_API_KEY', '') or not HAS_REQUESTS:
        return None

    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=2)

    resp = requests.get(
        'https://api.stormglass.io/v2/tide/extremes/point',
        params={
            'lat': config.TIDE_LAT,
            'lng': config.TIDE_LNG,
            'start': start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end.strftime('%Y-%m-%dT%H:%M:%S'),
        },
        headers={'Authorization': config.STORMGLASS_API_KEY},
        timeout=15,
    )
    data = resp.json()

    tides = []
    for item in data.get('data', []):
        ts_str = item['time'][:19]
        epoch = timegm(time.strptime(ts_str, '%Y-%m-%dT%H:%M:%S'))
        tides.append({
            'time': time.strftime('%H:%M', time.localtime(epoch)),
            'height': item['height'],
            'type': item['type'],
            'epoch': epoch,
        })

    _tide_cache['date'] = today
    _tide_cache['data'] = tides
    _save_cache('tides.json', {'date': str(today), 'data': tides})
    print("Tides fetched: {} entries (API quota: {}/{})".format(
        len(tides),
        data.get('meta', {}).get('requestCount', '?'),
        data.get('meta', {}).get('dailyQuota', '?')))
    return tides


_sealevel_cache = {'date': None, 'data': None}


def fetch_sea_level():
    """Fetch hourly sea level data from Stormglass for tide curve. Cached daily."""
    import config

    today = datetime.now().date()
    if _sealevel_cache['date'] == today and _sealevel_cache['data']:
        return _sealevel_cache['data']

    if not getattr(config, 'STORMGLASS_API_KEY', '') or not HAS_REQUESTS:
        return None

    try:
        start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=36)

        resp = requests.get(
            'https://api.stormglass.io/v2/tide/sea-level/point',
            params={
                'lat': config.TIDE_LAT,
                'lng': config.TIDE_LNG,
                'start': start.strftime('%Y-%m-%dT%H:%M:%S'),
                'end': end.strftime('%Y-%m-%dT%H:%M:%S'),
            },
            headers={'Authorization': config.STORMGLASS_API_KEY},
            timeout=15,
        )
        data = resp.json()

        points = []
        for item in data.get('data', []):
            ts_str = item['time'][:19]
            epoch = timegm(time.strptime(ts_str, '%Y-%m-%dT%H:%M:%S'))
            # Use 'sg' source, fallback to first available
            sg = item.get('sg', item.get('msl'))
            if sg is not None:
                points.append({
                    'epoch': epoch,
                    'height': sg,
                    'hour': time.strftime('%H', time.localtime(epoch)),
                })

        _sealevel_cache['date'] = today
        _sealevel_cache['data'] = points
        _save_cache('sealevel.json', {'date': str(today), 'data': points})
        print("Sea level fetched: {} points".format(len(points)))
        return points

    except Exception as e:
        print("Sea level API error: {}".format(e))
        if _sealevel_cache.get('data'):
            return _sealevel_cache['data']
        cached = _load_cache('sealevel.json')
        if cached and cached.get('date') == str(today):
            return cached['data']
        return None


def _get_utc_offset():
    lt = time.localtime()
    if lt.tm_isdst and time.daylight:
        return -time.altzone // 3600
    return -time.timezone // 3600


def fetch_shom_coefficients():
    """Fetch official tide coefficients from SHOM free portal API.

    Coefficients are universal across all French ports.
    Cached daily.
    """
    today = datetime.now().date()
    if _shom_cache['date'] == today and _shom_cache['data']:
        return _shom_cache['data']

    if not HAS_REQUESTS:
        return None

    try:
        utc = _get_utc_offset()
        resp = requests.get(
            'https://services.data.shom.fr/b2q8lrcdl4s04cbabsj4nhcb/hdm/spm/hlt',
            params={
                'harborName': 'BREST',
                'duration': 7,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'utc': str(utc),
                'correlation': '1',
            },
            headers={'Referer': 'https://maree.shom.fr/'},
            timeout=15,
        )
        data = resp.json()

        coeffs = {}
        for date_str, entries in data.items():
            day_coeffs = []
            for entry in entries:
                if entry[0] == 'tide.high' and entry[3] != '---':
                    day_coeffs.append(int(entry[3]))
            if day_coeffs:
                coeffs[date_str] = day_coeffs

        _shom_cache['date'] = today
        _shom_cache['data'] = coeffs
        print("SHOM coefficients fetched: {} days".format(len(coeffs)))
        return coeffs

    except Exception as e:
        print("SHOM API error: {} - using approximation".format(e))
        return _shom_cache.get('data')


def calc_tide_coefficients(tides):
    """Assign official SHOM coefficients to HIGH tides.

    Falls back to approximate formula if SHOM is unavailable.
    Approximate values are marked with coeff_approx=True.
    """
    import config

    for t in tides:
        t['coeff'] = None
        t['coeff_approx'] = False

    # Try SHOM official data
    shom = fetch_shom_coefficients()
    if shom:
        daily_highs = defaultdict(list)
        for t in tides:
            if t['type'] == 'high':
                local_date = time.strftime('%Y-%m-%d', time.localtime(t['epoch']))
                daily_highs[local_date].append(t)

        for date_str, highs in daily_highs.items():
            if date_str in shom:
                for i, high in enumerate(highs):
                    if i < len(shom[date_str]):
                        high['coeff'] = shom[date_str][i]

    # Fallback: approximate missing coefficients
    coeff_a = getattr(config, 'TIDE_COEFF_A', 12.0)
    coeff_b = getattr(config, 'TIDE_COEFF_B', 12.0)

    for i, t in enumerate(tides):
        if t.get('coeff') is not None or t['type'] != 'high':
            continue
        lows = []
        if i > 0 and tides[i - 1]['type'] == 'low':
            lows.append(tides[i - 1]['height'])
        if i < len(tides) - 1 and tides[i + 1]['type'] == 'low':
            lows.append(tides[i + 1]['height'])
        if lows:
            tidal_range = t['height'] - (sum(lows) / len(lows))
            coeff = int(round(coeff_a * tidal_range + coeff_b))
            t['coeff'] = max(20, min(120, coeff))
            t['coeff_approx'] = True
