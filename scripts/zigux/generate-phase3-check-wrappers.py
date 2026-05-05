#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import tempfile

from phase3_catalog import DEFAULT_PATHS, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub


def is_generated_wrapper_script(path: Path, expected: str) -> bool:
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    if current == expected:
        return True
    return (
        "from phase3_check_lib import run_from_wrapper" in current
        and "run_from_wrapper(__file__)" in current
    )


def discover_wrapper_scripts(scripts_dir: Path, expected: str) -> list[Path]:
    return [
        path
        for path in sorted(scripts_dir.glob("check-phase3-*.py"))
        if is_generated_wrapper_script(path, expected)
    ]


def sync_wrappers(entries: list[object], expected: str, check: bool, scripts_dir: Path = DEFAULT_PATHS.scripts_dir) -> list[str]:
    mismatches: list[str] = []
    expected_paths = {entry.check_script for entry in entries}

    for entry in entries:
        path = entry.check_script
        if not path.exists():
            mismatches.append(path.as_posix())
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding="utf-8", newline="\n")
            continue
        current = path.read_text(encoding="utf-8")
        if current != expected:
            mismatches.append(path.as_posix())
            if not check:
                path.write_text(expected, encoding="utf-8", newline="\n")

    for path in discover_wrapper_scripts(scripts_dir, expected):
        if path in expected_paths:
            continue
        mismatches.append(path.as_posix())
        if not check:
            path.unlink()

    return mismatches


def run_self_test() -> int:
    expected = render_wrapper_stub()
    stale = "#!/usr/bin/env python3\nprint('stale')\n"

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected_wrapper = tmp_dir / "check-phase3-expected.py"
        missing_wrapper = tmp_dir / "check-phase3-missing.py"
        stale_wrapper = tmp_dir / "check-phase3-expected.py"
        stale_wrapper.write_text(stale, encoding="utf-8", newline="\n")
        obsolete_wrapper = tmp_dir / "check-phase3-stale.py"
        obsolete_wrapper.write_text(expected, encoding="utf-8", newline="\n")
        support_checker = tmp_dir / "check-phase3-support.py"
        support_checker.write_text("# support\n", encoding="utf-8", newline="\n")

        entries = [
            SimpleNamespace(check_script=expected_wrapper),
            SimpleNamespace(check_script=missing_wrapper),
        ]

        mismatches = sync_wrappers(entries, expected, check=True, scripts_dir=tmp_dir)
        assert mismatches == [stale_wrapper.as_posix(), missing_wrapper.as_posix(), obsolete_wrapper.as_posix()]
        assert not missing_wrapper.exists()
        assert stale_wrapper.read_text(encoding="utf-8") == stale
        assert obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, expected, check=False, scripts_dir=tmp_dir)
        assert mismatches == [stale_wrapper.as_posix(), missing_wrapper.as_posix(), obsolete_wrapper.as_posix()]
        assert missing_wrapper.read_text(encoding="utf-8") == expected
        assert stale_wrapper.read_text(encoding="utf-8") == expected
        assert not obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, expected, check=True, scripts_dir=tmp_dir)
        assert mismatches == []

    print("PHASE3_WRAPPER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate template-backed Phase 3 wrapper scripts.")
    parser.add_argument("--check", action="store_true", help="Fail if any wrapper does not match the generated stub.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated wrapper rewrite and drift checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    expected = render_wrapper_stub()
    mismatches = sync_wrappers(discover_phase3_slices(), expected, check=args.check)

    if mismatches and args.check:
        print("PHASE3_WRAPPER_TEMPLATES=fail")
        for path in mismatches:
            print(path)
        return 1

    if args.check:
        print("PHASE3_WRAPPER_TEMPLATES=pass")
    else:
        print(f"PHASE3_WRAPPER_TEMPLATES=updated:{len(mismatches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())