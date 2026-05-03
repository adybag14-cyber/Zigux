#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
SELF_TEST_CASE_COUNT = 5

DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
REQUIRED_SCRIPT_PATHS = [
    Path("scripts/zigux/check-phase6-base64-c-parity.py"),
    Path("scripts/zigux/check-phase6-bsearch-c-parity.py"),
    Path("scripts/zigux/check-phase6-checksum-c-parity.py"),
    Path("scripts/zigux/check-phase6-hexdump-c-parity.py"),
]

EXTERNAL_PARITY_LINE = (
    "`python3 scripts/zigux/check-phase6-base64-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and "
    "`python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the shipped "
    "external C-vs-Zig review hooks for the bounded base64, bsearch, checksum, "
    "and hexdump portability surfaces."
)


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def normalized_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines()]


def validate(root: Path) -> list[str]:
    missing: list[str] = []

    required_paths = [DOCS_ROOT_PATH, *REQUIRED_SCRIPT_PATHS]
    for relative_path in required_paths:
        if not (root / relative_path).exists():
            missing.append(f"missing_file:{relative_path.as_posix()}")

    if missing:
        return missing

    docs_root_lines = normalized_lines(read_text(root, DOCS_ROOT_PATH))
    actual_count = sum(1 for line in docs_root_lines if line == EXTERNAL_PARITY_LINE)
    if actual_count != 1:
        missing.append(
            "docs_root_external_parity_line:"
            f"expected=1:actual={actual_count}"
        )

    return missing


def write(root: Path, relative_path: Path, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_fixture_tree(root: Path) -> None:
    write(root, DOCS_ROOT_PATH, f"{EXTERNAL_PARITY_LINE}\n")
    for relative_path in REQUIRED_SCRIPT_PATHS:
        write(root, relative_path, "# placeholder\n")


def expect_contains(items: list[str], needle: str) -> None:
    if needle not in items:
        raise AssertionError(f"missing expectation {needle}")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="phase6_docs_root_external_parity_") as temp_dir:
            root = Path(temp_dir)
            count = 0

            build_fixture_tree(root)
            if validate(root):
                raise AssertionError(validate(root))
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text("", encoding="utf-8")
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=0",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                f"{EXTERNAL_PARITY_LINE}\n{EXTERNAL_PARITY_LINE}\n",
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=2",
            )
            count += 1

            build_fixture_tree(root)
            (root / REQUIRED_SCRIPT_PATHS[2]).unlink()
            expect_contains(
                validate(root),
                "missing_file:scripts/zigux/check-phase6-checksum-c-parity.py",
            )
            count += 1

            build_fixture_tree(root)
            docs_root = root / DOCS_ROOT_PATH
            docs_root.write_text(
                docs_root.read_text(encoding="utf-8").replace(
                    "check-phase6-hexdump-c-parity.py",
                    "check-phase6-hexdump-c-parity.py --drift",
                    1,
                ),
                encoding="utf-8",
            )
            expect_contains(
                validate(root),
                "docs_root_external_parity_line:expected=1:actual=0",
            )
            count += 1

            if count != SELF_TEST_CASE_COUNT:
                raise AssertionError(
                    f"expected {SELF_TEST_CASE_COUNT} self-test cases, got {count}"
                )
    except AssertionError as exc:
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST=fail")
        print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST=pass")
    print(f"PHASE6_DOCS_ROOT_EXTERNAL_PARITY_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 6 docs-root external parity inventory line."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = validate(ROOT)
    if missing:
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY=fail")
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_MISSING_END")
        return 1

    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY=pass")
    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_REQUIRED_FILE_COUNT=5")
    print("PHASE6_DOCS_ROOT_EXTERNAL_PARITY_REQUIRED_LINE_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
