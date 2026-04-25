#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import tempfile

from phase3_catalog import discover_phase3_slices
from phase3_check_lib import render_wrapper_stub


def sync_wrappers(entries: list[object], expected: str, check: bool) -> list[str]:
    mismatches: list[str] = []
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
    return mismatches


def run_self_test() -> int:
    expected = render_wrapper_stub()
    stale = "#!/usr/bin/env python3\nprint('stale')\n"

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        missing_wrapper = tmp_dir / "check-phase3-missing.py"
        stale_wrapper = tmp_dir / "check-phase3-stale.py"
        stale_wrapper.write_text(stale, encoding="utf-8", newline="\n")

        entries = [
            SimpleNamespace(check_script=missing_wrapper),
            SimpleNamespace(check_script=stale_wrapper),
        ]

        mismatches = sync_wrappers(entries, expected, check=True)
        assert mismatches == [missing_wrapper.as_posix(), stale_wrapper.as_posix()]
        assert not missing_wrapper.exists()
        assert stale_wrapper.read_text(encoding="utf-8") == stale

        mismatches = sync_wrappers(entries, expected, check=False)
        assert mismatches == [missing_wrapper.as_posix(), stale_wrapper.as_posix()]
        assert missing_wrapper.read_text(encoding="utf-8") == expected
        assert stale_wrapper.read_text(encoding="utf-8") == expected

        mismatches = sync_wrappers(entries, expected, check=True)
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
