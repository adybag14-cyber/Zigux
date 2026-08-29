#!/usr/bin/env python3
"""Static contract for the exhaustive-to-bootable kernel config boundary."""

from __future__ import annotations

import re
from pathlib import Path

SCRIPT = Path(__file__).with_name("build-kernel-package.sh")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    disable = re.search(
        r"for symbol in \\\n(?P<body>.*?)\n\s*\"\$cfg\" .*? --disable \"\$symbol\"",
        text,
        re.DOTALL,
    )
    require(disable is not None, "bootability disable loop was not found")
    disable_symbols = set(re.findall(r"[A-Z][A-Z0-9_]+", disable.group("body")))

    forbidden = re.search(r"for forbidden in (?P<body>[^;]+); do", text)
    require(forbidden is not None, "post-olddefconfig forbidden loop was not found")
    forbidden_symbols = set(re.findall(r"[A-Z][A-Z0-9_]+", forbidden.group("body")))

    required_boot_guards = {
        "FTRACE_STARTUP_TEST",
        "SERIAL_NUVOTON_MA35D1_CONSOLE",
        "KCOV",
    }
    require(
        required_boot_guards <= disable_symbols,
        f"missing disable guards: {sorted(required_boot_guards - disable_symbols)}",
    )
    require(
        required_boot_guards <= forbidden_symbols,
        f"missing fail-closed guards: {sorted(required_boot_guards - forbidden_symbols)}",
    )

    original = text.index('cp "$out/.config" "$dist/config-${profile}-original"')
    disable_start = disable.start()
    normalize = text.index('make -C "$src" O="$out" olddefconfig')
    forbidden_start = forbidden.start()
    bootable = text.index('cp "$out/.config" "$dist/config-${profile}-bootable"')
    require(
        original < disable_start < normalize < forbidden_start < bootable,
        "config provenance/order must be original -> disable -> olddefconfig -> assert -> bootable",
    )

    print("CachyOS boot config contract: OK")


if __name__ == "__main__":
    main()
