#!/usr/bin/env python3
"""Keep the Lane 21 cross validate-contract checker's self-test surface intact."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-validate-contract.py"

REQUIRED_SOURCE_MARKERS = (
    '"""Guard the Phase 2 cross packet inside the shared validator contract."""',
    'VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"',
    'WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"',
    'MAKEFILE = ROOT / "zigux" / "Makefile"',
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'DIRECT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
    'ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
    'FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"',
    'EXPECTED_ROUTE_NAME = "phase2-cross"',
    'EXPECTED_ROUTE = "make -C zigux phase2-cross"',
    'EXPECTED_DIRECT_CHECKER_ROUTE_LINE = \'ROUTE = "make -C zigux phase2-cross"\'',
    '"run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross.py",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '"run: make -C zigux phase2-cross",',
    '"phase2-cross:",',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",',
    '"scripts/zigux/check-phase2-cross.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
    '"x86_64-linux": "archive_required",',
    '"aarch64-linux": "route contract only",',
    'expected_case_count = 15',
    'print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST=pass")',
    'print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")',
    'print("PHASE2_CROSS_VALIDATE_CONTRACT=pass")',
    'print(f"PHASE2_CROSS_VALIDATE_CONTRACT_WORKFLOW_LINE_COUNT={len(EXPECTED_VALIDATOR_WORKFLOW_LINES)}")',
    'print(f"PHASE2_CROSS_VALIDATE_CONTRACT_REQUIRED_PATH_COUNT={len(EXPECTED_VALIDATOR_PATHS)}")',
)

REQUIRED_CASE_MARKERS = (
    'assert ("MISSING_LIVE_WORKFLOW_LINE", EXPECTED_VALIDATOR_WORKFLOW_LINES[4]) in collect_issues(root)',
    'assert ("MISSING_VALIDATOR_WORKFLOW_LINE", EXPECTED_VALIDATOR_WORKFLOW_LINES[4]) in collect_issues(root)',
    'assert ("MISSING_LIVE_MAKEFILE_LINE", EXPECTED_VALIDATOR_MAKEFILE_LINES[0]) in collect_issues(root)',
    'assert ("MISSING_VALIDATOR_MAKEFILE_LINE", EXPECTED_VALIDATOR_MAKEFILE_LINES[1]) in collect_issues(root)',
    'assert ("MISSING_VALIDATOR_REQUIRED_PATH", EXPECTED_VALIDATOR_PATHS[2]) in collect_issues(root)',
    'assert ("MISSING_POLICY_ROUTE", EXPECTED_ROUTE_NAME) in collect_issues(root)',
    'assert "duplicate required_make_routes" in str(exc)',
    'policy["upgrade_policy"]["required_make_routes"].remove("phase2-cross")',
    'policy["upgrade_policy"]["required_make_routes"].append("phase2-cross")',
    'assert ("MISSING_DIRECT_CHECKER_ROUTE", EXPECTED_ROUTE) in collect_issues(root)',
    'assert ("INVALID_FIXTURE_ROUTE", EXPECTED_ROUTE) in collect_issues(root)',
    'assert ("INVALID_FIXTURE_TARGET_MODE", "aarch64-linux:route_contract_only") in collect_issues(root)',
    'alignment_path.unlink()',
    'duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), EXPECTED_VALIDATOR_WORKFLOW_LINES[0])',
    'raise AssertionError("missing validator did not abort")',
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    checker_text = read_text(resolve_path(root, CHECKER))
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SOURCE_MARKERS:
        count = checker_text.count(marker)
        if count == 0:
            issues.append(("MISSING_SOURCE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SOURCE_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_CASE_MARKERS:
        count = checker_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CASE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CASE_MARKER", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, CHECKER), "\n".join((*REQUIRED_SOURCE_MARKERS, *REQUIRED_CASE_MARKERS, "")))


def run_self_test() -> int:
    expected_case_count = 1 + len(REQUIRED_SOURCE_MARKERS) + len(REQUIRED_CASE_MARKERS) + 1 + 1
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_contract_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_SOURCE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_SOURCE_MARKER", marker) in collect_issues(root)
            checks += 1

        for marker in REQUIRED_CASE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, CHECKER)
            path.write_text(path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_CASE_MARKER", marker) in collect_issues(root)
            checks += 1

        build_self_test_root(root)
        path = resolve_path(root, CHECKER)
        path.write_text(path.read_text(encoding="utf-8") + REQUIRED_SOURCE_MARKERS[0] + "\n", encoding="utf-8")
        assert (
            "DUPLICATE_SOURCE_MARKER",
            f"{REQUIRED_SOURCE_MARKERS[0]}:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        resolve_path(root, CHECKER).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing target checker did not abort")

    assert checks == expected_case_count
    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 cross validate-contract checker's self-test surface intact."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT_SOURCE_MARKER_COUNT={len(REQUIRED_SOURCE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELFTEST_ALIGNMENT_CASE_MARKER_COUNT={len(REQUIRED_CASE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
