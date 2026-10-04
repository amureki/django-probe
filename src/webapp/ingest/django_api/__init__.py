"""Load the vendored Django API vocabularies."""

from __future__ import annotations

import gzip
import json
from bisect import bisect_left
from functools import cache
from pathlib import Path
from typing import cast


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


_VOCABULARY_DIRECTORY = Path(__file__).parent
_COMBINED_VOCABULARY = _VOCABULARY_DIRECTORY / "all.json.gz"
_VOCABULARIES = {
    path.name.removesuffix(".json.gz"): path
    for path in _VOCABULARY_DIRECTORY.glob("[0-9]*.json.gz")
}
DJANGO_API_VERSIONS = tuple(sorted(_VOCABULARIES, key=_version_key))


def _read_api_names(version: str) -> list[str]:
    """Read one vendored API catalog without retaining an intermediate set."""
    path = _VOCABULARIES[version]
    return cast(list[str], json.loads(gzip.decompress(path.read_bytes()))["names"])


@cache
def _combined_api_names() -> tuple[str, ...]:
    """Read the sorted vocabulary shared by every supported Django release."""
    payload = json.loads(gzip.decompress(_COMBINED_VOCABULARY.read_bytes()))
    return tuple(cast(list[str], payload["names"]))


def is_django_api_name(name: str) -> bool:
    """Return whether a name occurs in the combined Django API vocabulary."""
    names = _combined_api_names()
    index = bisect_left(names, name)
    return index < len(names) and names[index] == name
