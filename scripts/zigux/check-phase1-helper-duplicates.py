#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DEFAULT_FILES = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/string.zig",
    "tools/lib/rbtree.zig",
)

TOP_LEVEL_FN_RE = re.compile(r"^(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def scan_file(path: Path) -> dict[str, list[int]]:
    seen: dict[str, list[int]] = defaultdict(list)
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = TOP_LEVEL_FN_RE.match(line)
        if match:
            seen[match.group(1)].append(lineno)
    return {name: lines for name, lines in seen.items() if len(lines) > 1}


def run_check(root: Path, files: tuple[str, ...]) -> int:
    failures: list[str] = []
    for rel in files:
        path = root / rel
        if not path.exists():
            failures.append(f"MISSING {rel}")
            continue
        duplicates = scan_file(path)
        for name, lines in sorted(duplicates.items()):
            joined = ",".join(str(line) for line in lines)
            failures.append(f"DUPLICATE {rel} {name} {joined}")

    if failures:
        print("PHASE1_HELPER_DUPLICATES=fail")
        for failure in failures:
            print(f"PHASE1_HELPER_DUPLICATES_ISSUE={failure}")
        return 1

    print("PHASE1_HELPER_DUPLICATES=pass")
    print(f"PHASE1_HELPER_DUPLICATES_FILE_COUNT={len(files)}")
    return 0


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1_helper_duplicates_") as tmp:
        root = Path(tmp)
        write(
            root / "tools/lib/pass.zig",
            "\n".join(
                (
                    "pub fn alpha() void {}",
                    "fn beta() void {}",
                    'test "duplicate-looking text does not count: pub fn alpha() void {}" {}',
                    "",
                )
            ),
        )
        write(
            root / "tools/lib/fail.zig",
            "\n".join(
                (
                    "pub fn alpha() void {}",
                    "fn beta() void {}",
                    "pub fn alpha() void {}",
                    "fn beta() void {}",
                    "",
                )
            ),
        )

        pass_rc = run_check(root, ("tools/lib/pass.zig",))
        fail_rc = run_check(root, ("tools/lib/fail.zig",))
        if pass_rc != 0 or fail_rc != 1:
            print("PHASE1_HELPER_DUPLICATES_SELF_TEST=fail")
            return 1

    print("PHASE1_HELPER_DUPLICATES_SELF_TEST=pass")
    print("PHASE1_HELPER_DUPLICATES_SELF_TEST_CASE_COUNT=2")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Phase 1 helper files for duplicate top-level Zig function definitions.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--files", nargs="*", default=list(DEFAULT_FILES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve(), tuple(args.files))


if __name__ == "__main__":
    raise SystemExit(main())
