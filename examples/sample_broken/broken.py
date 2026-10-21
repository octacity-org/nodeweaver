"""This file contains an intentional syntax error. Do not fix it.

The parser must not crash on it: it should mark the file as having a
parse error and still return what it can read from the valid parts.
"""

import os


def valid_function():
    return os.getcwd()


def broken_function(:
    return "the parameter list above is invalid"


def another_valid_function():
    return 42
