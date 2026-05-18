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
SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
)
CHECKER_OUTPUT_MARKERS = (
    'print("PHASE2_CROSS_REPLAY_MODE=single-target")',
    'print(f"PHASE2_CROSS_TARGET={target}")',
    'print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")',
    "print(f\"PHASE2_CROSS_TARGETS={','.join(targets)}\")",
    'print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")',
    'print(f"PHASE2_CROSS_MATRIX_ENTRY_COUNT={len(matrix_entries)}")',
    'print("PHASE2_CROSS_MATRIX_ENTRIES=" + ",".join(matrix_entries))',
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "repeated authenticated reads on current `master` still return missing for",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "historical packet members",
)

TESTS_README_MARKERS = (
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster",
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`",
    "keep the pinned `x86_64-linux` bootstrap archive note",
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
    "\"the current directly readable Phase 2 packet is the scripts-root kbuild, cross-selftest, docs-shared-reminder, required-make-route, and toolchain reminder set plus the live kconfig bridge helpers, the restored closure-side note and validator entrypoint, the shipped `zigux/Makefile` wrappers, and their fixture roster\",",
    "\"repeated authenticated reads on current `master` still return missing for `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/install-zig.py`, `python3 scripts/zigux/install-zig.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py --self-test`, `python3 scripts/zigux/check-phase2-cross.py`, and `zigux/tests/fixtures/phase2_cross_targets.json`\",",
    "\"`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`\",",
    "\"`python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`\",",
    "\"`make -C zigux phase2-cross`\",",
)

EXPECTED_SELF_TEST_CASE_COUNT = 59


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    surface_paths = {path: resolve_path(root, path) for path in SURFACE_PATHS}
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
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
        collect_exact_line_issues(
            read_text(resolve_path(root, KBUILD_ROUTES)),
            KBUILD_ROUTE_MARKERS,
            "MISSING_KBUILD_ROUTE_MARKERS",
            "DUPLICATE_KBUILD_ROUTE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, TOOLCHAIN_PINNING)),
            TOOLCHAIN_PINNING_MARKERS,
            "MISSING_TOOLCHAIN_PINNING_MARKERS",
            "DUPLICATE_TOOLCHAIN_PINNING_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, TESTS_ALIGNMENT)),
            TESTS_ALIGNMENT_MARKERS,
            "MISSING_TESTS_ALIGNMENT_MARKERS",
            "DUPLICATE_TESTS_ALIGNMENT_MARKERS",
        )
    )
    for path in SURFACE_PATHS:
        if not surface_paths[path].exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))
    if surface_paths[SURFACE_PATHS[0]].exists():
        issues.extend(
            collect_exact_line_issues(
                read_text(surface_paths[SURFACE_PATHS[0]]),
                CHECKER_OUTPUT_MARKERS,
                "MISSING_CHECKER_OUTPUT_MARKERS",
                "DUPLICATE_CHECKER_OUTPUT_MARKERS",
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
    write_text(resolve_path(root, SURFACE_PATHS[0]), "\n".join(CHECKER_OUTPUT_MARKERS) + "\n")
    write_text(resolve_path(root, SURFACE_PATHS[1]), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_all(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        presence_cases = (
            (SCRIPTS_README, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"),
            (TESTS_README, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"),
        )

        for path, markers, code in presence_cases:
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    replace_all(resolved.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                assert (code, marker) in issues
                checks_run += 1

        exact_line_cases = (
            (KBUILD_ROUTES, KBUILD_ROUTE_MARKERS, "MISSING_KBUILD_ROUTE_MARKERS", "DUPLICATE_KBUILD_ROUTE_MARKERS"),
            (TOOLCHAIN_PINNING, TOOLCHAIN_PINNING_MARKERS, "MISSING_TOOLCHAIN_PINNING_MARKERS", "DUPLICATE_TOOLCHAIN_PINNING_MARKERS"),
            (TESTS_ALIGNMENT, TESTS_ALIGNMENT_MARKERS, "MISSING_TESTS_ALIGNMENT_MARKERS", "DUPLICATE_TESTS_ALIGNMENT_MARKERS"),
            (SURFACE_PATHS[0], CHECKER_OUTPUT_MARKERS, "MISSING_CHECKER_OUTPUT_MARKERS", "DUPLICATE_CHECKER_OUTPUT_MARKERS"),
        )

        for path, markers, missing_code, duplicate_code in exact_line_cases:
            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    replace_exact_line(resolved.read_text(encoding="utf-8"), marker, "# removed for self-test"),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                assert (missing_code, marker) in issues
                checks_run += 1

            for marker in markers:
                build_self_test_root(root)
                resolved = resolve_path(root, path)
                resolved.write_text(
                    duplicate_exact_line(resolved.read_text(encoding="utf-8"), marker),
                    encoding="utf-8",
                )
                issues = collect_issues(root)
                assert (duplicate_code, f"{marker}:count=2") in issues
                checks_run += 1

        for path, _, _ in presence_cases:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

        for path, _, _, _ in exact_line_cases:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            if path == SURFACE_PATHS[0]:
                issues = collect_issues(root)
                assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in issues
                checks_run += 1
                continue
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

        for path in SURFACE_PATHS:
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current directly readable Phase 2 cross reminder packet and starter surfaces aligned."
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
        f"{len(SCRIPTS_README_MARKERS) + len(TESTS_README_MARKERS) + len(KBUILD_ROUTE_MARKERS) + len(TOOLCHAIN_PINNING_MARKERS) + len(TESTS_ALIGNMENT_MARKERS) + len(CHECKER_OUTPUT_MARKERS)}"
    )
    print(f"PHASE2_CROSS_ALIGNMENT_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
