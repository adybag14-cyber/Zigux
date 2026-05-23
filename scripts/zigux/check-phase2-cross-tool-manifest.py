#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
EXPECTED_SCOPE = (
    "current directly readable scripts-root toolchain, local-archive, installer, "
    "direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and "
    "tranche-closure reminder packet"
)
EXPECTED_CHECKERS = (
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
)
EXPECTED_CROSS_ROUTE_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_POLICY_SURFACE = ("scripts/zigux/zig-toolchain-policy.json",)
EXPECTED_REQUIRED_MAKE_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_WRAPPER_PREFIX = (
    "zigux/Makefile",
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
)
SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
ROUTE = "make -C zigux phase2-cross"
WORKFLOW_ROUTE_LINE = "run: make -C zigux phase2-cross"
MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
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


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, indent=2) + "\n")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_duplicates(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def require_string_list(payload: object, path: Path, field: str) -> list[str]:
    if not isinstance(payload, list) or not payload:
        raise SystemExit(f"invalid {field} in required file: {path}")
    normalized: list[str] = []
    for entry in payload:
        if not isinstance(entry, str) or not entry.strip():
            raise SystemExit(f"invalid {field} in required file: {path}")
        normalized.append(entry.strip())
    return normalized


def load_policy(root: Path) -> tuple[list[str], dict[str, str]]:
    payload = read_json(root / POLICY)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / POLICY}")
    if payload.get("phase") != EXPECTED_PHASE:
        raise SystemExit(f"invalid phase in required file: {root / POLICY}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / POLICY}")
    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {root / POLICY}")
    archive_target_scope = require_string_list(
        upgrade_policy.get("archive_target_scope"),
        root / POLICY,
        "archive_target_scope",
    )
    if find_duplicates(archive_target_scope):
        raise SystemExit(f"duplicate archive_target_scope entry in required file: {root / POLICY}")
    unsupported = [target for target in archive_target_scope if target not in SUPPORTED_CROSS_TARGETS]
    if unsupported:
        raise SystemExit(
            "unsupported archive_target_scope targets in required file: " + ", ".join(unsupported)
        )
    expected_modes = {
        target: ("archive_required" if target in archive_target_scope else "route_contract_only")
        for target in SUPPORTED_CROSS_TARGETS
    }
    return archive_target_scope, expected_modes


def collect_surface_issues(root: Path, surfaces: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(surfaces, dict):
        return [("INVALID_MANIFEST_FIELD", "present_surfaces")]

    checkers = surfaces.get("checkers")
    if not isinstance(checkers, list):
        issues.append(("INVALID_SURFACE_CATEGORY", "checkers"))
    else:
        string_checkers = [entry for entry in checkers if isinstance(entry, str)]
        for entry in EXPECTED_CHECKERS:
            if entry not in string_checkers:
                issues.append(("MISSING_CHECKER_ENTRY", entry))
        for entry in find_duplicates(string_checkers):
            if entry in EXPECTED_CHECKERS:
                issues.append(("DUPLICATE_CHECKER_ENTRY", entry))
        expected_positions = [string_checkers.index(entry) for entry in EXPECTED_CHECKERS if entry in string_checkers]
        if len(expected_positions) == len(EXPECTED_CHECKERS) and expected_positions != sorted(expected_positions):
            issues.append(("CHECKER_ORDER_MISMATCH", ",".join(EXPECTED_CHECKERS)))

    cross_support = surfaces.get("cross_route_support")
    if not isinstance(cross_support, list):
        issues.append(("INVALID_SURFACE_CATEGORY", "cross_route_support"))
    else:
        string_support = [entry for entry in cross_support if isinstance(entry, str)]
        if string_support != list(EXPECTED_CROSS_ROUTE_SUPPORT):
            issues.append(("CROSS_ROUTE_SUPPORT_MISMATCH", json.dumps(string_support)))
        for entry in string_support:
            if not (root / entry).exists():
                issues.append(("MISSING_SURFACE_PATH", f"cross_route_support:{entry}"))

    policy_surface = surfaces.get("policy")
    if not isinstance(policy_surface, list):
        issues.append(("INVALID_SURFACE_CATEGORY", "policy"))
    else:
        string_policy = [entry for entry in policy_surface if isinstance(entry, str)]
        if string_policy != list(EXPECTED_POLICY_SURFACE):
            issues.append(("POLICY_SURFACE_MISMATCH", json.dumps(string_policy)))
        for entry in string_policy:
            if not (root / entry).exists():
                issues.append(("MISSING_SURFACE_PATH", f"policy:{entry}"))

    wrappers = surfaces.get("make_wrappers")
    if not isinstance(wrappers, list):
        issues.append(("INVALID_SURFACE_CATEGORY", "make_wrappers"))
    else:
        string_wrappers = [entry for entry in wrappers if isinstance(entry, str)]
        for entry in EXPECTED_WRAPPER_PREFIX:
            if entry not in string_wrappers:
                issues.append(("MISSING_MAKE_WRAPPER", entry))
        for entry in find_duplicates(string_wrappers):
            if entry in EXPECTED_WRAPPER_PREFIX:
                issues.append(("DUPLICATE_MAKE_WRAPPER", entry))
        prefix = string_wrappers[: len(EXPECTED_WRAPPER_PREFIX)]
        if prefix != list(EXPECTED_WRAPPER_PREFIX):
            issues.append(("MAKE_WRAPPER_ORDER_MISMATCH", json.dumps(prefix)))
    return issues


def collect_fixture_issues(root: Path, expected_scope: list[str], expected_modes: dict[str, str]) -> list[tuple[str, str]]:
    payload = read_json(root / CROSS_TARGETS)
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_CROSS_TARGET_FIXTURE", type(payload).__name__)]
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != expected_scope:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_CROSS_TARGET_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", type(entry).__name__))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        review_status = entry.get("review_status")
        route = entry.get("route")
        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", "target"))
            continue
        target = target.strip()
        if target in actual_modes:
            issues.append(("DUPLICATE_CROSS_TARGET_ENTRY", target))
        if not isinstance(mode, str) or not mode.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        actual_modes[target] = mode.strip()

    if actual_modes != expected_modes:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_json(root / MANIFEST)
    if not isinstance(manifest, dict):
        raise SystemExit(f"invalid json shape in required file: {root / MANIFEST}")

    issues: list[tuple[str, str]] = []
    if manifest.get("phase") != EXPECTED_PHASE:
        issues.append(("TOP_LEVEL_MISMATCH", "phase"))
    if manifest.get("status") != EXPECTED_STATUS:
        issues.append(("TOP_LEVEL_MISMATCH", "status"))
    if manifest.get("workflow") != EXPECTED_WORKFLOW:
        issues.append(("TOP_LEVEL_MISMATCH", "workflow"))
    if manifest.get("scope") != EXPECTED_SCOPE:
        issues.append(("TOP_LEVEL_MISMATCH", "scope"))
    if manifest.get("repo_reality_gaps") != []:
        issues.append(("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps"))

    issues.extend(collect_surface_issues(root, manifest.get("present_surfaces")))

    expected_scope, expected_modes = load_policy(root)
    issues.extend(collect_fixture_issues(root, expected_scope, expected_modes))

    workflow_text = read_text(root / WORKFLOW)
    workflow_count = count_exact_lines(workflow_text, WORKFLOW_ROUTE_LINE)
    if workflow_count == 0:
        issues.append(("MISSING_WORKFLOW_LINE", WORKFLOW_ROUTE_LINE))
    elif workflow_count != 1:
        issues.append(("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_ROUTE_LINE}:count={workflow_count}"))

    makefile_text = read_text(root / MAKEFILE)
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_TOOL_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_manifest() -> dict[str, object]:
    return {
        "phase": EXPECTED_PHASE,
        "status": EXPECTED_STATUS,
        "scope": EXPECTED_SCOPE,
        "workflow": EXPECTED_WORKFLOW,
        "present_surfaces": {
            "checkers": [
                "scripts/zigux/check-phase2-tests-readme-alignment.py",
                *EXPECTED_CHECKERS,
                "scripts/zigux/check-phase2-toolchain-pinning.py",
            ],
            "cross_route_support": list(EXPECTED_CROSS_ROUTE_SUPPORT),
            "policy": list(EXPECTED_POLICY_SURFACE),
            "make_wrappers": [
                *EXPECTED_WRAPPER_PREFIX,
                "make -C zigux phase2-genksyms",
                "make -C zigux phase2-fixdep",
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ],
        },
        "repo_reality_gaps": [],
        "notes": ["present"],
    }


def build_self_test_root(root: Path) -> None:
    write_json(root / MANIFEST, build_self_test_manifest())
    write_json(
        root / POLICY,
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
    )
    write_json(
        root / CROSS_TARGETS,
        {
            "phase": EXPECTED_PHASE,
            "status": EXPECTED_STATUS,
            "route": ROUTE,
            "archive_target_scope": ["x86_64-linux"],
            "cross_targets": [
                {
                    "target": "x86_64-linux",
                    "review_status": "pinned bootstrap archive",
                    "validation_mode": "archive_required",
                    "route": ROUTE,
                },
                {
                    "target": "aarch64-linux",
                    "review_status": "route contract only",
                    "validation_mode": "route_contract_only",
                    "route": ROUTE,
                },
            ],
        },
    )
    write_text(root / MAKEFILE, "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root / WORKFLOW, "name: zigux-bootstrap\n" + WORKFLOW_ROUTE_LINE + "\n")
    write_text(root / "scripts" / "zigux" / "check-phase2-cross.py", "present\n")
    write_text(root / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py", "present\n")
    write_text(root / "scripts" / "zigux" / "zig-toolchain-policy.json", read_text(root / POLICY))
    write_text(root / "zigux" / "Makefile", read_text(root / MAKEFILE))
    write_text(root / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json", read_text(root / CROSS_TARGETS))


def run_self_test() -> int:
    expected_case_count = 24
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest_path = root / MANIFEST
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)

        for field in ("phase", "status", "workflow", "scope"):
            build_self_test_root(root)
            manifest = read_json(manifest_path)
            assert isinstance(manifest, dict)
            manifest[field] = "broken"
            write_json(manifest_path, manifest)
            assert ("TOP_LEVEL_MISMATCH", field) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["repo_reality_gaps"] = ["gap"]
        write_json(manifest_path, manifest)
        assert ("NONEMPTY_REPO_REALITY_GAPS", "repo_reality_gaps") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["cross_route_support"] = ["zigux/tests/fixtures/phase2_cross_targets.json"]
        write_json(manifest_path, manifest)
        assert any(code == "CROSS_ROUTE_SUPPORT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["policy"] = []
        write_json(manifest_path, manifest)
        assert any(code == "POLICY_SURFACE_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["checkers"] = [
            "scripts/zigux/check-phase2-cross-selftest-alignment.py",
            "scripts/zigux/check-phase2-cross.py",
        ]
        write_json(manifest_path, manifest)
        assert ("CHECKER_ORDER_MISMATCH", ",".join(EXPECTED_CHECKERS)) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["checkers"].append("scripts/zigux/check-phase2-cross.py")
        write_json(manifest_path, manifest)
        assert ("DUPLICATE_CHECKER_ENTRY", "scripts/zigux/check-phase2-cross.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["make_wrappers"][0], manifest["present_surfaces"]["make_wrappers"][1] = (
            manifest["present_surfaces"]["make_wrappers"][1],
            manifest["present_surfaces"]["make_wrappers"][0],
        )
        write_json(manifest_path, manifest)
        assert any(code == "MAKE_WRAPPER_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["present_surfaces"]["make_wrappers"].append("make -C zigux phase2-cross")
        write_json(manifest_path, manifest)
        assert ("DUPLICATE_MAKE_WRAPPER", "make -C zigux phase2-cross") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy = read_json(root / POLICY)
        assert isinstance(policy, dict)
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_json(root / POLICY, policy)
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing phase2-cross policy route did not abort")

        build_self_test_root(root)
        policy = read_json(root / POLICY)
        assert isinstance(policy, dict)
        policy["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        policy["archive_sha256"] = {"riscv64-linux": "3" * 64}
        write_json(root / POLICY, policy)
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope targets" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("unsupported policy target did not abort")

        build_self_test_root(root)
        fixture = read_json(root / CROSS_TARGETS)
        assert isinstance(fixture, dict)
        fixture["archive_target_scope"] = ["aarch64-linux"]
        write_json(root / CROSS_TARGETS, fixture)
        assert ("INVALID_CROSS_TARGET_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = read_json(root / CROSS_TARGETS)
        assert isinstance(fixture, dict)
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        write_json(root / CROSS_TARGETS, fixture)
        assert any(code == "INVALID_CROSS_TARGET_MATRIX" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        fixture = read_json(root / CROSS_TARGETS)
        assert isinstance(fixture, dict)
        fixture["cross_targets"][0]["review_status"] = ""
        write_json(root / CROSS_TARGETS, fixture)
        assert ("INVALID_CROSS_TARGET_ENTRY", "x86_64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = read_json(root / CROSS_TARGETS)
        assert isinstance(fixture, dict)
        fixture["cross_targets"].append(dict(fixture["cross_targets"][0]))
        write_json(root / CROSS_TARGETS, fixture)
        assert ("DUPLICATE_CROSS_TARGET_ENTRY", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root / WORKFLOW, "name: zigux-bootstrap\n")
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_ROUTE_LINE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(root / WORKFLOW, "name: zigux-bootstrap\n" + WORKFLOW_ROUTE_LINE + "\n" + WORKFLOW_ROUTE_LINE + "\n")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_ROUTE_LINE}:count=2") in collect_issues(root)
        checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root / MAKEFILE, "\n".join(line for line in MAKEFILE_LINES if line != marker) + "\n")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        (root / MANIFEST).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_TOOL_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 cross packet in the tool manifest aligned with the live route surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_TOOL_MANIFEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_TARGET_COUNT={len(SUPPORTED_CROSS_TARGETS)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_WRAPPER_COUNT={len(EXPECTED_WRAPPER_PREFIX)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())