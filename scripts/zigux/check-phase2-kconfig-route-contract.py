#!/usr/bin/env python3

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_PHASE2 = ROOT / "scripts" / "zigux" / "validate-phase2.py"
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

VALIDATE_REQUIRED_LINES = (
    'KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-route-contract.py"',
    '    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-route-contract.py",',
    '    [sys.executable, str(KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER), "--self-test"],',
    '    [sys.executable, str(KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER)],',
)

MAKEFILE_KCONFIG_ROUTE_LINES = (
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test',
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py',
    '\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig',
)

WORKFLOW_KCONFIG_ROUTE_LINES = (
    '  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
    '  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
    '  run: python3 scripts/zigux/check-kconfig-bridge.py --self-test',
    '  run: python3 scripts/zigux/check-kconfig-bridge.py',
    '  run: zig test scripts/zigux/kconfig/confdata_bridge.zig',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_issue(issues: list[tuple[str, str]], code: str, label: str, lines: list[str], expected: int = 1) -> None:
    actual = lines.count(label)
    if actual != expected:
        issues.append((code, f"{label}:actual={actual}:expected={expected}"))


def collect_issues(validate_phase2_text: str, makefile_text: str, workflow_text: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    validate_lines = validate_phase2_text.splitlines()
    makefile_lines = makefile_text.splitlines()
    workflow_lines = workflow_text.splitlines()

    for snippet in VALIDATE_REQUIRED_LINES:
        count_issue(issues, "VALIDATE_PHASE2_ROUTE_DRIFT", snippet, validate_lines)

    for snippet in MAKEFILE_KCONFIG_ROUTE_LINES:
        count_issue(issues, "MAKEFILE_KCONFIG_PACKET_DRIFT", snippet, makefile_lines)

    for snippet in WORKFLOW_KCONFIG_ROUTE_LINES:
        count_issue(issues, "WORKFLOW_KCONFIG_PACKET_DRIFT", snippet, workflow_lines)

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> None:
    print("PHASE2_KCONFIG_ROUTE_CONTRACT=fail")
    for code, detail in issues:
        print(f"{code}={detail}")


def build_validate_phase2_text(*, include_route_contract: bool = True) -> str:
    lines = [
        '#!/usr/bin/env python3',
        'from __future__ import annotations',
        'import argparse',
        'import subprocess',
        'import sys',
        'from pathlib import Path',
        'ROOT = Path(__file__).resolve().parents[2]',
        'KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"',
        'KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"',
    ]
    if include_route_contract:
        lines.append('KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-route-contract.py"')
    lines.extend(
        [
            'required = [',
            '    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",',
            '    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",',
        ]
    )
    if include_route_contract:
        lines.append('    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-route-contract.py",')
    lines.extend(
        [
            ']',
            'commands = [',
            '    [sys.executable, str(KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_CHECKER), "--self-test"],',
            '    [sys.executable, str(KCONFIG_BRIDGE_SELFTEST_ALIGNMENT_CHECKER)],',
            '    [sys.executable, str(KCONFIG_BRIDGE_CHECKER), "--self-test"],',
            '    [sys.executable, str(KCONFIG_BRIDGE_CHECKER)],',
        ]
    )
    if include_route_contract:
        lines.extend(
            [
                '    [sys.executable, str(KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER), "--self-test"],',
                '    [sys.executable, str(KCONFIG_BRIDGE_ROUTE_CONTRACT_CHECKER)],',
            ]
        )
    lines.append(']')
    return "\n".join(lines)


def build_makefile_text() -> str:
    lines = [
        'phase2-validate:',
        '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
        '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
    ]
    lines.extend(
        [
            'phase2-kconfig:',
            '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test',
            '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py',
            '\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig',
        ]
    )
    return "\n".join(lines)


def build_workflow_text() -> str:
    lines = [
        '- name: Self-test Phase 2 kconfig selftest alignment',
        '  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test',
        '- name: Check Phase 2 kconfig selftest alignment',
        '  run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py',
    ]
    lines.extend(
        [
            '- name: Self-test bounded kconfig bridge parity checker',
            '  run: python3 scripts/zigux/check-kconfig-bridge.py --self-test',
            '- name: Check bounded kconfig bridge parity',
            '  run: python3 scripts/zigux/check-kconfig-bridge.py',
            '- name: Run bounded confdata bridge unit tests',
            '  run: zig test scripts/zigux/kconfig/confdata_bridge.zig',
        ]
    )
    return "\n".join(lines)


def run_self_test() -> int:
    checks_run = 0

    healthy = collect_issues(
        build_validate_phase2_text(),
        build_makefile_text(),
        build_workflow_text(),
    )
    assert healthy == []
    checks_run += 1

    validate_missing = collect_issues(
        build_validate_phase2_text(include_route_contract=False),
        build_makefile_text(),
        build_workflow_text(),
    )
    assert any(code == "VALIDATE_PHASE2_ROUTE_DRIFT" for code, _ in validate_missing)
    checks_run += 1

    confdata_missing_make = collect_issues(
        build_validate_phase2_text(),
        build_makefile_text().replace(
            '\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig',
            '',
            1,
        ),
        build_workflow_text(),
    )
    assert any(code == "MAKEFILE_KCONFIG_PACKET_DRIFT" for code, _ in confdata_missing_make)
    checks_run += 1

    confdata_missing_workflow = collect_issues(
        build_validate_phase2_text(),
        build_makefile_text(),
        build_workflow_text().replace(
            '  run: zig test scripts/zigux/kconfig/confdata_bridge.zig',
            '',
            1,
        ),
    )
    assert any(code == "WORKFLOW_KCONFIG_PACKET_DRIFT" for code, _ in confdata_missing_workflow)
    checks_run += 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_route_contract_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        validate_path = tmp_dir / "validate-phase2.py"
        makefile_path = tmp_dir / "Makefile"
        workflow_path = tmp_dir / "zigux-bootstrap.yml"
        validate_path.write_text(build_validate_phase2_text(), encoding="utf-8")
        makefile_path.write_text(build_makefile_text(), encoding="utf-8")
        workflow_path.write_text(build_workflow_text(), encoding="utf-8")
        issues = collect_issues(
            read_text(validate_path),
            read_text(makefile_path),
            read_text(workflow_path),
        )
        assert issues == []
        checks_run += 1

    print("PHASE2_KCONFIG_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shared Phase 2 validator, Makefile, and workflow routes still carry the bounded kconfig bridge packet."
    )
    parser.add_argument("--validate-phase2", type=Path, default=VALIDATE_PHASE2, help="Override validate-phase2.py path")
    parser.add_argument("--makefile", type=Path, default=MAKEFILE, help="Override Makefile path")
    parser.add_argument("--workflow", type=Path, default=WORKFLOW, help="Override workflow path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage without repo files")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(
        read_text(args.validate_phase2),
        read_text(args.makefile),
        read_text(args.workflow),
    )
    if issues:
        emit_issues(issues)
        return 1

    print("PHASE2_KCONFIG_ROUTE_CONTRACT=pass")
    print(f"VALIDATE_PHASE2={args.validate_phase2}")
    print(f"MAKEFILE={args.makefile}")
    print(f"WORKFLOW={args.workflow}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
