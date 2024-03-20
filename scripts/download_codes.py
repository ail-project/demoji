#!/usr/bin/env python3

"""Download emoji data to package_data."""

import json
import pathlib

import requests

from demoji import URL

# We do *not* use importlib.resources here since we just want the source file,
# not where it (might) be installed
parent = pathlib.Path(__file__).parent.parent.resolve() / "demoji"
CACHEPATH = parent / "codes.json"
MODULEPATH = parent / "__init__.py"


def download_codes():
    codes = dict(stream_unicodeorg_emojifile(URL))
    _write_codes(codes)


def _write_codes(codes):
    print(f'Writing emoji data to {CACHEPATH} ...')
    with open(CACHEPATH, "w") as f:
        json.dump(codes, f, separators=(",", ":"))
    print('... OK')


def stream_unicodeorg_emojifile(url=URL):
    for codes, desc in _raw_stream_unicodeorg_emojifile(url):
        if ".." in codes:
            for cp in parse_unicode_range(codes):
                yield cp, desc
        else:
            yield parse_unicode_sequence(codes), desc


def parse_unicode_sequence(string):
    return "".join((chr(int(i.zfill(8), 16)) for i in string.split()))


def parse_unicode_range(string):
    start, _, end = string.partition("..")
    start, end = map(lambda i: int(i.zfill(8), 16), (start, end))
    return (chr(i) for i in range(start, end + 1))


def _raw_stream_unicodeorg_emojifile(url):
    print(f'Downloading emoji data from {url} ...')
    resp = requests.request("GET", url, stream=True)
    print(f'... OK (Got response in {resp.elapsed.total_seconds()} seconds)')

    POUNDSIGN = "#"
    POUNDSIGN_B = b"#"
    SEMICOLON = ";"
    SPACE = " "
    for line in resp.iter_lines():
        if not line or line.startswith(POUNDSIGN_B):
            continue
        line = line.decode("utf-8")
        codes, desc = line.split(SEMICOLON, 1)
        _, desc = desc.split(POUNDSIGN, 1)
        desc = desc.split(SPACE, 3)[-1]
        yield codes.strip(), desc.strip()


if __name__ == "__main__":
    download_codes()
