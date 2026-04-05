"""Picture of the day: Wikimedia Commons POTD or NASA APOD."""

import os
import json
from datetime import date
from io import BytesIO

import requests
from PIL import Image, ImageEnhance

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
_cache = {'date': None, 'data': None}


def fetch_picture_of_day():
    """Fetch today's picture. Cached daily as PNG in cache/.

    Returns dict with 'image' (PIL Image, grayscale) and 'title'.
    """
    today = date.today()
    if _cache['date'] == today and _cache['data']:
        return _cache['data']

    import config
    source = getattr(config, 'POTD_SOURCE', 'wikimedia')

    try:
        if source == 'local':
            result = _fetch_local_photo()
        elif source == 'nasa_apod':
            result = _fetch_nasa_apod()
        else:
            result = _fetch_wikimedia_potd()

        if result:
            _cache['date'] = today
            _cache['data'] = result
            # Save cached image
            os.makedirs(CACHE_DIR, exist_ok=True)
            result['image'].save(os.path.join(CACHE_DIR, 'potd.png'))
            with open(os.path.join(CACHE_DIR, 'potd_meta.json'), 'w') as f:
                json.dump({'title': result['title'], 'date': today.isoformat()}, f)
            return result
    except Exception as e:
        print("POTD fetch error: {}".format(e))

    # Try loading from cache
    return _load_cached()


def _fetch_local_photo():
    """Pick a random photo from a local directory. Rotates daily."""
    import config
    import hashlib
    import glob

    photo_dir = getattr(config, 'POTD_LOCAL_DIR', 'photos')
    if not os.path.isdir(photo_dir):
        return None

    files = sorted(glob.glob(os.path.join(photo_dir, '*.jpg')) +
                   glob.glob(os.path.join(photo_dir, '*.jpeg')) +
                   glob.glob(os.path.join(photo_dir, '*.png')))
    if not files:
        return None

    # Deterministic daily pick
    day_hash = int(hashlib.md5(date.today().isoformat().encode()).hexdigest(), 16)
    path = files[day_hash % len(files)]
    filename = os.path.basename(path).rsplit('.', 1)[0].replace('_', ' ')

    img = Image.open(path).convert('L')
    img = ImageEnhance.Contrast(img).enhance(1.3)

    return {'image': img, 'title': filename, 'source': 'Eigene Fotos'}


def _fetch_wikimedia_potd():
    """Fetch Wikimedia Commons Picture of the Day."""
    today = date.today()
    url = 'https://api.wikimedia.org/feed/v1/wikipedia/en/featured/{}/{:02d}/{:02d}'.format(
        today.year, today.month, today.day)

    resp = requests.get(url, timeout=15,
                        headers={'User-Agent': 'FamilyDashboard/1.0'})
    data = resp.json()

    img_data = data.get('image', {})
    if not img_data:
        return None

    title = img_data.get('title', '').replace('File:', '').rsplit('.', 1)[0]
    title = title.replace('_', ' ')[:60]

    # Extract description/location if available
    desc = img_data.get('description', {})
    description = ''
    if isinstance(desc, dict):
        description = desc.get('text', '')
    elif isinstance(desc, str):
        description = desc
    # Clean HTML tags from description
    import re
    description = re.sub('<[^>]+>', '', description).strip()[:100]

    # Get image URL — try thumbnail first, then original
    thumb = img_data.get('thumbnail', {})
    img_url = thumb.get('source', '')
    if not img_url:
        img_url = img_data.get('image', {}).get('source', '')
    if not img_url:
        return None

    # Skip SVG files — request a rasterized version if possible
    if '.svg' in img_url.lower():
        # Wikimedia can render SVGs as PNG via thumb URL with width param
        orig = img_data.get('image', {}).get('source', '')
        if orig and '.svg' in orig.lower():
            # Try fetching NASA APOD as fallback
            try:
                return _fetch_nasa_apod()
            except Exception:
                return None

    # Download image
    img_resp = requests.get(img_url, timeout=15,
                            headers={'User-Agent': 'FamilyDashboard/1.0'})
    try:
        img = Image.open(BytesIO(img_resp.content))
    except Exception:
        # Image format not supported, try NASA fallback
        try:
            return _fetch_nasa_apod()
        except Exception:
            return None

    # Convert to grayscale and enhance contrast for e-paper
    img = img.convert('L')
    img = ImageEnhance.Contrast(img).enhance(1.3)

    return {'image': img, 'title': title, 'description': description,
            'source': 'Wikimedia Commons'}


def _fetch_nasa_apod():
    """Fetch NASA Astronomy Picture of the Day."""
    import config
    key = getattr(config, 'NASA_APOD_KEY', 'DEMO_KEY')

    resp = requests.get('https://api.nasa.gov/planetary/apod',
                        params={'api_key': key}, timeout=15)
    data = resp.json()

    if data.get('media_type') != 'image':
        return None

    title = data.get('title', 'NASA APOD')[:60]
    img_url = data.get('url', '')

    img_resp = requests.get(img_url, timeout=15)
    img = Image.open(BytesIO(img_resp.content))
    img = img.convert('L')
    img = ImageEnhance.Contrast(img).enhance(1.3)

    return {'image': img, 'title': title, 'source': 'NASA APOD'}


def _load_cached():
    """Try loading cached POTD from disk."""
    try:
        img_path = os.path.join(CACHE_DIR, 'potd.png')
        meta_path = os.path.join(CACHE_DIR, 'potd_meta.json')
        if os.path.exists(img_path) and os.path.exists(meta_path):
            img = Image.open(img_path).convert('L')
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            return {'image': img, 'title': meta.get('title', '')}
    except Exception:
        pass
    return None
