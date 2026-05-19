#!/usr/bin/env python3
"""Retire stale historical Phase 3 wrapper stubs."""

from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import tempfile


SCRIPT_PREFIX = "check-phase3-"
LEGACY_IMPORT_MARKER = "from phase3_check_lib import run_from_wrapper"
LEGACY_CALL_MARKER = "run_from_wrapper(__file__)"
DEFAULT_SCRIPTS_DIR = Path(__file__).resolve().parent

WRAPPER_STUB = """#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == \"__main__\":
    raise SystemExit(run_from_wrapper(__file__))
"""


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def is_generated_wrapper_script(path: Path, expected: str) -> bool:
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    if current == expected:
        return True
    return LEGACY_IMPORT_MARKER in current and LEGACY_CALL_MARKER in current


def discover_wrapper_scripts(scripts_dir: Path, expected: str) -> list[Path]:
    return [
        path
        for path in sorted(scripts_dir.glob(f"{SCRIPT_PREFIX}*.py"))
        if is_generated_wrapper_script(path, expected)
    ]


def sync_wrappers(
    entries: list[object],
    expected: str,
    check: bool,
    scripts_dir: Path = DEFAULT_SCRIPTS_DIR,
) -> list[str]:
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
    shared_runner_wrapper = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import sys",
            "from phase3_check_lib import run_from_wrapper",
            "",
            'if __name__ == "__main__":',
            "    print(sys.version_info[0])",
            '    raise SystemExit(run_from_wrapper(__file__))',
            "",
        ]
    )

    with tempfile.TemporaryDirectory(prefix="zigux_phase3_wrapper_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        expected_wrapper = tmp_dir / "check-phase3-expected.py"
        missing_wrapper = tmp_dir / "check-phase3-missing.py"
        stale_wrapper = tmp_dir / "check-phase3-expected.py"
        stale_wrapper.write_text(stale, encoding="utf-8", newline="\n")
        obsolete_wrapper = tmp_dir / "check-phase3-stale.py"
        obsolete_wrapper.write_text(expected, encoding="utf-8", newline="\n")
        obsolete_shared_runner_wrapper = tmp_dir / "check-phase3-shared-runner.py"
        obsolete_shared_runner_wrapper.write_text(
            shared_runner_wrapper,
            encoding="utf-8",
            newline="\n",
        )
        support_checker = tmp_dir / "check-phase3-support.py"
        support_checker.write_text("# support\n", encoding="utf-8", newline="\n")

        entries = [
            SimpleNamespace(check_script=expected_wrapper),
            SimpleNamespace(check_script=missing_wrapper),
        ]

        mismatches = sync_wrappers(entries, expected, check=True, scripts_dir=tmp_dir)
        assert mismatches == [
            stale_wrapper.as_posix(),
            missing_wrapper.as_posix(),
            obsolete_shared_runner_wrapper.as_posix(),
            obsolete_wrapper.as_posix(),
        ]
        assert not missing_wrapper.exists()
        assert stale_wrapper.read_text(encoding="utf-8") == stale
        assert obsolete_shared_runner_wrapper.exists()
        assert obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, expected, check=False, scripts_dir=tmp_dir)
        assert mismatches == [
            stale_wrapper.as_posix(),
            missing_wrapper.as_posix(),
            obsolete_shared_runner_wrapper.as_posix(),
            obsolete_wrapper.as_posix(),
        ]
        assert missing_wrapper.read_text(encoding="utf-8") == expected
        assert stale_wrapper.read_text(encoding="utf-8") == expected
        assert not obsolete_shared_runner_wrapper.exists()
        assert not obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, expected, check=True, scripts_dir=tmp_dir)
        assert mismatches == []

    print("PHASE3_WRAPPER_SELF_TEST=pass")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync or retire historical Phase 3 shared-runner wrapper stubs."
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=DEFAULT_SCRIPTS_DIR,
        help="directory that contains Phase 3 wrapper scripts",
    )
    parser.add_argument(
        "--expected-wrapper",
        action="append",
        default=[],
        help="wrapper filename to keep or recreate inside --scripts-dir",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if any stale or missing historical wrapper stub is detected",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run isolated stale-wrapper detection coverage",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    expected = render_wrapper_stub()
    entries = [
        SimpleNamespace(check_script=args.scripts_dir / name)
        for name in sorted(set(args.expected_wrapper))
    ]
    mismatches = sync_wrappers(entries, expected, check=args.check, scripts_dir=args.scripts_dir)

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
