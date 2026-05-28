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


if __name__ == "__main__":
    raise SystemExit(run_from_wrapper(__file__))
"""


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def normalize_expected_wrapper_name(name: str) -> str:
    candidate = Path(name)
    if candidate.is_absolute():
        raise ValueError(f"expected wrapper must be a basename inside scripts/zigux: {name}")
    if candidate.name != name:
        raise ValueError(f"expected wrapper must not include path separators: {name}")
    if not name.startswith(SCRIPT_PREFIX) or not name.endswith(".py"):
        raise ValueError(
            f"expected wrapper must match {SCRIPT_PREFIX}*.py inside scripts/zigux: {name}"
        )
    return name


def normalize_expected_wrapper_path(path: Path, scripts_dir: Path) -> Path:
    scripts_dir_resolved = scripts_dir.resolve(strict=False)
    candidate = Path(path).resolve(strict=False)
    try:
        relative = candidate.relative_to(scripts_dir_resolved)
    except ValueError as exc:
        raise ValueError(
            f"expected wrapper path inside {scripts_dir_resolved}: {path}"
        ) from exc
    if relative.parent != Path("."):
        raise ValueError(
            f"expected wrapper path to live directly inside {scripts_dir_resolved}: {path}"
        )
    normalize_expected_wrapper_name(relative.name)
    return scripts_dir_resolved / relative.name


def build_expected_entries(
    expected_wrapper_names: list[str], scripts_dir: Path
) -> list[object]:
    normalized_names = sorted(
        {normalize_expected_wrapper_name(name) for name in expected_wrapper_names}
    )
    return [
        SimpleNamespace(check_script=scripts_dir / normalized_name)
        for normalized_name in normalized_names
    ]


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
    normalized_expected_paths = [
        normalize_expected_wrapper_path(Path(entry.check_script), scripts_dir)
        for entry in entries
    ]
    expected_paths = set(normalized_expected_paths)

    for path in normalized_expected_paths:
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
    case_count = 0

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
        case_count += 1

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
        case_count += 1

        mismatches = sync_wrappers(entries, expected, check=True, scripts_dir=tmp_dir)
        assert mismatches == []
        case_count += 1

        expected_entries = build_expected_entries(
            [
                "check-phase3-zeta.py",
                "check-phase3-alpha.py",
                "check-phase3-zeta.py",
            ],
            tmp_dir,
        )
        assert [entry.check_script.name for entry in expected_entries] == [
            "check-phase3-alpha.py",
            "check-phase3-zeta.py",
        ]
        case_count += 1

        invalid_names = (
            "../check-phase3-outside.py",
            "support.py",
            "/tmp/check-phase3-absolute.py",
        )
        for invalid_name in invalid_names:
            try:
                build_expected_entries([invalid_name], tmp_dir)
            except ValueError:
                case_count += 1
                continue
            raise AssertionError(
                f"expected invalid wrapper name to be rejected: {invalid_name}"
            )

        outside_wrapper = tmp_dir.parent / "check-phase3-outside.py"
        try:
            sync_wrappers(
                [SimpleNamespace(check_script=outside_wrapper)],
                expected,
                check=True,
                scripts_dir=tmp_dir,
            )
        except ValueError as exc:
            assert "expected wrapper path inside" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected outside wrapper path to be rejected")

        nested_wrapper = tmp_dir / "nested" / "check-phase3-nested.py"
        try:
            sync_wrappers(
                [SimpleNamespace(check_script=nested_wrapper)],
                expected,
                check=True,
                scripts_dir=tmp_dir,
            )
        except ValueError as exc:
            assert "live directly inside" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected nested wrapper path to be rejected")

    print("PHASE3_WRAPPER_SELF_TEST=pass")
    print(f"PHASE3_WRAPPER_SELF_TEST_CASE_COUNT={case_count}")
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
        help="wrapper basename to keep or recreate inside --scripts-dir",
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
    try:
        entries = build_expected_entries(args.expected_wrapper, args.scripts_dir)
        mismatches = sync_wrappers(
            entries,
            expected,
            check=args.check,
            scripts_dir=args.scripts_dir,
        )
    except ValueError as exc:
        print("PHASE3_WRAPPER_TEMPLATES=fail")
        print(str(exc))
        return 1

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
