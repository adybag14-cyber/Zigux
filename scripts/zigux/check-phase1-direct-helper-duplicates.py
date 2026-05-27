#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent

HELPERS = (
    Path("tools/lib/bitmap.zig"),
    Path("tools/lib/find_bit.zig"),
    Path("tools/lib/string.zig"),
    Path("tools/lib/rbtree.zig"),
)

FUNCTION_RE = re.compile(r"^(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
TEST_RE = re.compile(r'^test\s+"([^"]+)"\s*\{', re.MULTILINE)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_duplicates(items: list[str]) -> list[tuple[str, int]]:
    counts = Counter(items)
    return sorted((name, count) for name, count in counts.items() if count > 1)


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for helper in HELPERS:
        path = root / helper
        if not path.exists():
            issues.append(f"missing:{helper.as_posix()}")
            continue

        text = read_text(path)
        function_duplicates = find_duplicates(FUNCTION_RE.findall(text))
        test_duplicates = find_duplicates(TEST_RE.findall(text))

        for name, count in function_duplicates:
            issues.append(
                f"duplicate_function:{helper.as_posix()}:{name}:count={count}"
            )
        for name, count in test_duplicates:
            issues.append(
                f"duplicate_test:{helper.as_posix()}:{name}:count={count}"
            )

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        print("PHASE1_DIRECT_HELPER_DUPLICATES=fail")
        for issue in issues:
            print(f"PHASE1_DIRECT_HELPER_DUPLICATE_ISSUE={issue}")
        return 1

    print("PHASE1_DIRECT_HELPER_DUPLICATES=pass")
    print(f"PHASE1_DIRECT_HELPER_DUPLICATES_HELPER_COUNT={len(HELPERS)}")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_text(
        root / "tools/lib/bitmap.zig",
        """const std = @import(\"std\");

pub fn bitmap_ok() void {}

test \"bitmap helper stays unique\" {}
""",
    )
    write_text(
        root / "tools/lib/find_bit.zig",
        """pub fn find_ok() void {}

fn private_ok() void {}
""",
    )
    write_text(
        root / "tools/lib/string.zig",
        """pub fn string_ok() void {}

test \"string helper stays unique\" {}
""",
    )
    write_text(
        root / "tools/lib/rbtree.zig",
        """pub fn tree_ok() void {}

test \"tree helper stays unique\" {}
""",
    )


def run_self_test() -> int:
    cases: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="phase1_direct_helper_duplicates_") as tmp_dir:
        tmp = Path(tmp_dir)

        good = tmp / "good"
        build_sample_root(good)
        cases.append(("good", run_check(good) == 0))

        duplicate_function = tmp / "duplicate_function"
        build_sample_root(duplicate_function)
        write_text(
            duplicate_function / "tools/lib/string.zig",
            """pub fn string_ok() void {}
pub fn string_ok() void {}
""",
        )
        cases.append(("duplicate_function", run_check(duplicate_function) == 1))

        duplicate_private_function = tmp / "duplicate_private_function"
        build_sample_root(duplicate_private_function)
        write_text(
            duplicate_private_function / "tools/lib/rbtree.zig",
            """fn helper() void {}
fn helper() void {}
""",
        )
        cases.append(
            ("duplicate_private_function", run_check(duplicate_private_function) == 1)
        )

        duplicate_test = tmp / "duplicate_test"
        build_sample_root(duplicate_test)
        write_text(
            duplicate_test / "tools/lib/find_bit.zig",
            """pub fn find_ok() void {}

test \"shared name\" {}
test \"shared name\" {}
""",
        )
        cases.append(("duplicate_test", run_check(duplicate_test) == 1))

        missing_helper = tmp / "missing_helper"
        build_sample_root(missing_helper)
        (missing_helper / "tools/lib/bitmap.zig").unlink()
        cases.append(("missing_helper", run_check(missing_helper) == 1))

    failed = [name for name, ok in cases if not ok]
    if failed:
        print("PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST=fail")
        for name in failed:
            print(f"PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST_FAILED_CASE={name}")
        return 1

    print("PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST=pass")
    print(
        f"PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST_CASE_COUNT={len(cases)}"
    )
    print(
        "PHASE1_DIRECT_HELPER_DUPLICATES_SELF_TEST_CASES="
        + ",".join(name for name, _ in cases)
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect duplicate top-level helper definitions in direct Phase 1 helpers."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
