#!/usr/bin/env python3
"""Check blank-line spacing across the packed Phase 3 ABI tail bindings."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ABI_BINDINGS = Path("zigux/bindings/abi.zig")
TARGET_PREFIX = "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_"
SELF_TEST_CASE_COUNT = 5


def top_level_const_name(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("pub const "):
        return None
    name = stripped[len("pub const ") :].split(":", 1)[0].strip()
    return name or None


def validate_tail_spacing(path: Path) -> list[str]:
    issues: list[str] = []
    previous_name: str | None = None
    previous_line: int | None = None
    with path.open("r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    for line_number, line in enumerate(lines, start=1):
        name = top_level_const_name(line)
        if name is None or not name.startswith(TARGET_PREFIX):
            continue
        if previous_name is not None and previous_line is not None and line_number == previous_line + 1:
            issues.append(
                f"{path}:{previous_line}-{line_number}:missing_blank_line_between_tail_consts:"
                f"{previous_name}->{name}"
            )
        previous_name = name
        previous_line = line_number
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = Path(tmp_dir) / "abi.zig"
        target.write_text(
            "\n".join(
                [
                    "pub const OTHER_PREFIX: u32 = 0;",
                    "",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE: u32 = 0;",
                    "",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED: u32 = 1;",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_tail_spacing(target) == []

        target.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE: u32 = 0;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED: u32 = 1;",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_tail_spacing(target) == [
            f"{target}:1-2:missing_blank_line_between_tail_consts:"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE->"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED"
        ]

        target.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE: u32 = 0;",
                    "",
                    "pub const OTHER_PREFIX: u32 = 0;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED: u32 = 1;",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_tail_spacing(target) == []

        target.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED: u32 = 5;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;",
                    "",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;",
                    "",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_USED: u32 = 2;",
                    "",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED: u32 = 4;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED: u32 = 8;",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        assert validate_tail_spacing(target) == [
            f"{target}:1-2:missing_blank_line_between_tail_consts:"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED->"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
            f"{target}:8-9:missing_blank_line_between_tail_consts:"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED->"
            "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED",
        ]

        target.write_text("\n", encoding="utf-8", newline="\n")
        assert validate_tail_spacing(target) == []

    print(f"PHASE3_ABI_TAIL_SPACING_SELF_TEST_CASES={SELF_TEST_CASE_COUNT}")
    print("PHASE3_ABI_TAIL_SPACING_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Require blank lines between adjacent chrdev notify-ack tail constants in zigux/bindings/abi.zig."
    )
    parser.add_argument(
        "abi_path",
        nargs="?",
        type=Path,
        default=DEFAULT_ABI_BINDINGS,
        help="ABI bindings file to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated spacing-guard coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_tail_spacing(args.abi_path)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print(f"PHASE3_ABI_TAIL_SPACING_OK={args.abi_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
