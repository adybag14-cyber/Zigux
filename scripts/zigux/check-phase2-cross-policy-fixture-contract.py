#!/usr/bin/env python3
"""Guard the bounded Lane 21 policy/fixture contract for Phase 2 cross targets."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_REQUIRED_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"required file missing: {path}")
    if not path.is_file():
        raise SystemExit(f"required path is not a file: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read required file: {path}: {exc}") from exc


def load_json(path: Path) -> object:
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


def is_strict_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def load_policy_scope(root: Path) -> tuple[list[str], list[str]]:
    policy_path = resolve_path(root, POLICY)
    payload = load_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {policy_path}")

    if payload.get("phase") != EXPECTED_PHASE:
        raise SystemExit(f"invalid phase in required file: {policy_path}")

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")

    normalized_scope: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not is_strict_non_empty_string(value):
            raise SystemExit(f"invalid archive_target_scope entry in required file: {policy_path}")
        if value in seen_targets:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}: {value}")
        seen_targets.add(value)
        normalized_scope.append(value)

    archive_sha_targets = sorted(archive_sha256.keys())
    if sorted(normalized_scope) != archive_sha_targets:
        raise SystemExit(
            "archive_sha256 keys drift from archive_target_scope in required file: "
            f"{policy_path}: scope={normalized_scope!r}:sha_keys={archive_sha_targets!r}"
        )

    return normalized_scope, archive_sha_targets


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy_scope, archive_sha_targets = load_policy_scope(root)

    fixture_path = resolve_path(root, FIXTURE)
    payload = load_json(fixture_path)
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    fixture_scope = payload.get("archive_target_scope")
    if fixture_scope != policy_scope:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", f"policy={policy_scope!r}:fixture={fixture_scope!r}"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    target_order: list[str] = []
    seen_targets: set[str] = set()
    archive_required_targets: list[str] = []
    route_contract_targets: list[str] = []

    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not is_strict_non_empty_string(target):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        seen_targets.add(target)
        target_order.append(target)

        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not is_strict_non_empty_string(review_status):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if validation_mode == "archive_required":
            archive_required_targets.append(target)
        else:
            route_contract_targets.append(target)

    if target_order != list(EXPECTED_TARGET_ORDER):
        issues.append(("TARGET_ORDER_MISMATCH", f"expected={list(EXPECTED_TARGET_ORDER)!r}:actual={target_order!r}"))

    if archive_required_targets != policy_scope:
        issues.append(
            ("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", f"policy={policy_scope!r}:archive_required={archive_required_targets!r}")
        )

    expected_route_contract_targets = [target for target in EXPECTED_TARGET_ORDER if target not in policy_scope]
    if route_contract_targets != expected_route_contract_targets:
        issues.append(
            (
                "ROUTE_CONTRACT_TARGET_SET_MISMATCH",
                f"expected={expected_route_contract_targets!r}:actual={route_contract_targets!r}",
            )
        )

    if archive_sha_targets != sorted(policy_scope):
        issues.append(("ARCHIVE_SHA_TARGET_SET_MISMATCH", f"sha={archive_sha_targets!r}:scope={policy_scope!r}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT=fail")
    for code, value in issues:
        print(f"{code}={value}")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_ROUTES),
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
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
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


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_policy_fixture_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert any(code == "ARCHIVE_SCOPE_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = [fixture["cross_targets"][1], fixture["cross_targets"][0]]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert any(code == "TARGET_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["archive_sha256"] = {"aarch64-linux": "4" * 64}
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "archive_sha256 keys drift from archive_target_scope" in str(exc)
        else:
            raise AssertionError("expected archive_sha256 drift to fail closed")
        checks_run += 1

        build_self_test_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
        else:
            raise AssertionError("expected required_make_routes drift to fail closed")
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH" for code, _ in issues)
        assert any(code == "ROUTE_CONTRACT_TARGET_SET_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        policy_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("expected missing policy file to fail closed")
        checks_run += 1

        build_self_test_root(root)
        fixture_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("expected missing fixture file to fail closed")
        checks_run += 1

    print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 21 Phase 2 cross-target policy and fixture stay aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    root = args.root.resolve()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    policy_scope, _ = load_policy_scope(root)
    fixture = load_json(resolve_path(root, FIXTURE))
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)
    print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT=pass")
    print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_TARGET_COUNT={len(cross_targets)}")
    print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_ARCHIVE_SCOPE_COUNT={len(policy_scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
