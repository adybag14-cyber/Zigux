#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
FIXTURE = Path("zigux/tests/fixtures/phase2_cross_targets.json")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
MAKEFILE = Path("zigux/Makefile")

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
EXPECTED_VALIDATE_ROUTE = "make -C zigux phase2-validate"
EXPECTED_PHASE_ROUTE = "make -C zigux phase2"
EXPECTED_TARGET_ORDER = ("x86_64-linux", "aarch64-linux")
EXPECTED_REVIEW_STATUS_BY_MODE = {
    "archive_required": "pinned bootstrap archive",
    "route_contract_only": "route contract only",
}
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
EXPECTED_MANIFEST_KEYS = {
    "phase",
    "scope",
    "status",
    "workflow",
    "notes",
    "present_surfaces",
    "repo_reality_gaps",
}
EXPECTED_SURFACE_KEYS = {
    "archive_support",
    "artifact_support",
    "bootstrap_helpers",
    "bridge_helpers",
    "checkers",
    "closure_notes",
    "cross_route_support",
    "fixdep_support",
    "fixture_roster",
    "make_wrappers",
    "policy",
    "review_surfaces",
    "validators",
}
EXPECTED_SELF_TEST_CASE_COUNT = 13


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, rel: Path) -> Path:
    try:
        return root / rel.relative_to(ROOT)
    except ValueError:
        return root / rel


def duplicate_guard_object_pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate json key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    try:
        return json.loads(
            read_text(path),
            object_pairs_hook=duplicate_guard_object_pairs_hook,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and value.strip() == value and value != ""


def ensure_string_list(value: object, code: str) -> tuple[list[str], list[tuple[str, str]]]:
    if not isinstance(value, list):
        return [], [(code, repr(value))]

    issues: list[tuple[str, str]] = []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not is_non_empty_string(item):
            issues.append((code, repr(item)))
            continue
        if item in seen:
            issues.append((f"{code}_DUPLICATE", item))
            continue
        seen.add(item)
        normalized.append(item)
    return normalized, issues


def load_policy_archive_scope(root: Path) -> list[str]:
    payload = read_json(resolve_path(root, POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {resolve_path(root, POLICY)}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, POLICY)}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, POLICY)}"
        )
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, POLICY)}"
        )

    normalized: list[str] = []
    seen: set[str] = set()
    for target in archive_target_scope:
        if not is_non_empty_string(target):
            raise SystemExit(
                f"invalid archive_target_scope entry in required file: {resolve_path(root, POLICY)}"
            )
        if target not in EXPECTED_TARGET_ORDER:
            raise SystemExit(
                f"unsupported archive_target_scope target in required file: {resolve_path(root, POLICY)}: {target}"
            )
        if target in seen:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {resolve_path(root, POLICY)}: {target}"
            )
        seen.add(target)
        normalized.append(target)
    return normalized


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, FIXTURE))
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    archive_scope = load_policy_archive_scope(root)
    fixture_scope, fixture_scope_issues = ensure_string_list(
        payload.get("archive_target_scope"),
        "INVALID_FIXTURE_ARCHIVE_SCOPE",
    )
    issues.extend(fixture_scope_issues)
    if not fixture_scope_issues and fixture_scope != archive_scope:
        issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE", ",".join(fixture_scope)))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_target_order: list[str] = []
    archive_required_targets: list[str] = []
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{index}:{type(entry).__name__}"))
            continue
        unexpected_keys = sorted(set(entry) - {"target", "review_status", "validation_mode", "route"})
        for key in unexpected_keys:
            issues.append(("UNEXPECTED_CROSS_TARGET_KEY", f"{index}:{key}"))

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not is_non_empty_string(target):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{index}:target"))
            continue
        actual_target_order.append(target)
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if validation_mode not in EXPECTED_REVIEW_STATUS_BY_MODE:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if review_status != EXPECTED_REVIEW_STATUS_BY_MODE[validation_mode]:
            issues.append(("INVALID_CROSS_TARGET_STATUS", target))
        if validation_mode == "archive_required":
            archive_required_targets.append(target)

    if actual_target_order != list(EXPECTED_TARGET_ORDER):
        issues.append(("INVALID_TARGET_ORDER", ",".join(actual_target_order)))
    if archive_required_targets != archive_scope:
        issues.append(("INVALID_ARCHIVE_REQUIRED_TARGETS", ",".join(archive_required_targets)))
    return issues


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = read_json(resolve_path(root, MANIFEST))
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_SHAPE", type(payload).__name__)]

    issues: list[tuple[str, str]] = []
    unexpected_top_level = sorted(set(payload) - EXPECTED_MANIFEST_KEYS)
    for key in unexpected_top_level:
        issues.append(("UNEXPECTED_MANIFEST_KEY", key))

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_MANIFEST_FIELD", "status"))

    present_surfaces = payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_FIELD", "present_surfaces"))
        return issues

    unexpected_surface_keys = sorted(set(present_surfaces) - EXPECTED_SURFACE_KEYS)
    for key in unexpected_surface_keys:
        issues.append(("UNEXPECTED_SURFACE_KEY", key))

    checkers, checker_issues = ensure_string_list(
        present_surfaces.get("checkers"),
        "INVALID_SURFACE_CHECKERS",
    )
    issues.extend(checker_issues)
    for required in (
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    ):
        if required not in checkers:
            issues.append(("MISSING_CROSS_CHECKER", required))

    cross_route_support, cross_route_issues = ensure_string_list(
        present_surfaces.get("cross_route_support"),
        "INVALID_SURFACE_CROSS_ROUTE_SUPPORT",
    )
    issues.extend(cross_route_issues)
    for required in (
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ):
        if required not in cross_route_support:
            issues.append(("MISSING_CROSS_ROUTE_SUPPORT", required))

    validators, validator_issues = ensure_string_list(
        present_surfaces.get("validators"),
        "INVALID_SURFACE_VALIDATORS",
    )
    issues.extend(validator_issues)
    for required in (
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
    ):
        if required not in validators:
            issues.append(("MISSING_VALIDATOR", required))

    make_wrappers, make_wrapper_issues = ensure_string_list(
        present_surfaces.get("make_wrappers"),
        "INVALID_SURFACE_MAKE_WRAPPERS",
    )
    issues.extend(make_wrapper_issues)
    for required in ("zigux/Makefile", EXPECTED_ROUTE, EXPECTED_VALIDATE_ROUTE, EXPECTED_PHASE_ROUTE):
        if required not in make_wrappers:
            issues.append(("MISSING_MAKE_WRAPPER", required))

    policy, policy_issues = ensure_string_list(
        present_surfaces.get("policy"),
        "INVALID_SURFACE_POLICY",
    )
    issues.extend(policy_issues)
    if "scripts/zigux/zig-toolchain-policy.json" not in policy:
        issues.append(("MISSING_POLICY_SURFACE", "scripts/zigux/zig-toolchain-policy.json"))

    return issues


def collect_makefile_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, MAKEFILE))
    required_lines = (
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
        "phase2: phase2-validate",
    )
    issues: list[tuple[str, str]] = []
    lines = {line.strip(): 0 for line in required_lines}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped in lines:
            lines[stripped] += 1
    for line, count in lines.items():
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{line}:count={count}"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_fixture_issues(root))
    issues.extend(collect_manifest_issues(root))
    issues.extend(collect_makefile_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
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
    write_text(
        resolve_path(root, MANIFEST),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "scope": "current bounded cross packet",
                "status": EXPECTED_STATUS,
                "workflow": ".github/workflows/zigux-bootstrap.yml",
                "notes": ["cross packet is present"],
                "present_surfaces": {
                    "archive_support": ["third_party/README.md"],
                    "artifact_support": ["scripts/zigux/artifact_diff.py"],
                    "bootstrap_helpers": ["scripts/zigux/install-zig.py"],
                    "bridge_helpers": ["scripts/zigux/kconfig/conf_bridge.zig"],
                    "checkers": [
                        "scripts/zigux/check-phase2-cross.py",
                        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
                    ],
                    "closure_notes": ["Documentation/zigux/phase2-closure.md"],
                    "cross_route_support": [
                        "scripts/zigux/check-phase2-cross.py",
                        "zigux/tests/fixtures/phase2_cross_targets.json",
                    ],
                    "fixdep_support": ["scripts/zigux/fixdep.zig"],
                    "fixture_roster": ["zigux/tests/fixtures/phase2_cross_targets.json"],
                    "make_wrappers": [
                        "zigux/Makefile",
                        EXPECTED_ROUTE,
                        EXPECTED_VALIDATE_ROUTE,
                        EXPECTED_PHASE_ROUTE,
                    ],
                    "policy": ["scripts/zigux/zig-toolchain-policy.json"],
                    "review_surfaces": ["zigux/tests/README.md"],
                    "validators": [
                        "scripts/zigux/validate-phase2.py",
                        "scripts/zigux/validate-phase2-closure.py",
                    ],
                },
                "repo_reality_gaps": [],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join(
            (
                "phase2-cross:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
                "",
                "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
                "",
                "phase2: phase2-validate",
            )
        )
        + "\n",
    )


def capture_stdout(fn, *args) -> tuple[int, str]:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        result = fn(*args)
    return result, stream.getvalue()


def run_checked(root: Path) -> int:
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=pass")
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_ARCHIVE_SCOPE=x86_64-linux")
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_REQUIRED_WRAPPER_COUNT=4")
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_TARGET_COUNT=2")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tool_manifest_contract_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = resolve_path(root, MANIFEST)
        fixture_path = resolve_path(root, FIXTURE)
        policy_path = resolve_path(root, POLICY)
        makefile_path = resolve_path(root, MAKEFILE)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = "later"
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_STATUS", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["cross_targets"].reverse()
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_TARGET_ORDER" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "INVALID_FIXTURE_ARCHIVE_SCOPE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        del payload["present_surfaces"]["cross_route_support"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_SURFACE_CROSS_ROUTE_SUPPORT", "None") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove("scripts/zigux/check-phase2-cross.py")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_CROSS_CHECKER", "scripts/zigux/check-phase2-cross.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["make_wrappers"].remove(EXPECTED_VALIDATE_ROUTE)
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MAKE_WRAPPER", EXPECTED_VALIDATE_ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_payload = json.loads(policy_path.read_text(encoding="utf-8"))
        policy_payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid required_make_routes did not abort")

        build_self_test_root(root)
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace("phase2-cross:\n", "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", "phase2-cross:") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid manifest json did not abort")

        build_self_test_root(root)
        fixture_path.write_text('{\n  "phase": "Phase 2",\n  "phase": "Again"\n}\n', encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate fixture key did not abort")

        build_self_test_root(root)
        result, output = capture_stdout(run_checked, root)
        assert result == 0
        assert "PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=pass" in output
        assert "PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_TARGET_COUNT=2" in output
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["extra"] = "noise"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_MANIFEST_KEY", "extra") in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 tool manifest aligned with the shipped cross-route packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    return run_checked(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
