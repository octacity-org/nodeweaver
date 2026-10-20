"""String helpers, two levels deep inside the package."""

from .. import VERSION                 # from .. import y


def greet(name):
    return f"hello {name} (v{VERSION})"


def shout(text):
    return text.upper() + "!"
