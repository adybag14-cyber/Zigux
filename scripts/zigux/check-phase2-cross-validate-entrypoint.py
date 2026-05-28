#!/usr/bin/env python3
"""Guard the current Phase 2 cross packet at the validator entrypoint."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

VALIDATOR_REQUIRED_PATH_LINES = (
    '"scripts/zigux/check-phase2-cross.py",',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
    'TOOLCHAIN_POLICY,',
    "MAKEFILE,",
)

VALIDATOR_REQUIRED_WORKFLOW_LINES = (
    '"run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross.py",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '"run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '"run: make -C zigux phase2-cross",',
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

ROUTE = "phase2-cross"
FIXTURE_ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_SELF_TEST_CASE_COUNT = 12


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


def load_required_make_routes(root: Path) -> tuple[str, ...]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    normalized: list[str] = []
    seen: set[str] = set()
    for entry in routes:
        if not isinstance(entry, str) or not entry.strip():
            raise SystemExit(
                f"invalid required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        route = entry.strip()
        if route in seen:
            raise SystemExit(
                f"duplicate required_make_routes entry in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
            )
        normalized.append(route)
        seen.add(route)
    return tuple(normalized)


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(resolve_path(root, FIXTURE))
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", "root")]

    if payload.get("route") != FIXTURE_ROUTE:
        issues.append(("INVALID_FIXTURE_ROUTE", FIXTURE_ROUTE))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or len(cross_targets) != len(SUPPORTED_TARGETS):
        issues.append(("INVALID_FIXTURE_TARGET_COUNT", str(len(cross_targets) if isinstance(cross_targets, list) else 0)))
        return issues

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_FIXTURE_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or target not in SUPPORTED_TARGETS:
            issues.append(("INVALID_FIXTURE_TARGET", str(target)))
            continue
        if route != FIXTURE_ROUTE:
            issues.append(("INVALID_FIXTURE_TARGET_ROUTE", target))
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_FIXTURE_TARGET_MODE", target))
            continue
        actual_modes[target] = validation_mode

    expected_modes = {
        "x86_64-linux": "archive_required",
        "aarch64-linux": "route_contract_only",
    }
    if actual_modes != expected_modes:
        issues.append(("INVALID_FIXTURE_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validator_text = read_text(resolve_path(root, VALIDATOR))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    required_make_routes = load_required_make_routes(root)

    for marker in VALIDATOR_REQUIRED_PATH_LINES:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_PATH_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_PATH_LINE", f"{marker}:count={count}"))

    for marker in VALIDATOR_REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_WORKFLOW_LINE", f"{marker}:count={count}"))

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

    route_count = required_make_routes.count(ROUTE)
    if route_count == 0:
        issues.append(("MISSING_REQUIRED_MAKE_ROUTE", ROUTE))
    elif route_count != 1:
        issues.append(("DUPLICATE_REQUIRED_MAKE_ROUTE", f"{ROUTE}:count={route_count}"))

    issues.extend(collect_fixture_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_ENTRYPOINT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, VALIDATOR),
        "\n".join(
            (
                "REQUIRED_PATHS = (",
                *[f"    {line}" for line in VALIDATOR_REQUIRED_PATH_LINES],
                ")",
                "REQUIRED_WORKFLOW_LINES = (",
                *[f"    {line}" for line in VALIDATOR_REQUIRED_WORKFLOW_LINES],
                ")",
            )
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(WORKFLOW_LINES) + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(MAKEFILE_LINES) + "\n",
    )
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
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ],
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
                "route": FIXTURE_ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": FIXTURE_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": FIXTURE_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_entrypoint_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validator_path = resolve_path(root, VALIDATOR)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            replace_exact_line(validator_text, VALIDATOR_REQUIRED_PATH_LINES[0], "    # removed"),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_PATH_LINE", VALIDATOR_REQUIRED_PATH_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            duplicate_exact_line(validator_text, VALIDATOR_REQUIRED_PATH_LINES[1]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_VALIDATOR_PATH_LINE",
            f"{VALIDATOR_REQUIRED_PATH_LINES[1]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_text = validator_path.read_text(encoding="utf-8")
        validator_path.write_text(
            replace_exact_line(validator_text, VALIDATOR_REQUIRED_WORKFLOW_LINES[0], "    # removed"),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_WORKFLOW_LINE", VALIDATOR_REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            replace_exact_line(workflow_text, WORKFLOW_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_text = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(duplicate_exact_line(workflow_text, WORKFLOW_LINES[1]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[1]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            replace_exact_line(makefile_text, MAKEFILE_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_text = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(duplicate_exact_line(makefile_text, MAKEFILE_LINES[2]), encoding="utf-8")
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[2]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"].remove(ROUTE)
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_REQUIRED_MAKE_ROUTE", ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"].append(ROUTE)
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate required_make_routes entry" in str(exc)
        else:
            raise AssertionError("duplicate required_make_routes did not fail closed")
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["route"] = "make -C zigux phase2-tools"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_ROUTE", FIXTURE_ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = fixture["cross_targets"][:1]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_TARGET_COUNT", "1") in collect_issues(root)
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise AssertionError(
            f"expected {EXPECTED_SELF_TEST_CASE_COUNT} self-test cases, got {checks_run}"
        )
    print("PHASE2_CROSS_VALIDATE_ENTRYPOINT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    payload = read_json(resolve_path(args.root.resolve(), FIXTURE))
    assert isinstance(payload, dict)
    cross_targets = payload["cross_targets"]
    assert isinstance(cross_targets, list)
    print("PHASE2_CROSS_VALIDATE_ENTRYPOINT=pass")
    print(f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_VALIDATOR_PATH_COUNT={len(VALIDATOR_REQUIRED_PATH_LINES)}")
    print(
        f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_VALIDATOR_WORKFLOW_LINE_COUNT={len(VALIDATOR_REQUIRED_WORKFLOW_LINES)}"
    )
    print(f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_ENTRYPOINT_TARGET_COUNT={len(cross_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
