#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
KBUILD_ROUTES = ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py"
TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
TESTS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "historical packet members",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
    "shared cross-selftest alignment self-test: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "shared cross-selftest alignment gate: `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
)

TESTS_README_MARKERS = (
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`make -C zigux phase2-cross`",
    "historical packet members rather than direct tests-root evidence",
)

KBUILD_ROUTE_MARKERS = (
    "\"`python3 scripts/zigux/check-phase2-cross.py --self-test`\",",
    "\"`make -C zigux phase2`\",",
    "\"historical packet members\",",
)

TOOLCHAIN_PINNING_MARKERS = (
    "\"`python3 scripts/zigux/check-phase2-cross.py --self-test`\",",
    "\"`python3 scripts/zigux/check-phase2-cross.py`\",",
    "\"`make -C zigux phase2-validate`\",",
    "\"`make -C zigux phase2`\",",
)

TESTS_ALIGNMENT_MARKERS = (
    "'`python3 scripts/zigux/check-phase2-cross.py --self-test`'",
    "'`python3 scripts/zigux/check-phase2-cross.py`'",
    "'`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`'",
    "'`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`'",
    "'`make -C zigux phase2-cross`'",
)

EXPECTED_SELF_TEST_CASE_COUNT = 32


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_README_FORBIDDEN_MARKERS,
            "FORBIDDEN_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, KBUILD_ROUTES)),
            KBUILD_ROUTE_MARKERS,
            "MISSING_KBUILD_ROUTE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TOOLCHAIN_PINNING)),
            TOOLCHAIN_PINNING_MARKERS,
            "MISSING_TOOLCHAIN_PINNING_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_ALIGNMENT)),
            TESTS_ALIGNMENT_MARKERS,
            "MISSING_TESTS_ALIGNMENT_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, KBUILD_ROUTES), "\n".join(KBUILD_ROUTE_MARKERS) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_PINNING), "\n".join(TOOLCHAIN_PINNING_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_ALIGNMENT), "\n".join(TESTS_ALIGNMENT_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        file_cases = (
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
            (KBUILD_ROUTES, KBUILD_ROUTE_MARKERS, "MISSING_KBUILD_ROUTE_MARKERS"),
            (TOOLCHAIN_PINNING, TOOLCHAIN_PINNING_MARKERS, "MISSING_TOOLCHAIN_PINNING_MARKERS"),
            (TESTS_ALIGNMENT, TESTS_ALIGNMENT_MARKERS, "MISSING_TESTS_ALIGNMENT_MARKERS"),
        )

        for path, markers, code in file_cases:
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    replace_once(resolved.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            resolved = resolve_path(root, SCRIPTS_README)
            resolved.write_text(
                resolved.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("FORBIDDEN_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for path, _, _ in file_cases:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 cross-route reminder packet aligned across the live scripts and tests surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT="
        f"{len(SCRIPTS_README_MARKERS) + len(SCRIPTS_README_FORBIDDEN_MARKERS) + len(TESTS_README_MARKERS) + len(KBUILD_ROUTE_MARKERS) + len(TOOLCHAIN_PINNING_MARKERS) + len(TESTS_ALIGNMENT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
