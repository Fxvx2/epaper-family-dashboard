# epaper-family-dashboard

Family information dashboard for a Waveshare 9.7" e-Paper display (1200x825, 16-level grayscale) on Raspberry Pi 4.

Displays weather, tides, public transport, family calendar, shopping list, daily educational content, and more across 3 rotating screens. All panels render in grayscale for the IT8951-based e-Paper display.

## Screens

### Screen 1 -- Main Dashboard (displayed ~25 minutes)

```text
+-------------------+-------------------+------------------+
|  Weather City 1   |  3-Day Forecast   |  Tides + Curve   |
|  Temp, wind, RH   |  Icons, min/max   |  HOCH/TIEF times |
|  km/h + knots     |  wind km/h + kn   |  SHOM coefficients|
|  sunrise/sunset   |                   |  Tide curve 24h  |
+-------------------+-------------------+------------------+
|  Weather City 2   |  BVG Transport    |  Calendar        |
|  (compact)        |  Bus, U-Bahn,     |  Next 7 events   |
|                   |  S-Bahn journey   |  from iCal feeds  |
+-------------------+-------------------+------------------+
|  Quote (DE + EN)  |  Famous Person    |                  |
|  + author bio     |  + country        |                  |
+-------------------+-------------------+------------------+
|  Math Challenge   |  Word of the Day  |                  |
|  3 difficulty     |  DE word +        |                  |
|  levels           |  definition       |                  |
+-------------------+-------------------+------------------+
```

### Screen 2 -- Fun Screen (displayed ~5 minutes)

```text
+---------------------+-------------------+
|  Picture of the Day |  Shopping List    |
|  (Wikimedia/NASA)   |  (Bring! app)     |
|  + legend/location  |  Live sync        |
+------+------+-------+------+------------+
| Joke | BJJ  |Riddle | Science Concept   |
| (DE) | Move | (DE)  | + Gemini analogy  |
+------+------+-------+-------------------+
```

### Screen 3 -- Family Calendar Week (displayed ~2 minutes)

```text
+--------+---Mo---+---Di---+---Mi---+---Do---+---Fr---+---Sa---+---So---+
|Familie | events |        | events |        |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Papa   |        | events |        |        | events |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Mama   | events |        | events | events |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
| Kids   |        |        | events |        | events |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
```

Each row is a separate iCal subscription. Today is highlighted.

## Data Sources

| Service | What | Free Tier | Requests/Day |
|---------|------|-----------|-------------|
| OpenWeatherMap | Weather + forecast | 1M/month | ~96 |
| Stormglass.io | Tide times + sea level curve | 10/day | 2 |
| SHOM | French tide coefficients | Unlimited | 1 |
| BVG REST API | Bus, U-Bahn, S-Bahn departures | Unlimited | ~48 |
| iCal (.ics) | Calendar events | N/A | ~48 |
| Bring! API | Shared shopping list | N/A | ~48 |
| Google Gemini | Science analogy generation | 1500/day | 1 |
| Wikimedia/NASA | Picture of the day | Unlimited | 1 |

### Why multiple services?

No single free API provides weather, tides, AND official French tide coefficients. Stormglass provides global tide data but not the French coefficient (a Brest-referenced metric). SHOM provides the coefficient but only through their portal. Combining both gives complete tide information for any French coastal location.

The tide coefficient (coefficient de maree, 20-120) indicates tidal forcing strength. It is universal across all French ports -- calculated from astronomical data referenced at Brest. If SHOM is unavailable, an approximate coefficient is calculated from local tidal range and displayed with an asterisk (*).

## Hardware

- Raspberry Pi 4 Model B (2GB+ RAM)
- Waveshare 9.7" e-Paper HAT (IT8951 controller, 1200x825, 16 grayscale levels)
- SPI must be enabled

## Setup

### 1. Enable SPI

```bash
sudo raspi-config
# Interface Options > SPI > Enable
```

### 2. Install bcm2835 (required for IT8951)

```bash
cd /tmp
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz && cd bcm2835-1.71
./configure && make && sudo make install
```

### 3. Install IT8951 driver

```bash
cd ~/Work/FamilyDashboard97
pip3 install ./IT8951/
```

### 4. Install Python dependencies

```bash
pip3 install pyowm requests Pillow icalendar recurring-ical-events numpy
```

### 5. Configure

```bash
cp config.example.py config.py
# Edit config.py with your API keys, locations, calendar URLs, etc.
```

### 6. Set Bring! credentials (environment variables)

```bash
export BRING_EMAIL="your@email.com"
export BRING_PASSWORD="yourpassword"
```

### 7. Run

Development (PNG output, no hardware needed):

```bash
python3 main.py --virtual --once
# Output in cache/screen_*.png
```

Production (real e-Paper, must run as root):

```bash
sudo python3 main.py
```

### 8. Run as a service

```bash
sudo cp dashboard.service /etc/systemd/system/
# Edit /etc/systemd/system/dashboard.service to add BRING_EMAIL and BRING_PASSWORD
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

## Configuration

All settings are in `config.py` (gitignored). See `config.example.py` for all available options:

- Weather locations (OpenWeatherMap city IDs)
- Tide station coordinates
- Calendar URLs (iCal/webcal)
- Family member calendars for week view
- BVG stop IDs and line filters
- S-Bahn journey (from/to stop IDs)
- Picture of the day source (wikimedia, nasa_apod, or local folder)
- LLM API key for science analogies (optional)
- Refresh timing

## Daily Content

Rotates deterministically at midnight (same content all day, changes next day):

- German wisdom quote with English translation and author biography
- Famous person with country and "known for" description
- Science concept with domain, scientist, and AI-generated analogy
- German word of the day with definition and example
- Math challenge (3 difficulty levels, faint answers)
- Joke (Flachwitze for kids, answer in light gray)
- Riddle (answer barely visible)
- BJJ move of the day with technique description

Content is stored in JSON files under `data/static/` and can be extended.

## Project Structure

```text
FamilyDashboard97/
    main.py                 Entry point, screen rotation loop
    config.example.py       Configuration template
    display_manager.py      PNG (dev) or IT8951 (production) display
    layout.py               Grid system, panel definitions, utilities
    panels/                 Panel renderers (one per panel)
    data/                   Data fetchers with caching
    data/static/            JSON content files
    fonts/                  Arial + Meteocons weather icons
    IT8951/                 Waveshare IT8951 driver
    cache/                  Runtime cache (gitignored)
    dashboard.service       systemd service file
```

## Display Notes

- All panels use 8-bit grayscale (0=black, 255=white)
- Visual hierarchy through gray tones: 0 (headers), 50 (emphasis), 100 (secondary), 140 (tertiary), 190 (separators)
- Tide curve drawn from Stormglass sea-level hourly data with "now" marker
- Wind shown in both km/h and knots
- Shopping list syncs live from the Bring! app
- Gemini-generated analogies are cached daily (1 API call/day)

## License

MIT License. See LICENSE for details.

Derived from ProtoStax Weather Station Demo (BSD 3-Clause).
Waveshare IT8951 driver by GregDMeyer (MIT).
Meteocons font by Alessio Atzeni, free for use.
