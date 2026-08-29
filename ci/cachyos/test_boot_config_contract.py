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
        r"for symbol in \\\n(?P<body>(?:(?!\ndone).)*?)\n"
        r'\s*"\$cfg" [^\n]* --disable "\$symbol"\ndone',
        text,
        re.DOTALL,
    )
    require(disable is not None, "bootability disable loop was not found")
    disable_symbols = set(re.findall(r"[A-Z][A-Z0-9_]+", disable.group("body")))

    forbidden = re.search(r"for forbidden in (?P<body>[^;]+); do", text)
    require(forbidden is not None, "post-olddefconfig forbidden loop was not found")
    forbidden_symbols = set(re.findall(r"[A-Z][A-Z0-9_]+", forbidden.group("body")))

    required_boot_disables = {
        "BACKTRACE_SELF_TEST",
        "COMPILE_TEST",
        "CPA_DEBUG",
        "DEBUG_KOBJECT_RELEASE",
        "DEBUG_LOCKING_API_SELFTESTS",
        "DEBUG_OBJECTS_SELFTEST",
        "DEBUG_PAGEALLOC",
        "DMAPOOL_TEST",
        "FTRACE_STARTUP_TEST",
        "FSL_BMAN_TEST",
        "FSL_BMAN_TEST_API",
        "FSL_QMAN_TEST",
        "FSL_QMAN_TEST_API",
        "FSL_QMAN_TEST_STASH",
        "KALLSYMS_SELFTEST",
        "SERIAL_NUVOTON_MA35D1_CONSOLE",
        "KCOV",
        "LOCK_TORTURE_TEST",
        "OF_UNITTEST",
        "RCU_REF_SCALE_TEST",
        "RCU_SCALE_TEST",
        "RCU_TORTURE_TEST",
        "RUNTIME_TESTING_MENU",
        "SCF_TORTURE_TEST",
        "TEST_CLOCKSOURCE_WATCHDOG",
    }
    require(
        required_boot_disables <= disable_symbols,
        f"missing disable guards: {sorted(required_boot_disables - disable_symbols)}",
    )
    require(
        required_boot_disables <= forbidden_symbols,
        f"missing fail-closed guards: {sorted(required_boot_disables - forbidden_symbols)}",
    )

    enable = re.search(
        r"for symbol in \\\n(?P<body>(?:(?!\ndone).)*?)\n"
        r'\s*"\$cfg" [^\n]* --enable "\$symbol"\ndone',
        text,
        re.DOTALL,
    )
    require(enable is not None, "bootability enable loop was not found")
    enable_symbols = set(re.findall(r"[A-Z][A-Z0-9_]+", enable.group("body")))

    required_builtin = re.search(r"for required_builtin in (?P<body>[^;]+); do", text)
    require(
        required_builtin is not None,
        "post-olddefconfig required-built-in loop was not found",
    )
    required_builtin_symbols = set(
        re.findall(r"[A-Z][A-Z0-9_]+", required_builtin.group("body"))
    )
    require("BINFMT_SCRIPT" in enable_symbols, "BINFMT_SCRIPT must be built in for /init")
    require(
        "BINFMT_SCRIPT" in required_builtin_symbols,
        "BINFMT_SCRIPT=y must be checked after olddefconfig",
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

    smoke_init = re.search(
        r"cat > \"\$root/init\" <<'INIT'\n(?P<body>.*?)\nINIT",
        text,
        re.DOTALL,
    )
    require(smoke_init is not None, "direct-smoke /init heredoc was not found")
    init_commands = [
        line
        for line in smoke_init.group("body").splitlines()
        if line and not line.startswith("#!")
    ]
    require(
        init_commands[0] == "echo ZIGUX_KERNEL_BOOT_OK",
        "the PID 1 marker must be the first smoke-init command",
    )
    require(
        not any(command.startswith("mount ") for command in init_commands),
        "direct PID 1 smoke must not block on filesystem/module setup",
    )

    print("CachyOS boot config contract: OK")


if __name__ == "__main__":
    main()
