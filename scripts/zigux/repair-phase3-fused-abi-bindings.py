#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BINDINGS = ROOT / "zigux" / "bindings" / "abi.zig"
DEFAULT_STATUS_SYMBOL = "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED"
DEFAULT_BUDGET_SYMBOL = "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED"
SELF_TEST_CASE_COUNT = 6


def build_fused_fragment(status_symbol: str, budget_symbol: str) -> str:
    return f"{status_symbol}: u32 = 6; pub const {budget_symbol}: u32 = 1;"


def build_split_fragment(status_symbol: str, budget_symbol: str) -> str:
    return f"{status_symbol}: u32 = 6;\npub const {budget_symbol}: u32 = 1;"


def repair_source(source: str, status_symbol: str, budget_symbol: str) -> tuple[str, bool]:
    fused_fragment = build_fused_fragment(status_symbol, budget_symbol)
    split_fragment = build_split_fragment(status_symbol, budget_symbol)
    fused_count = source.count(fused_fragment)
    split_count = source.count(split_fragment)

    if split_count and fused_count:
        raise ValueError("ambiguous_fragment_state")
    if split_count:
        return source, False
    if fused_count == 0:
        raise ValueError("missing_fused_fragment")
    if fused_count > 1:
        raise ValueError("multiple_fused_fragments")
    return source.replace(fused_fragment, split_fragment, 1), True


def run_check(path: Path, status_symbol: str, budget_symbol: str) -> int:
    try:
        _, changed = repair_source(path.read_text(encoding="utf-8"), status_symbol, budget_symbol)
    except ValueError as exc:
        print("PHASE3_ABI_BINDING_REPAIR_CHECK=fail")
        print(f"PHASE3_ABI_BINDING_REPAIR_ISSUE={path}:{exc}")
        return 1

    if changed:
        print("PHASE3_ABI_BINDING_REPAIR_CHECK=fail")
        print(f"PHASE3_ABI_BINDING_REPAIR_ISSUE={path}:repair_needed")
        return 1

    print("PHASE3_ABI_BINDING_REPAIR_CHECK=pass")
    print(f"PHASE3_ABI_BINDING_REPAIR_PATH={path}")
    return 0


def run_repair(path: Path, status_symbol: str, budget_symbol: str, in_place: bool) -> int:
    try:
        updated, changed = repair_source(path.read_text(encoding="utf-8"), status_symbol, budget_symbol)
    except ValueError as exc:
        print("PHASE3_ABI_BINDING_REPAIR=fail")
        print(f"PHASE3_ABI_BINDING_REPAIR_ISSUE={path}:{exc}")
        return 1

    if not changed:
        print("PHASE3_ABI_BINDING_REPAIR=noop")
        print(f"PHASE3_ABI_BINDING_REPAIR_PATH={path}")
        return 0

    if in_place:
        path.write_text(updated, encoding="utf-8", newline="\n")
        print("PHASE3_ABI_BINDING_REPAIR=updated")
        print(f"PHASE3_ABI_BINDING_REPAIR_PATH={path}")
        return 0

    print(updated, end="")
    return 0


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase3_fused_abi_bindings_") as tmp_dir:
        path = Path(tmp_dir) / "abi.zig"

        path.write_text(
            "\n".join(
                (
                    "pub const PREFIX: u32 = 0;",
                    f"pub const {DEFAULT_STATUS_SYMBOL}: u32 = 6; pub const {DEFAULT_BUDGET_SYMBOL}: u32 = 1;",
                    "pub const SUFFIX: u32 = 2;",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        updated, changed = repair_source(path.read_text(encoding="utf-8"), DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL)
        assert changed
        assert build_split_fragment(DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL) in updated
        case_count += 1

        path.write_text(updated, encoding="utf-8", newline="\n")
        updated_again, changed_again = repair_source(path.read_text(encoding="utf-8"), DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL)
        assert not changed_again
        assert updated_again == updated
        case_count += 1

        path.write_text("pub const PREFIX: u32 = 0;\n", encoding="utf-8", newline="\n")
        try:
            repair_source(path.read_text(encoding="utf-8"), DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL)
        except ValueError as exc:
            assert str(exc) == "missing_fused_fragment"
        else:
            raise AssertionError("missing fragment should fail")
        case_count += 1

        path.write_text(
            "\n".join(
                (
                    f"pub const {DEFAULT_STATUS_SYMBOL}: u32 = 6; pub const {DEFAULT_BUDGET_SYMBOL}: u32 = 1;",
                    f"pub const {DEFAULT_STATUS_SYMBOL}: u32 = 6; pub const {DEFAULT_BUDGET_SYMBOL}: u32 = 1;",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        try:
            repair_source(path.read_text(encoding="utf-8"), DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL)
        except ValueError as exc:
            assert str(exc) == "multiple_fused_fragments"
        else:
            raise AssertionError("multiple fragments should fail")
        case_count += 1

        path.write_text(
            "\n".join(
                (
                    build_split_fragment(DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL),
                    build_fused_fragment(DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL),
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        try:
            repair_source(path.read_text(encoding="utf-8"), DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL)
        except ValueError as exc:
            assert str(exc) == "ambiguous_fragment_state"
        else:
            raise AssertionError("mixed fragment state should fail")
        case_count += 1

        path.write_text(
            "\n".join(
                (
                    f"pub const {DEFAULT_STATUS_SYMBOL}: u32 = 6; pub const {DEFAULT_BUDGET_SYMBOL}: u32 = 1;",
                    "",
                )
            ),
            encoding="utf-8",
            newline="\n",
        )
        assert run_check(path, DEFAULT_STATUS_SYMBOL, DEFAULT_BUDGET_SYMBOL) == 1
        case_count += 1

    print("PHASE3_ABI_BINDING_REPAIR_SELF_TEST=pass")
    print(f"PHASE3_ABI_BINDING_REPAIR_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair the exact fused Phase 3 ABI bindings tail pair without widening into broader wrapper churn."
    )
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--status-symbol", default=DEFAULT_STATUS_SYMBOL)
    parser.add_argument("--budget-symbol", default=DEFAULT_BUDGET_SYMBOL)
    parser.add_argument("--in-place", action="store_true", help="Rewrite the file in place when a repair is possible.")
    parser.add_argument("--check", action="store_true", help="Fail unless the targeted pair is already split.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated helper coverage.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.check:
        return run_check(args.path, args.status_symbol, args.budget_symbol)
    return run_repair(args.path, args.status_symbol, args.budget_symbol, args.in_place)


if __name__ == "__main__":
    raise SystemExit(main())
