"""Daily math challenge generator for kids (age 9-11)."""

import hashlib
import random
from datetime import date


def _daily_random(seed='math'):
    """Create a deterministic random generator for today."""
    day_str = date.today().isoformat() + seed
    h = int(hashlib.md5(day_str.encode()).hexdigest(), 16)
    rng = random.Random(h)
    return rng


def generate_challenge():
    """Generate today's math challenges: 3 problems of increasing difficulty.

    Returns dict with 'problems' list, each having 'question' and 'answer'.
    """
    rng = _daily_random()
    problems = []

    # Problem 1: Easy (+ or -, 2 digits)
    op = rng.choice(['+', '-'])
    a = rng.randint(10, 99)
    b = rng.randint(10, 99)
    if op == '-' and b > a:
        a, b = b, a
    answer = a + b if op == '+' else a - b
    problems.append({
        'question': '{} {} {} = ?'.format(a, op, b),
        'answer': str(answer),
        'level': 'leicht',
    })

    # Problem 2: Medium (x with small numbers or + with 3 digits)
    choice = rng.randint(0, 1)
    if choice == 0:
        a = rng.randint(3, 12)
        b = rng.randint(3, 12)
        answer = a * b
        problems.append({
            'question': '{} x {} = ?'.format(a, b),
            'answer': str(answer),
            'level': 'mittel',
        })
    else:
        a = rng.randint(100, 999)
        b = rng.randint(100, 999)
        answer = a + b
        problems.append({
            'question': '{} + {} = ?'.format(a, b),
            'answer': str(answer),
            'level': 'mittel',
        })

    # Problem 3: Hard (multi-step or larger multiplication)
    choice = rng.randint(0, 2)
    if choice == 0:
        # Two-step: a + b x c
        a = rng.randint(10, 50)
        b = rng.randint(2, 9)
        c = rng.randint(2, 9)
        answer = a + b * c
        problems.append({
            'question': '{} + {} x {} = ?'.format(a, b, c),
            'answer': str(answer),
            'level': 'schwer',
        })
    elif choice == 1:
        # Larger multiplication
        a = rng.randint(12, 25)
        b = rng.randint(4, 12)
        answer = a * b
        problems.append({
            'question': '{} x {} = ?'.format(a, b),
            'answer': str(answer),
            'level': 'schwer',
        })
    else:
        # Missing number: a + ? = c
        a = rng.randint(15, 80)
        answer = rng.randint(15, 80)
        c = a + answer
        problems.append({
            'question': '{} + ? = {}'.format(a, c),
            'answer': str(answer),
            'level': 'schwer',
        })

    return {'problems': problems}
