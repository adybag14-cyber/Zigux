#!/usr/bin/env python3
"""Guard the live Phase 1 closure-validator inventory against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[1] if len(HERE.parents) > 1 else HERE.parent
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_PATH_MARKERS = (
    'REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")',
    'ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")',
    'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
    'SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")',
    'ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")',
    'BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")',
    'FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")',
    'RBTREE_HELPER_REL = Path("tools/lib/rbtree.zig")',
    'STRING_HELPER_REL = Path("tools/lib/string.zig")',
)

REQUIRED_FILE_ENTRIES = (
    "    REVIEW_CHECKLIST_REL,",
    "    ROUTE_SUMMARY_CHECKER_REL,",
    "    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,",
    "    SHARED_REMINDER_CHECKER_REL,",
    "    ZIGUX_MAKEFILE_REL,",
    "    BITMAP_HELPER_REL,",
    "    FIND_BIT_HELPER_REL,",
    "    RBTREE_HELPER_REL,",
    "    STRING_HELPER_REL,",
)

REQUIRED_DELEGATED_CHECKERS = (
    '    (STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),',
    '    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
    '    (DIRECT_OWNER_CHECKER_REL, "phase1-direct-owner-markers"),',
    '    (ROUTE_SUMMARY_CHECKER_REL, "phase1-route-summary-counts"),',
    '    (BENCH_CHECKER_REL, "phase1-bench"),',
    '    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    '    (SHARED_REMINDER_CHECKER_REL, "phase1-shared-reminder-packet"),',
)

REQUIRED_CONTROL_MARKERS = (
    "def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:",
    "    for script_rel, label in DELEGATED_CHECKERS:",
    '    print("PHASE1_CLOSURE_SELF_TEST=pass")',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def expect_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    path = root / VALIDATOR_REL
    if not path.is_file():
        return [f"missing_file:{VALIDATOR_REL.as_posix()}"]

    text = read_text(root, VALIDATOR_REL)
    failures: list[str] = []
    for marker in REQUIRED_PATH_MARKERS:
        failures.extend(expect_once(text, f"path_marker:{marker}", marker))
    for marker in REQUIRED_FILE_ENTRIES:
        failures.extend(expect_once(text, f"required_files:{marker}", marker))
    for marker in REQUIRED_DELEGATED_CHECKERS:
        failures.extend(expect_once(text, f"delegated_checker:{marker}", marker))
    for marker in REQUIRED_CONTROL_MARKERS:
        failures.extend(expect_once(text, f"control_marker:{marker}", marker))
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_source() -> str:
    sections = [
        "#!/usr/bin/env python3",
        *REQUIRED_PATH_MARKERS,
        "REQUIRED_FILES = (",
        *REQUIRED_FILE_ENTRIES,
        ")",
        "DELEGATED_CHECKERS = (",
        *REQUIRED_DELEGATED_CHECKERS,
        ")",
        *REQUIRED_CONTROL_MARKERS,
        "",
    ]
    return "\n".join(sections)


def remove_once(text: str, marker: str) -> str:
    return text.replace(marker + "\n", "", 1)


def duplicate_once(text: str, marker: str) -> str:
    return text.replace(marker, marker + "\n" + marker, 1)


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str | None]] = [("baseline", None, None)]
    for marker in REQUIRED_PATH_MARKERS:
        cases.append(("remove_path_marker", marker, "remove"))
    for marker in REQUIRED_FILE_ENTRIES:
        cases.append(("remove_required_file_entry", marker, "remove"))
    for marker in REQUIRED_DELEGATED_CHECKERS:
        cases.append(("remove_delegated_checker", marker, "remove"))
    cases.append(("duplicate_delegated_checker", REQUIRED_DELEGATED_CHECKERS[3], "duplicate"))
    cases.append(("remove_control_marker", REQUIRED_CONTROL_MARKERS[1], "remove"))

    for name, marker, mode in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-validator-inventory-") as tmpdir:
            root = Path(tmpdir)
            validator_path = root / VALIDATOR_REL
            text = fixture_source()
            if mode == "remove" and marker is not None:
                text = remove_once(text, marker)
            elif mode == "duplicate" and marker is not None:
                text = duplicate_once(text, marker)
            write_text(validator_path, text)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print("self-test:baseline:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_VALIDATOR_INVENTORY_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_INVENTORY_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_VALIDATOR_INVENTORY=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_VALIDATOR_INVENTORY=pass")
    print(f"PHASE1_CLOSURE_VALIDATOR_INVENTORY_REQUIRED_PATH_MARKER_COUNT={len(REQUIRED_PATH_MARKERS)}")
    print(f"PHASE1_CLOSURE_VALIDATOR_INVENTORY_REQUIRED_FILE_ENTRY_COUNT={len(REQUIRED_FILE_ENTRIES)}")
    print(f"PHASE1_CLOSURE_VALIDATOR_INVENTORY_DELEGATED_CHECKER_COUNT={len(REQUIRED_DELEGATED_CHECKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
