"""Bring! shopping list API integration.

Credentials are read from environment variables:
  BRING_EMAIL, BRING_PASSWORD

Cached per refresh cycle (in-memory).
"""

import os
import requests

_cache = {'items': None}
_auth = {'token': None, 'list_id': None}


def _login():
    """Authenticate with Bring! API. Returns (token, list_uuid)."""
    email = os.environ.get('BRING_EMAIL', '')
    password = os.environ.get('BRING_PASSWORD', '')

    if not email or not password:
        # Fallback: try config.py
        try:
            import config
            email = getattr(config, 'BRING_EMAIL', '')
            password = getattr(config, 'BRING_PASSWORD', '')
        except ImportError:
            pass

    if not email or not password:
        return None, None

    resp = requests.post('https://api.getbring.com/rest/v2/bringauth',
        data={'email': email, 'password': password},
        timeout=10)

    if resp.status_code != 200:
        print("Bring! login failed: {}".format(resp.status_code))
        return None, None

    auth = resp.json()
    token = auth.get('access_token', '')
    list_id = auth.get('bringListUUID', '')
    return token, list_id


def fetch_shopping_list():
    """Fetch items from Bring! shopping list.

    Returns list of item strings, or None if unavailable.
    """
    # Login if needed
    if not _auth.get('token'):
        token, list_id = _login()
        if not token:
            return _cache.get('items')
        _auth['token'] = token
        _auth['list_id'] = list_id

    try:
        resp = requests.get(
            'https://api.getbring.com/rest/v2/bringlists/{}'.format(_auth['list_id']),
            headers={'Authorization': 'Bearer {}'.format(_auth['token'])},
            timeout=10)

        if resp.status_code == 401:
            # Token expired, re-login
            _auth['token'] = None
            token, list_id = _login()
            if not token:
                return _cache.get('items')
            _auth['token'] = token
            _auth['list_id'] = list_id
            resp = requests.get(
                'https://api.getbring.com/rest/v2/bringlists/{}'.format(list_id),
                headers={'Authorization': 'Bearer {}'.format(token)},
                timeout=10)

        data = resp.json()
        items = []
        for item in data.get('purchase', []):
            name = item.get('name', '')
            spec = item.get('specification', '')
            if spec:
                items.append('{} ({})'.format(name, spec))
            else:
                items.append(name)

        _cache['items'] = items
        return items

    except Exception as e:
        print("Bring! fetch error: {}".format(e))
        return _cache.get('items')
