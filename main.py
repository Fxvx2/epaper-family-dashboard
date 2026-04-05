#!/usr/bin/env python3
"""Family Dashboard for 9.7" Waveshare e-Paper Display.

Usage:
    python3 main.py --virtual     # Development mode (Tkinter preview)
    sudo python3 main.py          # Production mode (real e-paper on Pi)
    python3 main.py --once        # Single refresh, then exit
"""

import sys
import os
import signal
import argparse
import time
import logging
from datetime import datetime

# Ensure we can import from project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import display_manager
import layout

try:
    import config
except ImportError:
    print("Error: config.py not found.")
    print("Copy config.example.py to config.py and fill in your settings.")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger(__name__)


def fetch_all_data():
    """Fetch data for all panels. Returns dict of {panel_name: data}."""
    data = {}

    # Weather
    try:
        from data.weather import fetch_current, fetch_forecast
        data['weather_berlin'] = fetch_current(config.WEATHER_1_CITY_ID)
        if data['weather_berlin']:
            data['weather_berlin']['display_name'] = config.WEATHER_1_NAME
        data['weather_cartagena'] = fetch_current(config.WEATHER_2_CITY_ID)
        if data['weather_cartagena']:
            data['weather_cartagena']['display_name'] = config.WEATHER_2_NAME
        data['forecast_berlin'] = fetch_forecast(config.WEATHER_1_CITY_ID)
        log.info("Weather OK: %s + %s", config.WEATHER_1_NAME, config.WEATHER_2_NAME)
    except Exception as e:
        log.warning("Weather fetch error: %s", e)

    # Tides
    try:
        from data.tides import fetch_tides, calc_tide_coefficients, fetch_sea_level
        tides = fetch_tides()
        if tides:
            calc_tide_coefficients(tides)
        sea_level = fetch_sea_level()
        data['tides'] = {'extremes': tides, 'sea_level': sea_level} if tides else None
        log.info("Tides OK: %d entries, %d sea level points",
                 len(tides) if tides else 0,
                 len(sea_level) if sea_level else 0)
    except Exception as e:
        log.warning("Tides fetch error: %s", e)

    # Transport
    try:
        from data.transport_data import fetch_departures
        data['transport'] = fetch_departures()
        log.info("Transport OK")
    except Exception as e:
        log.warning("Transport fetch error: %s", e)

    # Calendar
    try:
        from data.calendar_data import fetch_events
        data['calendar'] = fetch_events()
        log.info("Calendar OK: %d events", len(data['calendar']) if data['calendar'] else 0)
    except Exception as e:
        log.warning("Calendar fetch error: %s", e)

    # Daily content
    try:
        from data.content import get_daily_content
        daily = get_daily_content()
        data.update(daily)
        log.info("Daily content OK")
    except Exception as e:
        log.warning("Daily content error: %s", e)

    # Picture of the day (Screen 2)
    try:
        from data.media import fetch_picture_of_day
        data['picture_of_day'] = fetch_picture_of_day()
        log.info("Picture of the day OK")
    except Exception as e:
        log.warning("Picture of day error: %s", e)

    # Math challenge (Screen 2)
    try:
        from data.math_challenge import generate_challenge
        data['math_challenge'] = generate_challenge()
        log.info("Math challenge OK")
    except Exception as e:
        log.warning("Math challenge error: %s", e)

    # Shopping list (Screen 2 — reads from cache/shopping.json)
    data['shopping_list'] = True  # panel reads its own file

    # Family calendar week view (Screen 3 — separate fetch per member)
    try:
        from data.calendar_data import fetch_family_calendars
        data['calendar_week'] = fetch_family_calendars()
        log.info("Family calendars OK: %d members",
                 len(data['calendar_week']) if data['calendar_week'] else 0)
    except Exception as e:
        log.warning("Family calendar error: %s", e)
        data['calendar_week'] = None

    return data


def render_screen1(data, fonts):
    """Render all panels for Screen 1 (main dashboard)."""
    rendered = {}
    for name, x, y, w, h in layout.SCREEN1_PANELS:
        try:
            panel_mod = _get_panel_module(name)
            if panel_mod and name in data and data[name] is not None:
                rendered[name] = panel_mod.render(data[name], fonts, (w, h))
            else:
                rendered[name] = layout.render_placeholder(name, w, h, fonts)
        except Exception as e:
            log.warning("Panel %s render error: %s", name, e)
            rendered[name] = layout.render_placeholder(name, w, h, fonts)
    return rendered


def render_screen2(data, fonts):
    """Render all panels for Screen 2 (photo + extras)."""
    # Map Screen 2 panel names to data keys (shopping_list reads its own file)
    data_key_map = {
        'shopping_list': 'shopping_list',
        'science': 'science',
    }
    rendered = {}
    for name, x, y, w, h in layout.SCREEN2_PANELS:
        try:
            panel_mod = _get_panel_module(name)
            data_key = data_key_map.get(name, name)
            if panel_mod and data_key in data and data[data_key] is not None:
                rendered[name] = panel_mod.render(data[data_key], fonts, (w, h))
            else:
                rendered[name] = layout.render_placeholder(name, w, h, fonts)
        except Exception as e:
            log.warning("Panel %s render error: %s", name, e)
            rendered[name] = layout.render_placeholder(name, w, h, fonts)
    return rendered


_panel_cache = {}

def _get_panel_module(name):
    """Lazy-load panel module by name. Returns None if not found."""
    if name in _panel_cache:
        return _panel_cache[name]

    # Map panel names to module names
    module_map = {
        'weather_berlin': 'panels.weather',
        'weather_cartagena': 'panels.weather',
        'forecast_berlin': 'panels.forecast',
        'tides': 'panels.tides',
        'transport': 'panels.transport',
        'calendar': 'panels.calendar_panel',
        'quote': 'panels.quote',
        'famous_person': 'panels.famous_person',
        'science': 'panels.science',
        'word_of_day': 'panels.word_of_day',
        'picture_of_day': 'panels.picture_of_day',
        'math_challenge': 'panels.math_challenge',
        'joke': 'panels.joke',
        'raetsel': 'panels.raetsel',
        'bjj': 'panels.bjj',
        'shopping_list': 'panels.shopping_list',
        'calendar_week': 'panels.calendar_week',
    }

    mod_name = module_map.get(name)
    if not mod_name:
        return None

    try:
        import importlib
        mod = importlib.import_module(mod_name)
        _panel_cache[name] = mod
        return mod
    except ImportError:
        _panel_cache[name] = None
        return None


def main():
    parser = argparse.ArgumentParser(description='Family Dashboard 9.7" e-Paper')
    parser.add_argument('--virtual', action='store_true',
                        help='Use virtual display (Tkinter preview)')
    parser.add_argument('--once', action='store_true',
                        help='Single refresh cycle, then exit')
    args = parser.parse_args()

    vcom = getattr(config, 'VCOM', -2.06)
    display = display_manager.create_display(virtual=args.virtual, vcom=vcom)
    fonts = layout.load_fonts()

    log.info("Family Dashboard started")
    log.info("Display: %dx%d", display_manager.WIDTH, display_manager.HEIGHT)

    while True:
        log.info("=== Refresh cycle: %s ===", datetime.now().strftime('%Y-%m-%d %H:%M'))

        data = fetch_all_data()

        # Screen 1: Main dashboard
        log.info("Rendering Screen 1 (main dashboard)")
        rendered1 = render_screen1(data, fonts)
        layout.composite(display, layout.SCREEN1_PANELS, rendered1)
        display_manager.show(display)

        if args.once:
            log.info("Single run mode -- exiting")
            break

        # Hold Screen 1
        hold1 = getattr(config, 'SCREEN1_HOLD', 1500)
        log.info("Screen 1 displayed for %d min", hold1 // 60)
        display_manager.smart_sleep(display, hold1)

        # Screen 2: Photo + extras
        log.info("Rendering Screen 2 (photo + extras)")
        rendered2 = render_screen2(data, fonts)
        layout.composite(display, layout.SCREEN2_PANELS, rendered2)
        display_manager.show(display)

        # Screen 3: Family calendar week
        log.info("Rendering Screen 3 (calendar week)")
        rendered3 = {}
        for name, x, y, w, h in layout.SCREEN3_PANELS:
            try:
                panel_mod = _get_panel_module(name)
                data_key = name
                if panel_mod and data_key in data and data[data_key] is not None:
                    rendered3[name] = panel_mod.render(data[data_key], fonts, (w, h))
                else:
                    rendered3[name] = layout.render_placeholder(name, w, h, fonts)
            except Exception as e:
                log.warning("Panel %s render error: %s", name, e)
                rendered3[name] = layout.render_placeholder(name, w, h, fonts)
        layout.composite(display, layout.SCREEN3_PANELS, rendered3)
        display_manager.show(display)

        # Hold Screen 2
        hold2 = getattr(config, 'SCREEN2_HOLD', 300)
        log.info("Screen 2 displayed for %d min", hold2 // 60)
        display_manager.smart_sleep(display, hold2)

        # Back to Screen 1 for remaining time
        log.info("Returning to Screen 1")
        layout.composite(display, layout.SCREEN1_PANELS, rendered1)
        display_manager.show(display)

        remaining = max(60, config.REFRESH_INTERVAL - hold1 - hold2)
        log.info("Next refresh in %dm %ds", remaining // 60, remaining % 60)
        display_manager.smart_sleep(display, remaining)


def shutdown(signum, frame):
    log.info("Shutting down")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

if __name__ == '__main__':
    main()
