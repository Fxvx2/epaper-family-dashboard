"""BVG public transport departures via v6.bvg.transport.rest API."""

import time
from datetime import datetime

import requests

API_BASE = 'https://v6.bvg.transport.rest'

_cache = {}


def _parse_time(iso_str):
    """Parse ISO 8601 time string, return epoch seconds."""
    # Handle both 'Z' and '+02:00' formats
    if not iso_str:
        return None
    try:
        # Try with timezone offset
        for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z'):
            try:
                dt = datetime.strptime(iso_str, fmt)
                return dt.timestamp()
            except ValueError:
                continue
        # Fallback: strip timezone and parse
        clean = iso_str[:19]
        dt = datetime.strptime(clean, '%Y-%m-%dT%H:%M:%S')
        return dt.timestamp()
    except Exception:
        return None


def _fetch_departures(stop_id, duration=60, results=15):
    """Fetch raw departures from BVG API."""
    resp = requests.get(
        '{}/stops/{}/departures'.format(API_BASE, stop_id),
        params={
            'duration': duration,
            'results': results,
        },
        timeout=15,
    )
    return resp.json().get('departures', resp.json() if isinstance(resp.json(), list) else [])


def fetch_departures():
    """Fetch M43 bus + U7 departures, filtered and formatted.

    Returns dict with 'bus' and 'ubahn' lists of departure dicts.
    """
    import config

    now = time.time()
    result = {'bus': [], 'ubahn': []}

    # -- Bus departures (both directions) --
    bus_stop = getattr(config, 'BVG_BUS_STOP_ID', '')
    bus_line = getattr(config, 'BVG_BUS_LINE', 'M43')

    if bus_stop:
        try:
            deps = _fetch_departures(bus_stop, duration=45, results=15)
            directions = {}  # {direction: [departures]}

            for dep in deps:
                line = dep.get('line', {}).get('name', '')
                if line != bus_line:
                    continue

                direction = dep.get('direction', 'Unknown')
                # Shorten direction name
                direction = direction.replace(' (Berlin)', '').replace(', ', ' ')

                when_str = dep.get('when') or dep.get('plannedWhen', '')
                when = _parse_time(when_str)
                if not when:
                    continue

                planned_str = dep.get('plannedWhen', when_str)
                planned = _parse_time(planned_str)
                delay = dep.get('delay', 0) or 0

                mins = int((when - now) / 60)
                if mins < 0:
                    continue

                entry = {
                    'line': line,
                    'direction': direction[:20],
                    'time': time.strftime('%H:%M', time.localtime(when)),
                    'mins': mins,
                    'delay': delay // 60 if delay else 0,
                }

                if direction not in directions:
                    directions[direction] = []
                directions[direction].append(entry)

            # Take next 2 per direction
            for direction in sorted(directions.keys()):
                result['bus'].extend(directions[direction][:2])

        except Exception as e:
            print("BVG bus error: {}".format(e))

    # -- U-Bahn departures (filtered by direction and min time) --
    ubahn_stop = getattr(config, 'BVG_UBAHN_STOP_ID', '')
    ubahn_line = getattr(config, 'BVG_UBAHN_LINE', 'U7')
    ubahn_dir = getattr(config, 'BVG_UBAHN_DIRECTION', 'Spandau')
    min_minutes = getattr(config, 'BVG_UBAHN_MIN_MINUTES', 15)

    if ubahn_stop:
        try:
            deps = _fetch_departures(ubahn_stop, duration=60, results=15)

            for dep in deps:
                line = dep.get('line', {}).get('name', '')
                if line != ubahn_line:
                    continue

                direction = dep.get('direction', '')
                if ubahn_dir.lower() not in direction.lower():
                    continue

                when_str = dep.get('when') or dep.get('plannedWhen', '')
                when = _parse_time(when_str)
                if not when:
                    continue

                delay = dep.get('delay', 0) or 0
                mins = int((when - now) / 60)

                if mins < min_minutes:
                    continue

                entry = {
                    'line': line,
                    'direction': 'Spandau',
                    'time': time.strftime('%H:%M', time.localtime(when)),
                    'mins': mins,
                    'delay': delay // 60 if delay else 0,
                }
                result['ubahn'].append(entry)

                if len(result['ubahn']) >= 3:
                    break

        except Exception as e:
            print("BVG U-Bahn error: {}".format(e))

    # -- S9 Treptower Park -> Savignyplatz --
    sbahn_from = getattr(config, 'BVG_SBAHN_FROM_ID', '')
    sbahn_to = getattr(config, 'BVG_SBAHN_TO_ID', '')
    sbahn_line = getattr(config, 'BVG_SBAHN_LINE', 'S9')
    result['sbahn'] = []

    if sbahn_from and sbahn_to:
        try:
            resp = requests.get(
                '{}/journeys'.format(API_BASE),
                params={
                    'from': sbahn_from,
                    'to': sbahn_to,
                    'departure': 'now',
                    'results': 5,
                    'suburban': 'true',
                },
                timeout=15,
            )
            journeys = resp.json().get('journeys', [])

            for j in journeys:
                legs = j.get('legs', [])
                if not legs:
                    continue

                # Check if direct S9 (single leg with matching line)
                if len(legs) == 1:
                    leg = legs[0]
                    line = leg.get('line', {}).get('name', '')
                    if sbahn_line and sbahn_line not in line:
                        continue

                    dep_str = leg.get('departure') or leg.get('plannedDeparture', '')
                    arr_str = leg.get('arrival') or leg.get('plannedArrival', '')
                    dep_time = _parse_time(dep_str)
                    arr_time = _parse_time(arr_str)

                    if not dep_time or not arr_time:
                        continue

                    mins_until = int((dep_time - now) / 60)
                    if mins_until < 0:
                        continue

                    duration = int((arr_time - dep_time) / 60)
                    delay = leg.get('departureDelay', 0) or 0

                    result['sbahn'].append({
                        'line': line,
                        'dep_time': time.strftime('%H:%M', time.localtime(dep_time)),
                        'arr_time': time.strftime('%H:%M', time.localtime(arr_time)),
                        'mins': mins_until,
                        'duration': duration,
                        'delay': delay // 60 if delay else 0,
                    })

                    if len(result['sbahn']) >= 2:
                        break

        except Exception as e:
            print("BVG S-Bahn error: {}".format(e))

    _cache['departures'] = result
    return result
