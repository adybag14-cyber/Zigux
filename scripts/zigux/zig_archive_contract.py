#!/usr/bin/env python3
from __future__ import annotations

EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}


def expected_archive_size_bytes(target: str) -> int:
    try:
        return EXPECTED_ARCHIVE_SIZES[target]
    except KeyError as exc:
        raise ValueError(f"missing expected archive size for {target}") from exc
