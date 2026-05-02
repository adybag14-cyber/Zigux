#!/usr/bin/env python3
"""Fail-closed Phase 11 HVC header-parity surface checker."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


DRIVER_PATH = Path("drivers/tty/hvc/hvc_console.zig")

STRUCT_NEEDLES = (
    "    exports_kick: bool,",
    "    exports_notifier_add_irq: bool,",
    "    exports_notifier_del_irq: bool,",
    "    exports_notifier_hangup_irq: bool,",
)

SNAPSHOT_NEEDLES = (
    "        .exports_kick = true,",
    "        .exports_notifier_add_irq = true,",
    "        .exports_notifier_del_irq = true,",
    "        .exports_notifier_hangup_irq = true,",
)


def require(text: str, needle: str, path: Path) -> None:
    if needle not in text:
        raise SystemExit(f"{path}: missing expected header parity needle: {needle.strip()}")


def validate_driver(root: Path) -> None:
    driver_path = root / DRIVER_PATH
    driver_text = driver_path.read_text(encoding="utf-8")

    for needle in STRUCT_NEEDLES:
        require(driver_text, needle, DRIVER_PATH)

    for needle in SNAPSHOT_NEEDLES:
        require(driver_text, needle, DRIVER_PATH)

    print("PHASE11_HVC_HEADER_PARITY=pass")
    print(f"PHASE11_HVC_HEADER_PARITY_FIELD_COUNT={len(STRUCT_NEEDLES)}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        driver_path = root / DRIVER_PATH
        driver_path.parent.mkdir(parents=True, exist_ok=True)
        driver_path.write_text(
            "\n".join(
                (
                    "const HeaderParitySnapshot = struct {",
                    *STRUCT_NEEDLES,
                    "};",
                    "",
                    "pub fn headerParitySnapshot() HeaderParitySnapshot {",
                    "    return .{",
                    *SNAPSHOT_NEEDLES,
                    "    };",
                    "}",
                    "",
                )
            ),
            encoding="utf-8",
        )

        validate_driver(root)

        broken_text = driver_path.read_text(encoding="utf-8").replace(
            SNAPSHOT_NEEDLES[-1],
            "",
            1,
        )
        driver_path.write_text(broken_text, encoding="utf-8")

        try:
            validate_driver(root)
        except SystemExit as exc:
            message = str(exc)
            if "exports_notifier_hangup_irq" not in message:
                raise SystemExit(
                    "self-test expected missing hangup irq message, got: " + message
                ) from exc
        else:
            raise SystemExit("self-test expected the broken header parity fixture to fail")

    print("PHASE11_HVC_HEADER_PARITY_SELF_TEST=pass")
    print("PHASE11_HVC_HEADER_PARITY_SELF_TEST_CASE_COUNT=2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the bounded Phase 11 hvc_console header-parity surface."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root that contains drivers/tty/hvc/hvc_console.zig",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in synthetic pass/fail coverage instead of checking a repo tree.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate_driver(Path(args.root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
