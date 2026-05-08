#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace
import tempfile

from phase3_catalog import DEFAULT_PATHS, discover_phase3_slices
from phase3_check_lib import render_wrapper_stub


ABI_WRAPPER_STUB = "\n".join(
    [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        "import subprocess",
        "import sys",
        "from pathlib import Path",
        "",
        "from phase3_check_lib import run_from_wrapper",
        "",
        "",
        "ROOT = Path(__file__).resolve().parents[2]",
        'SYNTAX_CHECKER = ROOT / "scripts" / "zigux" / "validate-phase3-abi-bindings-syntax.py"',
        "",
        "",
        'if __name__ == "__main__":',
        "    syntax_result = subprocess.run([sys.executable, str(SYNTAX_CHECKER)], check=False)",
        "    if syntax_result.returncode != 0:",
        "        raise SystemExit(syntax_result.returncode)",
        "    raise SystemExit(run_from_wrapper(__file__))",
        "",
    ]
)


def render_entry_wrapper(entry: object) -> str:
    if getattr(entry, "slug", None) == "abi":
        return ABI_WRAPPER_STUB
    return render_wrapper_stub()


def is_generated_wrapper_script(path: Path, expected_variants: tuple[str, ...]) -> bool:
    try:
        current = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    if current in expected_variants:
        return True
    return (
        "from phase3_check_lib import run_from_wrapper" in current
        and "run_from_wrapper(__file__)" in current
    )


def discover_wrapper_scripts(scripts_dir: Path, expected_variants: tuple[str, ...]) -> list[Path]:
    return [
        path
        for path in sorted(scripts_dir.glob("check-phase3-*.py"))
        if is_generated_wrapper_script(path, expected_variants)
    ]


def sync_wrappers(entries: list[object], check: bool, scripts_dir: Path = DEFAULT_PATHS.scripts_dir) -> list[str]:
    mismatches: list[str] = []
    expected_by_path = {entry.check_script: render_entry_wrapper(entry) for entry in entries}
    expected_paths = set(expected_by_path)
    expected_variants = tuple(sorted(set(expected_by_path.values())))

    for entry in entries:
        path = entry.check_script
        expected = expected_by_path[path]
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

    for path in discover_wrapper_scripts(scripts_dir, expected_variants):
        if path in expected_paths:
            continue
        mismatches.append(path.as_posix())
        if not check:
            path.unlink()

    return mismatches


def run_self_test() -> int:
    expected = render_wrapper_stub()
    abi_expected = ABI_WRAPPER_STUB
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
        expected_wrapper = tmp_dir / "check-phase3-alpha.py"
        abi_wrapper = tmp_dir / "check-phase3-abi.py"
        missing_wrapper = tmp_dir / "check-phase3-missing.py"
        stale_wrapper = tmp_dir / "check-phase3-alpha.py"
        stale_wrapper.write_text(stale, encoding="utf-8", newline="\n")
        abi_wrapper.write_text(expected, encoding="utf-8", newline="\n")
        obsolete_wrapper = tmp_dir / "check-phase3-stale.py"
        obsolete_wrapper.write_text(expected, encoding="utf-8", newline="\n")
        obsolete_shared_runner_wrapper = tmp_dir / "check-phase3-shared-runner.py"
        obsolete_shared_runner_wrapper.write_text(shared_runner_wrapper, encoding="utf-8", newline="\n")
        support_checker = tmp_dir / "check-phase3-support.py"
        support_checker.write_text("# support\n", encoding="utf-8", newline="\n")

        entries = [
            SimpleNamespace(slug="alpha", check_script=expected_wrapper),
            SimpleNamespace(slug="abi", check_script=abi_wrapper),
            SimpleNamespace(slug="missing", check_script=missing_wrapper),
        ]

        mismatches = sync_wrappers(entries, check=True, scripts_dir=tmp_dir)
        assert mismatches == [
            stale_wrapper.as_posix(),
            abi_wrapper.as_posix(),
            missing_wrapper.as_posix(),
            obsolete_shared_runner_wrapper.as_posix(),
            obsolete_wrapper.as_posix(),
        ]
        assert not missing_wrapper.exists()
        assert stale_wrapper.read_text(encoding="utf-8") == stale
        assert abi_wrapper.read_text(encoding="utf-8") == expected
        assert obsolete_shared_runner_wrapper.exists()
        assert obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, check=False, scripts_dir=tmp_dir)
        assert mismatches == [
            stale_wrapper.as_posix(),
            abi_wrapper.as_posix(),
            missing_wrapper.as_posix(),
            obsolete_shared_runner_wrapper.as_posix(),
            obsolete_wrapper.as_posix(),
        ]
        assert missing_wrapper.read_text(encoding="utf-8") == expected
        assert stale_wrapper.read_text(encoding="utf-8") == expected
        assert abi_wrapper.read_text(encoding="utf-8") == abi_expected
        assert not obsolete_shared_runner_wrapper.exists()
        assert not obsolete_wrapper.exists()
        assert support_checker.exists()

        mismatches = sync_wrappers(entries, check=True, scripts_dir=tmp_dir)
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

    mismatches = sync_wrappers(discover_phase3_slices(), check=args.check)

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
