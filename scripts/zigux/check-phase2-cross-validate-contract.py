#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
ALIGNMENT_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"

EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_ARCHIVE_SCOPE = ["x86_64-linux"]

REQUIRED_VALIDATE_MARKERS = (
    'PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py"',
    '"scripts/zigux/check-phase2-cross.py --self-test",',
    '"scripts/zigux/check-phase2-cross.py",',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '"zigux/tests/fixtures/phase2_cross_targets.json",',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-validate",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

REQUIRED_PATHS = (
    VALIDATE,
    WORKFLOW,
    MAKEFILE,
    POLICY,
    FIXTURE,
    CROSS_CHECKER,
    ALIGNMENT_CHECKER,
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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy = read_json(root / POLICY.relative_to(ROOT))
    fixture = read_json(root / FIXTURE.relative_to(ROOT))

    if not isinstance(policy, dict):
        return [("INVALID_POLICY_SHAPE", type(policy).__name__)]
    if not isinstance(fixture, dict):
        return [("INVALID_FIXTURE_SHAPE", type(fixture).__name__)]

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
        return issues

    archive_scope = upgrade_policy.get("archive_target_scope")
    if archive_scope != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_POLICY_FIELD", "archive_target_scope"))

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != EXPECTED_ARCHIVE_SCOPE:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or len(cross_targets) < 2:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    expected_targets = {
        "x86_64-linux": "archive_required",
        "aarch64-linux": "route_contract_only",
    }
    actual_targets: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(mode, str) or not mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if target in actual_targets:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        actual_targets[target] = mode

    if actual_targets != expected_targets:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_targets, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = root / path.relative_to(ROOT)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_text = read_text(root / VALIDATE.relative_to(ROOT))
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))

    issues.extend(
        collect_missing_markers(
            validate_text,
            REQUIRED_VALIDATE_MARKERS,
            "MISSING_VALIDATE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            REQUIRED_WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINES",
            "DUPLICATE_WORKFLOW_LINES",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile_text,
            REQUIRED_MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINES",
            "DUPLICATE_MAKEFILE_LINES",
        )
    )
    issues.extend(collect_fixture_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_VALIDATE_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(root / VALIDATE.relative_to(ROOT), "\n".join(REQUIRED_VALIDATE_MARKERS) + "\n")
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(root / POLICY.relative_to(ROOT), json.dumps(
        {
            "phase": "Phase 2",
            "channel": "0.17.0-dev.87+9b177a7d2",
            "minimum_version": "0.17.0-dev.87+9b177a7d2",
            "archive_sha256": {"x86_64-linux": "3" * 64},
            "upgrade_policy": {
                "channel_minimum_lockstep": True,
                "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
                "required_make_routes": ["phase2-toolchain", "phase2-validate"],
            },
        },
        indent=2,
    ) + "\n")
    write_text(root / FIXTURE.relative_to(ROOT), json.dumps(
        {
            "phase": "Phase 2",
            "status": "active",
            "route": EXPECTED_ROUTE,
            "archive_target_scope": EXPECTED_ARCHIVE_SCOPE,
            "cross_targets": [
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
            ],
        },
        indent=2,
    ) + "\n")
    write_text(root / CROSS_CHECKER.relative_to(ROOT), "present\n")
    write_text(root / ALIGNMENT_CHECKER.relative_to(ROOT), "present\n")


def remove_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


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
    expected_case_count = (
        1
        + len(REQUIRED_VALIDATE_MARKERS)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + 7
        + len(REQUIRED_PATHS)
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_validate_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in REQUIRED_VALIDATE_MARKERS:
            build_self_test_root(root)
            path = root / VALIDATE.relative_to(ROOT)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_VALIDATE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            write_text(path, replace_exact_line(read_text(path), marker, "run: python3 scripts/zigux/other.py"))
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE.relative_to(ROOT)
            write_text(path, replace_exact_line(read_text(path), marker, "# removed"))
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = root / MAKEFILE.relative_to(ROOT)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = root / POLICY.relative_to(ROOT)
        payload = json.loads(read_text(path))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXTURE.relative_to(ROOT)
        payload = json.loads(read_text(path))
        payload["route"] = "make -C zigux phase2"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_FIXTURE_FIELD", "route") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXTURE.relative_to(ROOT)
        payload = json.loads(read_text(path))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXTURE.relative_to(ROOT)
        payload = json.loads(read_text(path))
        payload["cross_targets"].append(payload["cross_targets"][0].copy())
        write_text(path, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXTURE.relative_to(ROOT)
        payload = json.loads(read_text(path))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-validate"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXTURE.relative_to(ROOT)
        write_text(path, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid fixture json did not abort")

        build_self_test_root(root)
        path = root / POLICY.relative_to(ROOT)
        write_text(path, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy json did not abort")

        for path in REQUIRED_PATHS:
            build_self_test_root(root)
            target = root / path.relative_to(ROOT)
            target.unlink()
            if path in (POLICY, FIXTURE, VALIDATE, WORKFLOW, MAKEFILE):
                try:
                    collect_issues(root)
                except SystemExit as exc:
                    assert "required file missing" in str(exc)
                else:
                    raise AssertionError(f"missing file did not abort: {path}")
            else:
                assert ("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()) in collect_issues(root)
            checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 validate/workflow cross-route contract aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_VALIDATE_CONTRACT=pass")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_VALIDATE_MARKER_COUNT={len(REQUIRED_VALIDATE_MARKERS)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_MAKEFILE_LINE_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_CROSS_VALIDATE_CONTRACT_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
