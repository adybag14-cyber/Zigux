#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHARED_SURFACE = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-shared-surface.py"
SHARED_SURFACE_ALIGNMENT = (
    ROOT
    / "scripts"
    / "zigux"
    / "check-phase2-cross-validate-shared-surface-selftest-alignment.py"
)
VALIDATOR_ORDER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-validator-order.py"
VALIDATOR_ORDER_ALIGNMENT = (
    ROOT
    / "scripts"
    / "zigux"
    / "check-phase2-cross-validate-validator-order-selftest-alignment.py"
)

DIRECT_VALIDATOR_SOURCE_MARKERS = (
    'check-phase2-cross-direct-tool-manifest-validator-contract.py',
    'check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py',
)

SHARED_SURFACE_REQUIRED_MARKERS = (
    'DIRECT_VALIDATOR_CHECKER = (',
    '    ROOT / "scripts" / "zigux" / "check-phase2-cross-direct-tool-manifest-validator-contract.py"',
    'DIRECT_VALIDATOR_ALIGNMENT = (',
    '    / "check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py"',
    '    DIRECT_VALIDATOR_CHECKER,',
    '    DIRECT_VALIDATOR_ALIGNMENT,',
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
)

VALIDATOR_ORDER_REQUIRED_MARKERS = (
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract.py",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py --self-test",',
    '    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-direct-tool-manifest-validator-contract-selftest-alignment.py",',
)

EXPECTED_SELF_TEST_CASE_COUNT = 9


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


def collect_marker_issues(
    root: Path,
    path: Path,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, path))
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_occurrences(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in (
        SHARED_SURFACE,
        SHARED_SURFACE_ALIGNMENT,
        VALIDATOR_ORDER,
        VALIDATOR_ORDER_ALIGNMENT,
    ):
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    if issues:
        return issues

    issues.extend(
        collect_marker_issues(
            root,
            SHARED_SURFACE,
            SHARED_SURFACE_REQUIRED_MARKERS,
            "MISSING_SHARED_SURFACE_MARKER",
            "DUPLICATE_SHARED_SURFACE_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            root,
            VALIDATOR_ORDER,
            VALIDATOR_ORDER_REQUIRED_MARKERS,
            "MISSING_VALIDATOR_ORDER_MARKER",
            "DUPLICATE_VALIDATOR_ORDER_MARKER",
        )
    )
    for path in (SHARED_SURFACE_ALIGNMENT, VALIDATOR_ORDER_ALIGNMENT):
        issues.extend(
            collect_marker_issues(
                root,
                path,
                DIRECT_VALIDATOR_SOURCE_MARKERS,
                "MISSING_ALIGNMENT_MARKER",
                "DUPLICATE_ALIGNMENT_MARKER",
            )
        )
    return issues


def run_check(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_REQUIRED_PATH_COUNT=4"
    )
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_MARKER_COUNT="
        f"{len(SHARED_SURFACE_REQUIRED_MARKERS) + len(VALIDATOR_ORDER_REQUIRED_MARKERS) + 2 * len(DIRECT_VALIDATOR_SOURCE_MARKERS)}"
    )
    return 0


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, SHARED_SURFACE), "\n".join((*SHARED_SURFACE_REQUIRED_MARKERS, "")))
    write_text(resolve_path(root, VALIDATOR_ORDER), "\n".join((*VALIDATOR_ORDER_REQUIRED_MARKERS, "")))
    alignment_body = "\n".join((*DIRECT_VALIDATOR_SOURCE_MARKERS, ""))
    write_text(resolve_path(root, SHARED_SURFACE_ALIGNMENT), alignment_body)
    write_text(resolve_path(root, VALIDATOR_ORDER_ALIGNMENT), alignment_body)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_cross_direct_tool_manifest_validator_support_surfaces_"
    ) as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert run_check(root) == 0
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, SHARED_SURFACE)
        path.write_text(path.read_text(encoding="utf-8").replace(SHARED_SURFACE_REQUIRED_MARKERS[0], "", 1), encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, SHARED_SURFACE)
        path.write_text(path.read_text(encoding="utf-8") + SHARED_SURFACE_REQUIRED_MARKERS[0] + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, VALIDATOR_ORDER)
        path.write_text(path.read_text(encoding="utf-8").replace(VALIDATOR_ORDER_REQUIRED_MARKERS[0], "", 1), encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, VALIDATOR_ORDER)
        path.write_text(path.read_text(encoding="utf-8") + VALIDATOR_ORDER_REQUIRED_MARKERS[0] + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, SHARED_SURFACE_ALIGNMENT).unlink()
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, SHARED_SURFACE_ALIGNMENT)
        path.write_text(path.read_text(encoding="utf-8").replace(DIRECT_VALIDATOR_SOURCE_MARKERS[0], "", 1), encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        path = resolve_path(root, VALIDATOR_ORDER_ALIGNMENT)
        path.write_text(path.read_text(encoding="utf-8") + DIRECT_VALIDATOR_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert run_check(root) == 1
        checks += 1

        build_sample_root(root)
        resolve_path(root, VALIDATOR_ORDER).unlink()
        assert run_check(root) == 1
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELF_TEST=pass")
    print(
        "PHASE2_CROSS_DIRECT_TOOL_MANIFEST_VALIDATOR_SUPPORT_SURFACES_SELF_TEST_CASE_COUNT="
        f"{checks}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Keep the Lane 21 shared-surface and validator-order support checkers aware "
            "of the direct tool-manifest validator-contract checker pair."
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
