#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
FUSED_MARKER = ";pub const "


def find_fused_pub_const_lines(source: str) -> list[int]:
    return [index for index, line in enumerate(source.splitlines(), start=1) if FUSED_MARKER in line]


def validate_bindings(path: Path) -> int:
    source = path.read_text(encoding="utf-8")
    fused_lines = find_fused_pub_const_lines(source)
    if fused_lines:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        print("FUSED_DECLARATIONS_START")
        for line in fused_lines:
            print(f"{path}:{line}:{FUSED_MARKER.strip()}")
        print("FUSED_DECLARATIONS_END")
        return 1
    print("PHASE3_ABI_BINDINGS_SYNTAX=pass")
    print(f"ABI_BINDINGS_PATH={path.relative_to(ROOT).as_posix()}")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_abi_bindings_syntax_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        good = tmp_dir / "good.zig"
        bad = tmp_dir / "bad.zig"
        good.write_text(
            "\n".join(
                [
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;",
                    "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;",
                    "",
                ]
            ),
            encoding="utf-8",
            newline="\n",
        )
        bad.write_text(
            "pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 6;pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;\n",
            encoding="utf-8",
            newline="\n",
        )

        assert find_fused_pub_const_lines(good.read_text(encoding="utf-8")) == []
        assert find_fused_pub_const_lines(bad.read_text(encoding="utf-8")) == [1]
        assert validate_bindings(good) == 0
        assert validate_bindings(bad) == 1

    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect fused top-level Phase 3 ABI binding declarations.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=DEFAULT_BINDINGS,
        help="Bindings file to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated syntax-guard coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return validate_bindings(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
