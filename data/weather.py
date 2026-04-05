"""Weather data fetching from OpenWeatherMap."""

import time
from datetime import datetime
from collections import defaultdict, Counter

import pyowm

_owm = None
_cache = {}

MS_TO_KN = 1.944
MS_TO_KMH = 3.6

# OWM weather code -> Meteocons font character
weather_icon_dict = {
    200: "6", 201: "6", 202: "6", 210: "6", 211: "6", 212: "6",
    221: "6", 230: "6", 231: "6", 232: "6",
    300: "7", 301: "7", 302: "8", 310: "7", 311: "8", 312: "8",
    313: "8", 314: "8", 321: "8",
    500: "7", 501: "7", 502: "8", 503: "8", 504: "8", 511: "8",
    520: "7", 521: "7", 522: "8", 531: "8",
    600: "V", 601: "V", 602: "W", 611: "X", 612: "X", 613: "X",
    615: "V", 616: "V", 620: "V", 621: "W", 622: "W",
    701: "M", 711: "M", 721: "M", 731: "M", 741: "M", 751: "M",
    761: "M", 762: "M", 771: "M", 781: "M",
    800: "1",
    801: "H", 802: "N", 803: "N", 804: "Y"
}


def _get_owm():
    global _owm
    if _owm is None:
        import config
        _owm = pyowm.OWM(config.OWM_API_KEY)
    return _owm


def _get_mgr():
    return _get_owm().weather_manager()


def wind_dir(deg):
    if deg is None:
        return ""
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][round(deg / 45) % 8]


def wind_str(speed):
    kmh = speed * MS_TO_KMH
    kn = speed * MS_TO_KN
    return "{:.0f}km/h {:.0f}kn".format(kmh, kn)


def fetch_current(city_id):
    """Fetch current weather for a city. Returns dict or None."""
    try:
        obs = _get_mgr().weather_at_id(city_id)
    except Exception as e:
        cached = _cache.get('current_{}'.format(city_id))
        if cached:
            return cached
        raise

    w = obs.weather
    temp = w.temperature('celsius')
    wind = w.wind() or {}
    rain = w.rain or {}
    pres = w.barometric_pressure() or {}

    data = {
        'location': obs.location.name,
        'reftime': w.reference_time(),
        'description': w.detailed_status,
        'temp': int(round(temp.get('temp', 0))),
        'temp_min': int(round(temp.get('temp_min', temp.get('temp', 0)))),
        'temp_max': int(round(temp.get('temp_max', temp.get('temp', 0)))),
        'feels_like': temp.get('feels_like'),
        'humidity': w.humidity,
        'pressure': int(round(pres.get('press', 0))),
        'clouds': w.clouds,
        'wind_speed': wind.get('speed', 0),
        'wind_deg': wind.get('deg'),
        'rain': rain.get('1h', rain.get('3h', 0)) if rain else 0,
        'sunrise': w.sunrise_time(),
        'sunset': w.sunset_time(),
        'icon': weather_icon_dict.get(w.weather_code, ')'),
    }
    _cache['current_{}'.format(city_id)] = data
    return data


def fetch_forecast(city_id):
    """Fetch 3-day forecast for a city. Returns list of day dicts."""
    try:
        fc = _get_mgr().forecast_at_id(city_id, '3h')
    except Exception as e:
        cached = _cache.get('forecast_{}'.format(city_id))
        if cached:
            return cached
        raise

    weathers = fc.forecast.weathers
    days = defaultdict(list)
    today = datetime.now().date()

    for w in weathers:
        d = datetime.fromtimestamp(w.reference_time()).date()
        if d > today:
            days[d].append(w)

    result = []
    for d in sorted(days.keys())[:3]:
        ws = days[d]
        temps = [w.temperature('celsius').get('temp', 0) for w in ws]
        codes = [w.weather_code for w in ws]
        winds = [w.wind().get('speed', 0) for w in ws if w.wind()]
        code = Counter(codes).most_common(1)[0][0]
        desc = next((w.detailed_status for w in ws
                      if w.weather_code == code), '')

        result.append({
            'day': d.strftime('%a'),
            'date': d.strftime('%d/%m'),
            'tmin': int(round(min(temps))),
            'tmax': int(round(max(temps))),
            'desc': desc,
            'wind': round(max(winds), 1) if winds else 0,
            'icon': weather_icon_dict.get(code, ')'),
        })

    _cache['forecast_{}'.format(city_id)] = result
    return result
