# Family Dashboard 9.7" e-Paper -- Configuration
# Copy this file to config.py and fill in your values.

# === Display ===
VCOM = -2.06                           # YOUR display's VCOM (read from FPC cable)

# === Weather (OpenWeatherMap) ===
# Get API key: https://openweathermap.org/api
OWM_API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'

# Location 1: Primary city
WEATHER_1_CITY_ID = 0                  # OWM city ID
WEATHER_1_NAME = 'City1'

# Location 2: Secondary city (current weather only)
WEATHER_2_CITY_ID = 0                  # OWM city ID
WEATHER_2_NAME = 'City2'

# === Tides (Stormglass + SHOM) ===
# Get API key: https://stormglass.io
STORMGLASS_API_KEY = 'YOUR_STORMGLASS_API_KEY'
TIDE_LOCATION = 'Coast'
TIDE_LAT = 0.0
TIDE_LNG = 0.0
TIDE_COEFF_A = 12.0
TIDE_COEFF_B = 12.0

# === Calendar (iCal / .ics subscriptions) ===
# Add your iCloud, Proton, or any .ics URLs here
ICAL_URLS = [
    # 'webcal://p123-caldav.icloud.com/published/2/...',
    # 'https://calendar.proton.me/api/...',
]
CALENDAR_MAX_EVENTS = 7
CALENDAR_DAYS_AHEAD = 14

# === Shopping List (iCloud Reminders) ===
# Share a Reminders list from iPhone: List > Share > Copy Link
SHOPPING_LIST_URL = ''

# === Transport (BVG Berlin) ===
# Stop IDs from v6.bvg.transport.rest/locations?query=...
BVG_BUS_STOP_ID = ''                   # Bus stop ID (from v6.bvg.transport.rest/locations?query=...)
BVG_BUS_STOP_NAME = ''                 # Display name for the stop
BVG_BUS_LINE = ''                      # Bus line to track
BVG_UBAHN_STOP_ID = ''                 # U-Bahn station ID
BVG_UBAHN_LINE = 'U7'                  # U-Bahn line to track
BVG_UBAHN_DIRECTION = 'Spandau'        # Direction filter
BVG_UBAHN_MIN_MINUTES = 15             # Minimum departure time (walk buffer)
BVG_MAX_DEPARTURES = 8

# === Picture of the Day ===
POTD_SOURCE = 'wikimedia'              # 'wikimedia', 'nasa_apod', or 'local'
NASA_APOD_KEY = 'DEMO_KEY'
POTD_LOCAL_DIR = 'photos'              # Folder with .jpg/.png files (for 'local' source)

# === LLM Analogy (optional, Google Gemini free tier) ===
# Get free API key at: https://aistudio.google.com/apikey
# If not set, static analogies from science_de.json are used
GEMINI_API_KEY = ''

# === Timing ===
REFRESH_INTERVAL = 1800                # Seconds between full refresh cycles
SCREEN1_HOLD = 1500                    # Seconds to show main dashboard (~25 min)
SCREEN2_HOLD = 300                     # Seconds to show photo screen (~5 min)
