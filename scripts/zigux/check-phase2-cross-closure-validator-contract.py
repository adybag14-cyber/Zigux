#!/usr/bin/env python3
"""Guard the Lane 21 cross packet at the Phase 2 closure-validator surface."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
CLOSURE_NOTE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
EXPECTED_TARGETS = [
    {
        "target": "x86_64-linux",
        "review_status": "pinned bootstrap archive",
        "validation_mode": "archive_required",
        "route": EXPECTED_ROUTE,
    },
    {
        "target": "aarch64-linux",
        "review_status": "route contract only",
        "validation_mode": "route_contract_only",
        "route": EXPECTED_ROUTE,
    },
]

VALIDATOR_MARKERS = (
    'PHASE2_CROSS_TARGETS_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")',
    '"scripts/zigux/check-phase2-cross.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
    '"cross_route_support",',
)

CLOSURE_MARKERS = (
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`",
    "`PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_SELF_TEST_CASE_COUNT = 14


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    root = root.resolve()
    issues: list[tuple[str, str]] = []

    validator_text = read_text(resolve_path(root, VALIDATOR))
    closure_text = read_text(resolve_path(root, CLOSURE_NOTE))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    policy = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    fixture = read_json(resolve_path(root, FIXTURE))

    for marker in VALIDATOR_MARKERS:
        if marker not in validator_text:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))

    for marker in CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if not isinstance(policy, dict):
        return issues + [("INVALID_POLICY_SHAPE", type(policy).__name__)]
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_POLICY_FIELD", "upgrade_policy")]
    if upgrade_policy.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))
    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
        issues.append(("INVALID_POLICY_FIELD", "required_make_routes"))

    if not isinstance(fixture, dict):
        return issues + [("INVALID_FIXTURE_SHAPE", type(fixture).__name__)]
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))
    if fixture.get("cross_targets") != EXPECTED_TARGETS:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(resolve_path(root, VALIDATOR), "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(resolve_path(root, CLOSURE_NOTE), "\n".join(CLOSURE_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": EXPECTED_ROUTE,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "cross_targets": EXPECTED_TARGETS,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_closure_validator_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validator_path = resolve_path(root, VALIDATOR)
        build_sample_root(root)
        validator_path.write_text(
            replace_once(
                validator_path.read_text(encoding="utf-8"),
                VALIDATOR_MARKERS[1],
                '"scripts/zigux/check-phase2-cross-selftest-alignment.py",',
            ),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", VALIDATOR_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        closure_path = resolve_path(root, CLOSURE_NOTE)
        build_sample_root(root)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), CLOSURE_MARKERS[0], "`scripts/zigux/check-phase2-kbuild-routes.py`"),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        workflow_path = resolve_path(root, WORKFLOW)
        build_sample_root(root)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_LINES[1]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[1]}:count=2") in collect_issues(root)
        checks_run += 1

        makefile_path = resolve_path(root, MAKEFILE)
        build_sample_root(root)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_LINES[2]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[2]}:count=2") in collect_issues(root)
        checks_run += 1

        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        build_sample_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY_FIELD", "required_make_routes") in collect_issues(root)
        checks_run += 1

        fixture_path = resolve_path(root, FIXTURE)
        build_sample_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["route"] = "make -C zigux phase2-tools"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "route") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        policy_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
        else:
            raise AssertionError("invalid policy json did not abort")
        checks_run += 1

        build_sample_root(root)
        fixture_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
        else:
            raise AssertionError("invalid fixture json did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT=pass")
    print(f"PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_REQUIRED_PATH_COUNT=6")
    print(f"PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_CLOSURE_VALIDATOR_CONTRACT_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
