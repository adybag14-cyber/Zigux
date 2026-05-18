#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

BOOTSTRAP_ROOT = Path("zigux-alpha")
REQUIRED_FILES = (
    BOOTSTRAP_ROOT / "README.md",
    BOOTSTRAP_ROOT / "ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    BOOTSTRAP_ROOT / "BOOTSTRAP_COMMIT_LEDGER.md",
)
FORBIDDEN_DIRS = (
    "Documentation",
    "drivers",
    "fs",
    "include",
    "kernel",
    "lib",
    "mm",
    "net",
    "ports",
    "samples",
    "scripts",
    "security",
    "tools",
    "zigux",
)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    flagged_forbidden_dirs: set[Path] = set()

    bootstrap_root = root / BOOTSTRAP_ROOT
    if not bootstrap_root.is_dir():
        return [f"missing-bootstrap-root:{BOOTSTRAP_ROOT.as_posix()}"]

    for required_file in REQUIRED_FILES:
        full_path = root / required_file
        if not full_path.is_file():
            failures.append(f"missing-file:{required_file.as_posix()}")

    for directory in sorted(
        (path for path in bootstrap_root.rglob("*") if path.is_dir()),
        key=lambda path: (len(path.parts), path.as_posix()),
    ):
        relative_path = directory.relative_to(root)
        if any(parent in flagged_forbidden_dirs for parent in directory.parents):
            continue
        if directory.name in FORBIDDEN_DIRS:
            failures.append(f"forbidden-dir:{relative_path.as_posix()}")
            flagged_forbidden_dirs.add(directory)

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_root(root: Path) -> None:
    _write(
        root / (BOOTSTRAP_ROOT / "README.md"),
        "# zigux-alpha\n\n`zigux-alpha` is the Zigux bootstrap workspace.\n",
    )
    _write(
        root / (BOOTSTRAP_ROOT / "ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"),
        "# ZAR to Zigux Product Roadmap\n",
    )
    _write(
        root / (BOOTSTRAP_ROOT / "BOOTSTRAP_COMMIT_LEDGER.md"),
        "# Zigux Alpha Bootstrap Commit Ledger\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_tree_shape_") as tmp_dir:
        root = Path(tmp_dir)
        _sample_root(root)

        if collect_failures(root):
            raise AssertionError("baseline Lane 01 bootstrap tree fixture should pass")
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "README.md")).unlink()
        failures = collect_failures(root)
        expected = ["missing-file:zigux-alpha/README.md"]
        if failures != expected:
            raise AssertionError(f"unexpected README failure list: {failures}")
        _sample_root(root)
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")).unlink()
        failures = collect_failures(root)
        expected = ["missing-file:zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md"]
        if failures != expected:
            raise AssertionError(f"unexpected roadmap failure list: {failures}")
        _sample_root(root)
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "BOOTSTRAP_COMMIT_LEDGER.md")).unlink()
        failures = collect_failures(root)
        expected = ["missing-file:zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md"]
        if failures != expected:
            raise AssertionError(f"unexpected ledger failure list: {failures}")
        _sample_root(root)
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "ports")).mkdir(parents=True, exist_ok=True)
        failures = collect_failures(root)
        expected = ["forbidden-dir:zigux-alpha/ports"]
        if failures != expected:
            raise AssertionError(f"unexpected ports failure list: {failures}")
        (root / (BOOTSTRAP_ROOT / "ports")).rmdir()
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "drivers" / "virtio")).mkdir(parents=True, exist_ok=True)
        failures = collect_failures(root)
        expected = [
            "forbidden-dir:zigux-alpha/drivers",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected drivers failure list: {failures}")
        (root / (BOOTSTRAP_ROOT / "drivers" / "virtio")).rmdir()
        (root / (BOOTSTRAP_ROOT / "drivers")).rmdir()
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "zigux" / "helpers")).mkdir(parents=True, exist_ok=True)
        failures = collect_failures(root)
        expected = [
            "forbidden-dir:zigux-alpha/zigux",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected zigux failure list: {failures}")
        (root / (BOOTSTRAP_ROOT / "zigux" / "helpers")).rmdir()
        (root / (BOOTSTRAP_ROOT / "zigux")).rmdir()
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "tools" / "lib")).mkdir(parents=True, exist_ok=True)
        failures = collect_failures(root)
        expected = [
            "forbidden-dir:zigux-alpha/tools",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected tools failure list: {failures}")
        (root / (BOOTSTRAP_ROOT / "tools" / "lib")).rmdir()
        (root / (BOOTSTRAP_ROOT / "tools")).rmdir()
        case_count += 1

        (root / (BOOTSTRAP_ROOT / "samples" / "zigux")).mkdir(parents=True, exist_ok=True)
        failures = collect_failures(root)
        expected = [
            "forbidden-dir:zigux-alpha/samples",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected samples failure list: {failures}")
        (root / (BOOTSTRAP_ROOT / "samples" / "zigux")).rmdir()
        (root / (BOOTSTRAP_ROOT / "samples")).rmdir()
        case_count += 1

    print("LANE01_BOOTSTRAP_TREE_SHAPE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_TREE_SHAPE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that zigux-alpha stays a small bootstrap workspace."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic bootstrap workspace fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Lane 01 bootstrap tree shape check passed.")
    print(f"LANE01_BOOTSTRAP_TREE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"LANE01_BOOTSTRAP_TREE_FORBIDDEN_DIR_COUNT={len(FORBIDDEN_DIRS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
