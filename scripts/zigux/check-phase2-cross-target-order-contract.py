#!/usr/bin/env python3
"""Validate canonical ordering for the Phase 2 cross-target fixture."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
CROSS_TARGETS_FIXTURE = Path("zigux/tests/fixtures/phase2_cross_targets.json")

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
ARCHIVE_MODE = "archive_required"
ROUTE_CONTRACT_MODE = "route_contract_only"
EXPECTED_SELF_TEST_CASE_COUNT = 10


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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_archive_target_scope(root: Path) -> list[str]:
    payload = read_json(root / TOOLCHAIN_POLICY)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / TOOLCHAIN_POLICY}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {root / TOOLCHAIN_POLICY}")

    normalized: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(archive_target_scope):
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope entry at index {index} in required file: {root / TOOLCHAIN_POLICY}"
            )
        target = value.strip()
        if target in seen:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {root / TOOLCHAIN_POLICY}: {target}"
            )
        normalized.append(target)
        seen.add(target)
    return normalized


def expected_target_order(
    archive_target_scope: list[str], cross_targets: list[dict[str, object]]
) -> list[str]:
    route_contract_targets = sorted(
        entry["target"]
        for entry in cross_targets
        if entry.get("validation_mode") == ROUTE_CONTRACT_MODE
        and isinstance(entry.get("target"), str)
        and entry["target"].strip()
    )
    return [*archive_target_scope, *route_contract_targets]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_target_scope = load_archive_target_scope(root)
    fixture = read_json(root / CROSS_TARGETS_FIXTURE)

    if not isinstance(fixture, dict):
        return [("INVALID_FIXTURE_SHAPE", "root")]

    if fixture.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if fixture.get("archive_target_scope") != archive_target_scope:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", ",".join(archive_target_scope)))

    raw_targets = fixture.get("cross_targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    cross_targets: list[dict[str, object]] = []
    seen_targets: set[str] = set()
    archive_mode_targets: list[str] = []
    for index, entry in enumerate(raw_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_TARGET_ENTRY", f"index={index}"))
            continue
        target = entry.get("target")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_TARGET_ENTRY", f"index={index}:target"))
            continue
        target = target.strip()
        if target in seen_targets:
            issues.append(("DUPLICATE_TARGET", target))
        seen_targets.add(target)

        mode = entry.get("validation_mode")
        if mode not in (ARCHIVE_MODE, ROUTE_CONTRACT_MODE):
            issues.append(("INVALID_TARGET_MODE", target))
        elif mode == ARCHIVE_MODE:
            archive_mode_targets.append(target)

        if entry.get("route") != EXPECTED_ROUTE:
            issues.append(("INVALID_TARGET_ROUTE", target))
        cross_targets.append(entry)

    if archive_mode_targets != archive_target_scope:
        issues.append(("ARCHIVE_TARGET_ORDER_MISMATCH", ",".join(archive_mode_targets)))

    actual_order = [
        entry.get("target", "")
        for entry in cross_targets
        if isinstance(entry.get("target"), str) and entry.get("target", "").strip()
    ]
    canonical_order = expected_target_order(archive_target_scope, cross_targets)
    if actual_order != canonical_order:
        issues.append(("TARGET_ORDER_MISMATCH", "actual=" + ",".join(actual_order)))
        issues.append(("TARGET_ORDER_EXPECTED", "expected=" + ",".join(canonical_order)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)

    print("PHASE2_CROSS_TARGET_ORDER_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_json(
        root / TOOLCHAIN_POLICY,
        {
            "phase": "Phase 2",
            "channel": "0.17.0-dev.87+9b177a7d2",
            "minimum_version": "0.17.0-dev.87+9b177a7d2",
            "archive_sha256": {"x86_64-linux": "3" * 64},
            "upgrade_policy": {
                "channel_minimum_lockstep": True,
                "archive_target_scope": ["x86_64-linux"],
                "required_make_routes": ["phase2-cross"],
            },
        },
    )
    write_json(
        root / CROSS_TARGETS_FIXTURE,
        {
            "phase": EXPECTED_PHASE,
            "status": EXPECTED_STATUS,
            "route": EXPECTED_ROUTE,
            "archive_target_scope": ["x86_64-linux"],
            "cross_targets": [
                {
                    "target": "x86_64-linux",
                    "review_status": "pinned bootstrap archive",
                    "validation_mode": ARCHIVE_MODE,
                    "route": EXPECTED_ROUTE,
                },
                {
                    "target": "aarch64-linux",
                    "review_status": "route contract only",
                    "validation_mode": ROUTE_CONTRACT_MODE,
                    "route": EXPECTED_ROUTE,
                },
            ],
        },
    )


def mutate_fixture(root: Path) -> dict[str, object]:
    path = root / CROSS_TARGETS_FIXTURE
    fixture = read_json(path)
    assert isinstance(fixture, dict)
    return fixture


def save_fixture(root: Path, fixture: dict[str, object]) -> None:
    write_json(root / CROSS_TARGETS_FIXTURE, fixture)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_target_order_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        assert isinstance(fixture["cross_targets"], list)
        fixture["cross_targets"] = list(reversed(fixture["cross_targets"]))
        save_fixture(root, fixture)
        assert (
            "TARGET_ORDER_MISMATCH",
            "actual=aarch64-linux,x86_64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        fixture["archive_target_scope"] = ["aarch64-linux"]
        save_fixture(root, fixture)
        assert ("ARCHIVE_SCOPE_MISMATCH", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        assert isinstance(fixture["cross_targets"], list)
        fixture["cross_targets"][0]["validation_mode"] = ROUTE_CONTRACT_MODE
        save_fixture(root, fixture)
        assert ("ARCHIVE_TARGET_ORDER_MISMATCH", "") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        assert isinstance(fixture["cross_targets"], list)
        fixture["cross_targets"].append(dict(fixture["cross_targets"][0]))
        save_fixture(root, fixture)
        assert ("DUPLICATE_TARGET", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        assert isinstance(fixture["cross_targets"], list)
        fixture["cross_targets"][1]["validation_mode"] = "native_smoke"
        save_fixture(root, fixture)
        assert ("INVALID_TARGET_MODE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        assert isinstance(fixture["cross_targets"], list)
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2"
        save_fixture(root, fixture)
        assert ("INVALID_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = mutate_fixture(root)
        fixture["status"] = "draft"
        save_fixture(root, fixture)
        assert ("INVALID_FIXTURE_FIELD", "status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_json(root / CROSS_TARGETS_FIXTURE, [])
        assert ("INVALID_FIXTURE_SHAPE", "root") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy = read_json(root / TOOLCHAIN_POLICY)
        assert isinstance(policy, dict)
        assert isinstance(policy["upgrade_policy"], dict)
        policy["upgrade_policy"]["archive_target_scope"] = [
            "x86_64-linux",
            "x86_64-linux",
        ]
        write_json(root / TOOLCHAIN_POLICY, policy)
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
        else:
            raise AssertionError("duplicate archive_target_scope did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TARGET_ORDER_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TARGET_ORDER_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Phase 2 cross targets keep their canonical fixture order."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    fixture = read_json(root / CROSS_TARGETS_FIXTURE)
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)
    archive_scope = load_archive_target_scope(root)
    print("PHASE2_CROSS_TARGET_ORDER_CONTRACT=pass")
    print(f"PHASE2_CROSS_TARGET_ORDER_CONTRACT_TARGET_COUNT={len(cross_targets)}")
    print(f"PHASE2_CROSS_TARGET_ORDER_CONTRACT_ARCHIVE_SCOPE_COUNT={len(archive_scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
