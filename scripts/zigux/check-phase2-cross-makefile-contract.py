#!/usr/bin/env python3
"""Guard the Phase 2 cross Makefile packet against current companion surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

MAKEFILE_VALIDATE_DEPENDENCY = "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep"
MAKEFILE_AGGREGATE_ROUTE = "phase2: phase2-validate"

WORKFLOW_LINES = (
    "- name: Self-test current Phase 2 cross checker",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "- name: Check current Phase 2 direct cross-route packet",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "- name: Self-test current Phase 2 cross selftest alignment checker",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "- name: Check current Phase 2 cross alignment packet",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "- name: Run current Phase 2 cross make route",
    f"run: {ROUTE}",
)

VALIDATE_MARKERS = (
    '    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",',
    '    "scripts/zigux/check-phase2-cross.py",',
    '    "scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '    "zigux/tests/fixtures/phase2_cross_targets.json",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def load_policy_contract(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    normalized_scope: list[str] = []
    seen_scope: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
        target = value.strip()
        if target in seen_scope:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
        normalized_scope.append(target)
        seen_scope.add(target)
    return {"required_make_routes": tuple(required_make_routes), "archive_target_scope": normalized_scope}


def collect_fixture_issues(root: Path, expected_scope: list[str]) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, FIXTURE))
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_ROUTE", str(payload.get("route"))))
    if payload.get("archive_target_scope") != expected_scope:
        issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE", json.dumps(payload.get("archive_target_scope"))))
    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues
    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_FIXTURE_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or target not in SUPPORTED_TARGETS:
            issues.append(("INVALID_FIXTURE_TARGET", str(target)))
            continue
        if route != ROUTE:
            issues.append(("INVALID_FIXTURE_TARGET_ROUTE", target))
        if target in actual_modes:
            issues.append(("DUPLICATE_FIXTURE_TARGET", target))
        if not isinstance(mode, str):
            issues.append(("INVALID_FIXTURE_MODE", target))
            continue
        actual_modes[target] = mode
    expected_modes = {target: ("archive_required" if target in expected_scope else "route_contract_only") for target in SUPPORTED_TARGETS}
    if actual_modes != expected_modes:
        issues.append(("INVALID_FIXTURE_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    validate_text = read_text(resolve_path(root, VALIDATE))
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE"))
    issues.extend(collect_exact_line_issues(workflow_text, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE"))
    for marker in (MAKEFILE_VALIDATE_DEPENDENCY, MAKEFILE_AGGREGATE_ROUTE):
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_DEPENDENCY", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_DEPENDENCY", f"{marker}:count={count}"))
    for marker in VALIDATE_MARKERS:
        if marker not in validate_text:
            issues.append(("MISSING_VALIDATE_MARKER", marker))
    policy_contract = load_policy_contract(root)
    issues.extend(collect_fixture_issues(root, policy_contract["archive_target_scope"]))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_MAKEFILE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, MAKEFILE), "\n".join((*MAKEFILE_LINES, "", MAKEFILE_VALIDATE_DEPENDENCY, "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test", "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py", "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test", "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py", "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py", "", MAKEFILE_AGGREGATE_ROUTE, "")))
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, VALIDATE), "\n".join(VALIDATE_MARKERS) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_POLICY), json.dumps({"phase": "Phase 2", "channel": "0.17.0-dev.87+9b177a7d2", "minimum_version": "0.17.0-dev.87+9b177a7d2", "archive_sha256": {"x86_64-linux": "3" * 64}, "upgrade_policy": {"channel_minimum_lockstep": True, "archive_target_scope": ["x86_64-linux"], "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES)}}, indent=2) + "\n")
    write_text(resolve_path(root, FIXTURE), json.dumps({"phase": "Phase 2", "status": "active", "route": ROUTE, "archive_target_scope": ["x86_64-linux"], "cross_targets": [{"target": "x86_64-linux", "review_status": "pinned bootstrap archive", "validation_mode": "archive_required", "route": ROUTE}, {"target": "aarch64-linux", "review_status": "route contract only", "validation_mode": "route_contract_only", "route": ROUTE}]}, indent=2) + "\n")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_makefile_contract_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1
        path = resolve_path(root, MAKEFILE)
        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1
        build_sample_root(root)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), MAKEFILE_VALIDATE_DEPENDENCY, "phase2-validate: phase2-toolchain phase2-tools"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_DEPENDENCY", MAKEFILE_VALIDATE_DEPENDENCY) in collect_issues(root)
        checks_run += 1
        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[-1], "run: make -C zigux phase2-toolchain"), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[-1]) in collect_issues(root)
        checks_run += 1
        build_sample_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-tools", "phase2-kconfig", "phase2-cross", "phase2-genksyms", "phase2-fixdep"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
        else:
            raise AssertionError("expected invalid required_make_routes failure")
        checks_run += 1
        build_sample_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["route"] = "make -C zigux phase2-kconfig"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1
        validate_path = resolve_path(root, VALIDATE)
        for marker in VALIDATE_MARKERS:
            build_sample_root(root)
            validate_text = validate_path.read_text(encoding="utf-8")
            validate_path.write_text(validate_text.replace(marker, "# removed", 1), encoding="utf-8")
            assert ("MISSING_VALIDATE_MARKER", marker) in collect_issues(root)
            checks_run += 1
        build_sample_root(root)
        workflow_path.write_text(duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1
    print("PHASE2_CROSS_MAKEFILE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_MAKEFILE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="write a sample repo root and exit")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    policy_contract = load_policy_contract(args.root)
    print("PHASE2_CROSS_MAKEFILE_CONTRACT=pass")
    print(f"PHASE2_CROSS_MAKEFILE_CONTRACT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES) + 2}")
    print(f"PHASE2_CROSS_MAKEFILE_CONTRACT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_MAKEFILE_CONTRACT_REQUIRED_ROUTE_COUNT={len(policy_contract['required_make_routes'])}")
    print(f"PHASE2_CROSS_MAKEFILE_CONTRACT_TARGET_COUNT={len(SUPPORTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
