#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = (
    ROOT / "scripts" / "zigux" / "check-phase2-cross-direct-tool-manifest-validator-support-surfaces.py"
)

REQUIRED_SOURCE_MARKERS = (
    'SHARED_SURFACE = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"',
    'SHARED_SURFACE_ALIGNMENT = (',
    'VALIDATOR_ORDER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-validator-order.py"',
    'VALIDATOR_ORDER_ALIGNMENT = (',
    "DIRECT_VALIDATOR_SOURCE_MARKERS = (",
    "SHARED_SURFACE_REQUIRED_MARKERS = (",
    "VALIDATOR_ORDER_REQUIRED_MARKERS = (",
    'collect_marker_issues(',
    'print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES=pass")',
    'print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELF_TEST=pass")',
)

REQUIRED_CASE_MARKERS = (
    'path.write_text(path.read_text(encoding="utf-8").replace(SHARED_SURFACE_REQUIRED_MARKERS[0], "", 1), encoding="utf-8")',
    'path.write_text(path.read_text(encoding="utf-8") + SHARED_SURFACE_REQUIRED_MARKERS[0] + "\\n", encoding="utf-8")',
    'path.write_text(path.read_text(encoding="utf-8").replace(VALIDATOR_ORDER_REQUIRED_MARKERS[0], "", 1), encoding="utf-8")',
    'resolve_path(root, SHARED_SURFACE_ALIGNMENT).unlink()',
    'path.write_text(path.read_text(encoding="utf-8").replace(DIRECT_VALIDATOR_SOURCE_MARKERS[0], "", 1), encoding="utf-8")',
    'path.write_text(path.read_text(encoding="utf-8") + DIRECT_VALIDATOR_SOURCE_MARKERS[0] + "\\n", encoding="utf-8")',
    'resolve_path(root, VALIDATOR_ORDER).unlink()',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    checker_text = read_text(resolve_path(root, CHECKER))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SOURCE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_SOURCE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SOURCE_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_CASE_MARKERS:
        count = count_occurrences(checker_text, marker)
        if count == 0:
            issues.append(("MISSING_CASE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CASE_MARKER", f"{marker}:count={count}"))

    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(
                "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_ISSUE="
                f"{code}:{detail}"
            )
        print(
            "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_ISSUE_COUNT="
            f"{len(issues)}"
        )
        return 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT="
        f"{len(REQUIRED_SOURCE_MARKERS)}"
    )
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT="
        f"{len(REQUIRED_CASE_MARKERS)}"
    )
    return 0


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, CHECKER), "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")))


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_direct_tool_manifest_validator_support_surfaces_alignment_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert run_check(root) == 0
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert run_check(root) == 1
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert run_check(root) == 1
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT="
        f"{checks}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 direct tool-manifest validator support-surfaces checker "
            "self-test markers intact."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
