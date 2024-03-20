"""Find and replace emojis within text strings.

The set of emojis is refreshable from its canonical source at
http://www.unicode.org/emoji/charts/full-emoji-list.html.
"""

__all__ = (
    "findall",
    "findall_list",
    "replace",
    "replace_with_desc",
)
__version__ = "1.1.1"

import functools
import logging
import os.path
import re
import sys

try:
    # Enable faster loads with ujson if installed
    import ujson as json
except ImportError:
    import json

logging.getLogger(__name__).addHandler(logging.NullHandler())

if sys.version_info >= (3, 7):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

# Download endpoint
URL = "https://unicode.org/Public/emoji/latest/emoji-test.txt"


def cache_setter(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        set_emoji_pattern()
        return func(*args, **kwargs)

    return wrapper


@cache_setter
def findall(string):
    """Find emojis within ``string``.

    :param string: The input text to search
    :type string: str
    :return: A dictionary of ``{emoji: description}``
    :rtype: dict
    """

    return {f: _CODE_TO_DESC[f] for f in set(_EMOJI_PAT.findall(string))}


@cache_setter
def findall_list(string, desc=True):
    """Find emojis within ``string``; return a list with possible duplicates.

    :param string: The input text to search
    :type string: str
    :param desc: Whether to return the description rather than emoji
    :type desc: bool
    :return: A list of ``[description, ...]`` in the order in which they
      are found.
    :rtype: list
    """

    if desc:
        return [_CODE_TO_DESC[k] for k in _EMOJI_PAT.findall(string)]
    else:
        return _EMOJI_PAT.findall(string)


@cache_setter
def replace(string, repl=""):
    """Replace emojis in ``string`` with ``repl``.

    :param string: The input text to search
    :type string: str
    :return: Modified ``str`` with replacements made
    :rtype: str
    """
    return _EMOJI_PAT.sub(repl, string)


@cache_setter
def replace_with_desc(string, sep=":"):
    """Replace emojis in ``string`` with their description.

    Add a ``sep`` immediately before and after ``string``.

    :param string: The input text to search
    :type string: str
    :param sep: String to put before and after the emoji description
    :type sep: str
    :return: New copy of ``string`` with replacements made and ``sep``
      immediately before and after each code
    :rtype: str
    """

    found = findall(string)
    result = string
    for emoji, desc in found.items():
        result = result.replace(emoji, sep + desc + sep)
    return result


def _compile_codes(codes):
    escp = (re.escape(c) for c in sorted(codes, key=len, reverse=True))
    return re.compile(r"|".join(escp))


_EMOJI_PAT = None
_CODE_TO_DESC = {}


def _load_codes_from_file():
    with importlib_resources.open_text("demoji", "codes.json") as f:
        return json.load(f)


def set_emoji_pattern():
    global _EMOJI_PAT
    global _CODE_TO_DESC
    if _EMOJI_PAT is None:
        codes = _load_codes_from_file()
        _EMOJI_PAT = _compile_codes(codes)
        _CODE_TO_DESC.update(codes)
