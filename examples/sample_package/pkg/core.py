"""Core logic for sample_package."""

from . import utils                    # from . import x
from .utils.strings import shout       # from .a.b import c


def run(name):
    greeting = utils.greet(name)
    return shout(greeting)
