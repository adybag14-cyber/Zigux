#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
]

DOCS_ROOT_LINE = (
    "`python3 scripts/zigux/check-phase6-base64-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-bsearch-c-parity.py`, "
    "`python3 scripts/zigux/check-phase6-checksum-c-parity.py`, and "
    "`python3 scripts/zigux/check-phase6-hexdump-c-parity.py` are the shipped "
    "external C-vs-Zig review hooks for the bounded base64, bsearch, checksum, "
    "and hexdump portability surfaces."
)

SCRIPTS_README_LINE = (
    "`check-phase6-base64-c-parity.py`, `check-phase6-bsearch-c-parity.py`, "
    "`check-phase6-checksum-c-parity.py`, and `check-phase6-hexdump-c-parity.py` "
    "remain the four external parity spot checks for the portability-sensitive "
    "helper slices."
)

EXPECTED_SCRIPTS = [
    "check-phase6-base64-c-parity.py",
    "check-phase6-bsearch-c-parity.py",
    "check-phase6-checksum-c-parity.py",
    "check-phase6-hexdump-c-parity.py",
]

SCRIPT_RE = re.compile(r"check-phase6-[a-z0-9-]+\.py")


def text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def require_line_once(missing: list[str], label: str, content: str, line: str) -> None:
    count = content.count(line)
    if count == 0:
        missing.append(f"{label}:missing:{line}")
    elif count != 1:
        missing.append(f"{label}:duplicate:{count}:{line}")


def extract_scripts(line: str) -> list[str]:
    return SCRIPT_RE.findall(line)


def validate_inventory(root: Path) -> dict[str, object]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return {"ok": False, "missing_files": missing_files, "missing": []}

    docs_root = text(root, "Documentation/zigux/README.md")
    scripts_readme = text(root, "scripts/zigux/README.md")

    missing: list[str] = []
    require_line_once(missing, "docs_root", docs_root, DOCS_ROOT_LINE)
    require_line_once(missing, "scripts_readme", scripts_readme, SCRIPTS_README_LINE)

    docs_inventory = extract_scripts(DOCS_ROOT_LINE)
    scripts_inventory = extract_scripts(SCRIPTS_README_LINE)
    if docs_inventory != EXPECTED_SCRIPTS:
        missing.append(f"docs_root:inventory:{docs_inventory!r}")
    if scripts_inventory != EXPECTED_SCRIPTS:
        missing.append(f"scripts_readme:inventory:{scripts_inventory!r}")

    return {"ok": not missing, "missing_files": [], "missing": missing}


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_self_test_tree(root: Path) -> None:
    write(root, "Documentation/zigux/README.md", f"{DOCS_ROOT_LINE}\n")
    write(root, "scripts/zigux/README.md", f"{SCRIPTS_README_LINE}\n")


def run_self_test() -> int:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            build_self_test_tree(root)
            result = validate_inventory(root)
            if not result["ok"]:
                raise AssertionError(result)

            build_self_test_tree(root)
            docs = root / "Documentation/zigux/README.md"
            docs.write_text("", encoding="utf-8")
            if f"docs_root:missing:{DOCS_ROOT_LINE}" not in validate_inventory(root)["missing"]:
                raise AssertionError("missing docs-root failure")

            build_self_test_tree(root)
            docs = root / "Documentation/zigux/README.md"
            docs.write_text(f"{DOCS_ROOT_LINE}\n{DOCS_ROOT_LINE}\n", encoding="utf-8")
            if f"docs_root:duplicate:2:{DOCS_ROOT_LINE}" not in validate_inventory(root)["missing"]:
                raise AssertionError("missing docs-root duplicate failure")

            build_self_test_tree(root)
            scripts = root / "scripts/zigux/README.md"
            scripts.write_text("", encoding="utf-8")
            if f"scripts_readme:missing:{SCRIPTS_README_LINE}" not in validate_inventory(root)["missing"]:
                raise AssertionError("missing scripts-readme failure")

            build_self_test_tree(root)
            scripts = root / "scripts/zigux/README.md"
            scripts.write_text(f"{SCRIPTS_README_LINE}\n{SCRIPTS_README_LINE}\n", encoding="utf-8")
            if f"scripts_readme:duplicate:2:{SCRIPTS_README_LINE}" not in validate_inventory(root)["missing"]:
                raise AssertionError("missing scripts-readme duplicate failure")

            build_self_test_tree(root)
            docs = root / "Documentation/zigux/README.md"
            docs.write_text(
                DOCS_ROOT_LINE.replace("check-phase6-hexdump-c-parity.py", "check-phase6-missing-c-parity.py"),
                encoding="utf-8",
            )
            if f"docs_root:missing:{DOCS_ROOT_LINE}" not in validate_inventory(root)["missing"]:
                raise AssertionError("missing docs-root exact-line failure")

            build_self_test_tree(root)
            (root / "Documentation/zigux/README.md").unlink()
            if "Documentation/zigux/README.md" not in validate_inventory(root)["missing_files"]:
                raise AssertionError("missing docs-root file failure")

            build_self_test_tree(root)
            (root / "scripts/zigux/README.md").unlink()
            if "scripts/zigux/README.md" not in validate_inventory(root)["missing_files"]:
                raise AssertionError("missing scripts-readme file failure")
    except AssertionError as exc:
        print("PHASE6_EXTERNAL_PARITY_INVENTORY_SELF_TEST=fail")
        print(f"PHASE6_EXTERNAL_PARITY_INVENTORY_SELF_TEST_REASON={exc}")
        return 1

    print("PHASE6_EXTERNAL_PARITY_INVENTORY_SELF_TEST=pass")
    print("PHASE6_EXTERNAL_PARITY_INVENTORY_SELF_TEST_CASE_COUNT=8")
    return 0


def report(result: dict[str, object]) -> int:
    if result["missing_files"]:
        print("PHASE6_EXTERNAL_PARITY_INVENTORY=fail")
        print("MISSING_FILES_START")
        for path in result["missing_files"]:
            print(path)
        print("MISSING_FILES_END")
        return 1
    if result["missing"]:
        print("PHASE6_EXTERNAL_PARITY_INVENTORY=fail")
        print("MISSING_MARKERS_START")
        for item in result["missing"]:
            print(item)
        print("MISSING_MARKERS_END")
        return 1
    print("PHASE6_EXTERNAL_PARITY_INVENTORY=pass")
    print("PHASE6_EXTERNAL_PARITY_SCRIPT_COUNT=4")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 6 external parity inventory across the docs root and scripts index."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    return report(validate_inventory(args.root))


if __name__ == "__main__":
    sys.exit(main())
