#!/usr/bin/env python3
"""Compatibility entrypoint for the shipped Phase 11 HVC teardown/failure packet checker."""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> None:
    target = Path(__file__).with_name("check-phase11-hvc-teardown-failure-packet.py")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
