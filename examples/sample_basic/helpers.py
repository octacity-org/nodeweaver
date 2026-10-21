"""Helper functions for sample_basic. main.py imports these with `import *`."""

import math

__all__ = ["round_price", "make_label"]


def round_price(value):
    return math.floor(value * 100) / 100


def make_label(text):
    # Nested function: defined and called inside make_label.
    def clean(raw):
        return raw.strip().lower()

    return clean(text)
