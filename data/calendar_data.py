"""iCal calendar data fetching and parsing."""

from datetime import datetime, timedelta, date
import requests
from icalendar import Calendar
import recurring_ical_events

_cache = {'data': None}


def fetch_events():
    """Fetch and merge events from all configured iCal URLs.

    Returns sorted list of event dicts within CALENDAR_DAYS_AHEAD days.
    """
    import config

    urls = getattr(config, 'ICAL_URLS', [])
    max_events = getattr(config, 'CALENDAR_MAX_EVENTS', 7)
    days_ahead = getattr(config, 'CALENDAR_DAYS_AHEAD', 14)

    if not urls:
        return _cache.get('data')

    all_events = []
    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    for url in urls:
        try:
            events = _fetch_ical(url, today, end_date)
            all_events.extend(events)
        except Exception as e:
            print("iCal fetch error for {}: {}".format(url[:50], e))

    # Sort by start time
    all_events.sort(key=lambda e: e['start'])

    # Limit
    result = all_events[:max_events]
    _cache['data'] = result
    return result


def _fetch_ical(url, start_date, end_date):
    """Fetch and parse a single iCal URL."""
    # Normalize webcal:// to https://
    if url.startswith('webcal://'):
        url = 'https://' + url[len('webcal://'):]

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    cal = Calendar.from_ical(resp.text)
    events = recurring_ical_events.of(cal).between(start_date, end_date)

    result = []
    for event in events:
        summary = str(event.get('SUMMARY', 'Untitled'))
        location = str(event.get('LOCATION', '')) if event.get('LOCATION') else ''
        dtstart = event.get('DTSTART').dt

        # Handle all-day events (date) vs timed events (datetime)
        if isinstance(dtstart, datetime):
            start_dt = dtstart
            all_day = False
            time_str = dtstart.strftime('%H:%M')
        elif isinstance(dtstart, date):
            start_dt = datetime.combine(dtstart, datetime.min.time())
            all_day = True
            time_str = ''
        else:
            continue

        # Date display
        if dtstart.date() == date.today() if isinstance(dtstart, datetime) else dtstart == date.today():
            date_str = 'Heute'
        elif (dtstart.date() if isinstance(dtstart, datetime) else dtstart) == date.today() + timedelta(days=1):
            date_str = 'Morgen'
        else:
            d = dtstart if isinstance(dtstart, date) else dtstart.date()
            date_str = d.strftime('%a %d/%m')

        result.append({
            'summary': summary[:30],
            'location': location[:20],
            'date_str': date_str,
            'time_str': time_str,
            'all_day': all_day,
            'start': start_dt,
            'is_today': date_str == 'Heute',
        })

    return result


def fetch_family_calendars():
    """Fetch events for each family member calendar separately.

    Returns list of {'name': str, 'events': [event dicts]} for Screen 3.
    """
    import config

    calendars = getattr(config, 'FAMILY_CALENDARS', [])
    days_ahead = getattr(config, 'CALENDAR_DAYS_AHEAD', 14)

    today = date.today()
    end_date = today + timedelta(days=days_ahead)

    result = []
    for cal in calendars:
        name = cal.get('name', '')
        url = cal.get('url', '')
        events = []
        if url:
            try:
                events = _fetch_ical(url, today, end_date)
            except Exception as e:
                print("iCal fetch error for {}: {}".format(name, e))
        result.append({'name': name, 'events': events})

    return result
