#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_REVIEW_STATUS_BY_TARGET = {
    "x86_64-linux": "pinned bootstrap archive",
    "aarch64-linux": "route contract only",
}


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


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
            raise SystemExit(
                f"unsupported archive_target_scope target in required file: {policy_path}: {value}"
            )
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


def run_contract(root: Path) -> int:
    issues = collect_fixture_issues(root)
    if issues:
        for code, detail in issues:
            print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_ISSUE={code}:{detail}")
        print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_ISSUE_COUNT={len(issues)}")
        return 1

    policy = load_expected_policy_contract(root)
    print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT=pass")
    print(
        "PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_ARCHIVE_SCOPE_COUNT="
        f"{len(policy['archive_target_scope'])}"
    )
    print(
        "PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_REQUIRED_ROUTE_COUNT="
        f"{len(EXPECTED_REQUIRED_MAKE_ROUTES)}"
    )
    print(
        "PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_TARGET_COUNT="
        f"{len(SUPPORTED_CROSS_TARGETS)}"
    )
    return 0


def build_passing_root(root: Path) -> None:
    write_text(
        resolve_path(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "sha256-x86_64-linux",
                },
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
                        "validation_mode": "archive_required",
                        "route": EXPECTED_ROUTE,
                        "review_status": "pinned bootstrap archive",
                    },
                    {
                        "target": "aarch64-linux",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_ROUTE,
                        "review_status": "route contract only",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_policy_fixture_contract_") as tmpdir:
        root = Path(tmpdir)
        build_passing_root(root)

        if run_contract(root) != 0:
            print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST_FAIL=expected-pass")
            return 1

        cases = [
            (
                "missing_policy",
                lambda: resolve_path(root, POLICY).unlink(),
                "required file missing",
            ),
            (
                "missing_fixture",
                lambda: resolve_path(root, FIXTURE).unlink(),
                "required file missing",
            ),
            (
                "duplicate_policy_key",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    '{"archive_sha256":{"x86_64-linux":"one","x86_64-linux":"two"},"upgrade_policy":{"archive_target_scope":["x86_64-linux"],"required_make_routes":["phase2-toolchain","phase2-tools","phase2-kconfig","phase2-cross","phase2-genksyms","phase2-fixdep","phase2-validate"]}}\n',
                ),
                "duplicate json key",
            ),
            (
                "duplicate_fixture_key",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    '{"phase":"Phase 2","phase":"Phase 2","status":"active","route":"make -C zigux phase2-cross","archive_target_scope":["x86_64-linux"],"cross_targets":[]}\n',
                ),
                "duplicate json key",
            ),
            (
                "invalid_required_make_routes",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {"x86_64-linux": "sha256-x86_64-linux"},
                            "upgrade_policy": {
                                "archive_target_scope": ["x86_64-linux"],
                                "required_make_routes": [
                                    "phase2-toolchain",
                                    "phase2-tools",
                                    "phase2-validate",
                                    "phase2-cross",
                                ],
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "invalid required_make_routes",
            ),
            (
                "archive_sha_target_drift",
                lambda: write_text(
                    resolve_path(root, POLICY),
                    json.dumps(
                        {
                            "archive_sha256": {"aarch64-linux": "sha256-aarch64-linux"},
                            "upgrade_policy": {
                                "archive_target_scope": ["x86_64-linux"],
                                "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                            },
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "archive_sha256 target drift",
            ),
            (
                "invalid_route",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": "make -C zigux phase2-validate",
                            "archive_target_scope": ["x86_64-linux"],
                            "cross_targets": [
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_FIXTURE_FIELD",
            ),
            (
                "invalid_review_status",
                lambda: write_text(
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
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_REVIEW_STATUS",
            ),
            (
                "invalid_order",
                lambda: write_text(
                    resolve_path(root, FIXTURE),
                    json.dumps(
                        {
                            "phase": "Phase 2",
                            "status": "active",
                            "route": EXPECTED_ROUTE,
                            "archive_target_scope": ["x86_64-linux"],
                            "cross_targets": [
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_ORDER",
            ),
            (
                "invalid_mode_matrix",
                lambda: write_text(
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
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "aarch64-linux",
                                    "validation_mode": "route_contract_only",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "route contract only",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "INVALID_CROSS_TARGET_MATRIX",
            ),
            (
                "duplicate_cross_target",
                lambda: write_text(
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
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                                {
                                    "target": "x86_64-linux",
                                    "validation_mode": "archive_required",
                                    "route": EXPECTED_ROUTE,
                                    "review_status": "pinned bootstrap archive",
                                },
                            ],
                        },
                        indent=2,
                    )
                    + "\n",
                ),
                "DUPLICATE_CROSS_TARGET_ENTRY",
            ),
        ]

        case_count = 0
        for name, mutate, expected_fragment in cases:
            build_passing_root(root)
            mutate()
            try:
                code = run_contract(root)
                if code == 0:
                    print(
                        "PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST_FAIL="
                        f"{name}:expected-failure"
                    )
                    return 1
            except SystemExit as exc:
                if expected_fragment not in str(exc):
                    print(
                        "PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST_FAIL="
                        f"{name}:expected={expected_fragment}:actual={exc}"
                    )
                    return 1
            case_count += 1

    print("PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_POLICY_FIXTURE_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 cross policy and fixture contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to validate (defaults to the current checkout)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the hermetic self-test suite instead of validating the repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    return run_contract(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
