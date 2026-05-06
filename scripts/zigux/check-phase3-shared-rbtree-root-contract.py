#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


REQUIRED_SNIPPETS = (
    "fn isValidRbtreeRootView(view: abi.RbtreeRootView) bool {",
    "fn canonicalizeRbtreeRootView(view: abi.RbtreeRootView) ?abi.RbtreeRootView {",
    "!isRbtreeEmpty(view) and view.root_addr == 0",
    "hasRbtreeLeftmost(view) != isRbtreeCached(view)",
    "isRbtreeCached(view) and view.leftmost_addr == 0",
    "PHASE3_SHARED_RBTREE_INVALID_RECORDS=rootless-uncached,cached-without-leftmost-addr,cached-without-leftmost-flag,leftmost-without-cached-flag",
    "const rootless_uncached: abi.RbtreeRootView = .{",
    "const cached_without_leftmost_addr: abi.RbtreeRootView = .{",
    "const cached_without_leftmost_flag: abi.RbtreeRootView = .{",
    "const leftmost_without_cached_flag: abi.RbtreeRootView = .{",
)


def validate_source(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_source:{path.as_posix()}"]

    issues: list[str] = []
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in source:
            issues.append(f"missing_snippet:{snippet}")
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase3_shared_rbtree_root_contract_") as tmp_dir:
        path = Path(tmp_dir) / "phase3_abi.zig"
        path.write_text("\n".join(REQUIRED_SNIPPETS) + "\n", encoding="utf-8")
        issues = validate_source(path)
        if issues:
            raise AssertionError(f"unexpected self-test failure: {issues}")

        path.write_text("\n".join(REQUIRED_SNIPPETS[:-1]) + "\n", encoding="utf-8")
        issues = validate_source(path)
        expected = f"missing_snippet:{REQUIRED_SNIPPETS[-1]}"
        if issues != [expected]:
            raise AssertionError(f"unexpected self-test issues: {issues}")

    print("PHASE3_SHARED_RBTREE_ROOT_CONTRACT_SELFTEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Require the shared Phase 3 rbtree root-view contract markers in zigux/tests/phase3_abi.zig."
    )
    parser.add_argument(
        "--source",
        default="zigux/tests/phase3_abi.zig",
        help="Path to the shared Phase 3 ABI Zig source to inspect.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run the checker in a temporary isolated workspace.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_source(Path(args.source))
    if issues:
        print("PHASE3_SHARED_RBTREE_ROOT_CONTRACT=fail")
        print("PHASE3_SHARED_RBTREE_ROOT_CONTRACT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_SHARED_RBTREE_ROOT_CONTRACT_ISSUES_END")
        return 1

    print("PHASE3_SHARED_RBTREE_ROOT_CONTRACT=pass")
    print(f"PHASE3_SHARED_RBTREE_ROOT_CONTRACT_SNIPPET_COUNT={len(REQUIRED_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
