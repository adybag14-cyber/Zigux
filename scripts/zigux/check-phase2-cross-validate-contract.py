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

SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
)
EXPECTED_REVIEW_STATUS_BY_TARGET = {
    "x86_64-linux": "pinned bootstrap archive",
    "aarch64-linux": "route contract only",
}

REQUIRED_VALIDATE_MARKERS = (
    '    "scripts/zigux/check-phase2-cross.py",',
    '    "scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '    "zigux/tests/fixtures/phase2_cross_targets.json",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross.py",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",',
    '    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",',
    '    "run: make -C zigux phase2-cross",',
    '    "run: make -C zigux phase2-validate",',
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
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


class DuplicateJsonKeyError(ValueError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc


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


def load_expected_policy_contract(root: Path) -> dict[str, object]:
    policy_path = resolve_path(root, POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")

    normalized_scope: list[str] = []
    seen_scope: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
        if value in seen_scope:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}")
        if value not in SUPPORTED_CROSS_TARGETS:
            raise SystemExit(f"unsupported archive_target_scope target in required file: {policy_path}: {value}")
        normalized_scope.append(value)
        seen_scope.add(value)

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {policy_path}")

    archive_sha256_targets: list[str] = []
    seen_hash_targets: set[str] = set()
    for key, value in archive_sha256.items():
        if not isinstance(key, str) or not key or key != key.strip():
            raise SystemExit(f"invalid archive_sha256 key in required file: {policy_path}")
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid archive_sha256 value in required file: {policy_path}: {key}")
        if key in seen_hash_targets:
            raise SystemExit(f"duplicate archive_sha256 key in required file: {policy_path}: {key}")
        archive_sha256_targets.append(key)
        seen_hash_targets.add(key)

    if archive_sha256_targets != normalized_scope:
        raise SystemExit(f"archive_sha256 target drift in required file: {policy_path}")

    return {
        "archive_target_scope": normalized_scope,
        "expected_modes": {
            target: ("archive_required" if target in seen_scope else "route_contract_only")
            for target in SUPPORTED_CROSS_TARGETS
        },
    }


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    expected_policy = load_expected_policy_contract(root)
    fixture_path = resolve_path(root, FIXTURE)
    fixture = read_json(fixture_path)

    if not isinstance(fixture, dict):
        return [("INVALID_FIXTURE_SHAPE", type(fixture).__name__)]

    if fixture.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != expected_policy["archive_target_scope"]:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    target_order: list[str] = []
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        review_status = entry.get("review_status")
        if not isinstance(target, str) or not target or target != target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if target not in SUPPORTED_CROSS_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))
        if not isinstance(mode, str) or not mode or mode != mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if review_status != EXPECTED_REVIEW_STATUS_BY_TARGET.get(target):
            issues.append(("INVALID_CROSS_TARGET_REVIEW_STATUS", f"{target}:{review_status}"))
        actual_modes[target] = mode
        target_order.append(target)

    if target_order != list(SUPPORTED_CROSS_TARGETS):
        issues.append(("INVALID_CROSS_TARGET_ORDER", ",".join(target_order)))
    if actual_modes != expected_policy["expected_modes"]:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_PATHS:
        resolved = resolve_path(root, path)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_PATH", path.relative_to(ROOT).as_posix()))

    validate_text = read_text(resolve_path(root, VALIDATE))
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    issues.extend(collect_missing_markers(validate_text, REQUIRED_VALIDATE_MARKERS, "MISSING_VALIDATE_MARKERS"))
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
    write_text(resolve_path(root, VALIDATE), "\n".join(REQUIRED_VALIDATE_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
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
                "archive_target_scope": ["x86_64-linux"],
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
        )
        + "\n",
    )
    write_text(resolve_path(root, CROSS_CHECKER), "present\n")
    write_text(resolve_path(root, ALIGNMENT_CHECKER), "present\n")


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
        + 8
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
            path = resolve_path(root, VALIDATE)
            write_text(path, remove_marker(read_text(path), marker))
            assert ("MISSING_VALIDATE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            write_text(path, replace_exact_line(read_text(path), marker, "run: python3 scripts/zigux/other.py"))
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, replace_exact_line(read_text(path), marker, "# removed"))
            assert ("MISSING_MAKEFILE_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            write_text(path, duplicate_exact_line(read_text(path), marker))
            assert ("DUPLICATE_MAKEFILE_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, POLICY)
        payload = json.loads(read_text(path))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(path, json.dumps(payload, indent=2) + "\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing phase2-cross required_make_routes entry did not abort")

        build_self_test_root(root)
        path = resolve_path(root, POLICY)
        payload = json.loads(read_text(path))
        payload["archive_sha256"]["aarch64-linux"] = "4" * 64
        write_text(path, json.dumps(payload, indent=2) + "\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "archive_sha256 target drift" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("archive_sha256 scope drift did not abort")

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(read_text(path))
        payload["cross_targets"][1]["review_status"] = "pinned bootstrap archive"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert (
            "INVALID_CROSS_TARGET_REVIEW_STATUS",
            "aarch64-linux:pinned bootstrap archive",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(read_text(path))
        payload["cross_targets"].reverse()
        write_text(path, json.dumps(payload, indent=2) + "\n")
        assert (
            "INVALID_CROSS_TARGET_ORDER",
            "aarch64-linux,x86_64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(read_text(path))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        write_text(path, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        payload = json.loads(read_text(path))
        payload["cross_targets"].append(payload["cross_targets"][0].copy())
        write_text(path, json.dumps(payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        write_text(path, "{\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid fixture json did not abort")

        build_self_test_root(root)
        path = resolve_path(root, POLICY)
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
            target = resolve_path(root, path)
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
