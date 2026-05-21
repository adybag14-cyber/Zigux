#!/usr/bin/env python3
"""Validate the current Phase 1 repo-reality gap packet."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


REQUIRED_PRESENT_FILES = {
    "scripts/zigux/install-zig.py": "#!/usr/bin/env python3",
    "scripts/zigux/check-phase1-bench.py": "#!/usr/bin/env python3",
}

REQUIRED_MISSING_FILES = (
    "scripts/zigux/check-phase1-installer-review-surfaces.py",
    "scripts/zigux/check-phase1-installer-companion-checks.py",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

SELF_TEST_CASES = (
    "sample_pass",
    "present_file_missing",
    "present_file_directory",
    "present_file_bad_header",
    "missing_file_present",
)


def repo_root_from(path: Path) -> Path:
    if path.is_dir():
        return path
    return path.parent


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_sample_root(root: Path) -> None:
    for rel_path, prefix in REQUIRED_PRESENT_FILES.items():
        write_text(root / rel_path, f"{prefix}\n# sample\n")


def validate(root: Path) -> tuple[bool, list[str]]:
    details: list[str] = []
    ok = True

    for rel_path, prefix in REQUIRED_PRESENT_FILES.items():
        path = root / rel_path
        if not path.exists():
            ok = False
            details.append(f"PRESENT_MISSING={rel_path}")
            continue
        if not path.is_file():
            ok = False
            details.append(f"PRESENT_NOT_FILE={rel_path}")
            continue
        first_line = path.read_text(encoding="utf-8").splitlines()[0] if path.read_text(encoding="utf-8") else ""
        if first_line != prefix:
            ok = False
            details.append(f"PRESENT_BAD_PREFIX={rel_path}:{first_line!r}")

    for rel_path in REQUIRED_MISSING_FILES:
        path = root / rel_path
        if path.exists():
            ok = False
            details.append(f"MISSING_PRESENT={rel_path}")

    details.append(f"PHASE1_REPO_REALITY_PRESENT_COUNT={len(REQUIRED_PRESENT_FILES)}")
    details.append(f"PHASE1_REPO_REALITY_MISSING_COUNT={len(REQUIRED_MISSING_FILES)}")
    return ok, details


def assert_case(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def run_self_test() -> int:
    covered: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_repo_reality_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        ok, details = validate(root)
        assert_case(ok, "sample_pass")
        assert_case("PHASE1_REPO_REALITY_PRESENT_COUNT=2" in details, "sample_pass")
        assert_case("PHASE1_REPO_REALITY_MISSING_COUNT=8" in details, "sample_pass")
        covered.append("sample_pass")

        missing_root = root / "missing"
        build_sample_root(missing_root)
        (missing_root / "scripts/zigux/install-zig.py").unlink()
        ok, details = validate(missing_root)
        assert_case(not ok and "PRESENT_MISSING=scripts/zigux/install-zig.py" in details, "present_file_missing")
        covered.append("present_file_missing")

        dir_root = root / "directory"
        build_sample_root(dir_root)
        bad_path = dir_root / "scripts/zigux/check-phase1-bench.py"
        bad_path.unlink()
        bad_path.mkdir(parents=True)
        ok, details = validate(dir_root)
        assert_case(not ok and "PRESENT_NOT_FILE=scripts/zigux/check-phase1-bench.py" in details, "present_file_directory")
        covered.append("present_file_directory")

        prefix_root = root / "prefix"
        build_sample_root(prefix_root)
        write_text(prefix_root / "scripts/zigux/install-zig.py", "#!/usr/bin/env bash\n")
        ok, details = validate(prefix_root)
        assert_case(
            not ok
            and "PRESENT_BAD_PREFIX=scripts/zigux/install-zig.py:'#!/usr/bin/env bash'" in details,
            "present_file_bad_header",
        )
        covered.append("present_file_bad_header")

        extra_root = root / "extra"
        build_sample_root(extra_root)
        write_text(extra_root / "scripts/zigux/validate-phase1.py", "#!/usr/bin/env python3\n")
        ok, details = validate(extra_root)
        assert_case(not ok and "MISSING_PRESENT=scripts/zigux/validate-phase1.py" in details, "missing_file_present")
        covered.append("missing_file_present")

    assert_case(tuple(covered) == SELF_TEST_CASES, "self_test_case_order")
    print("PHASE1_REPO_REALITY_SELF_TEST=pass")
    print(f"PHASE1_REPO_REALITY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check the current Phase 1 repo-reality gap packet.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to inspect.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a current-master-shaped sample repo root and exit.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        target = repo_root_from(args.write_sample_root)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        build_sample_root(target)
        return 0

    root = repo_root_from(args.root)
    ok, details = validate(root)
    print(f"PHASE1_REPO_REALITY={'pass' if ok else 'fail'}")
    for line in details:
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
