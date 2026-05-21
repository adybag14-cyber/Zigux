#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"

ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
REQUIRED_MANIFEST_SCOPE_FRAGMENT = "direct cross-route"
REQUIRED_CROSS_ROUTE_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
REQUIRED_BOOTSTRAP_HELPER = "scripts/zigux/install-zig.py"
REQUIRED_POLICY_ENTRY = "scripts/zigux/zig-toolchain-policy.json"
REQUIRED_MAKE_WRAPPERS = (
    "make -C zigux phase2-cross",
    "make -C zigux phase2-validate",
)
REQUIRED_NOTE_MARKERS = (
    "direct cross-route checker",
    "phase2_cross_targets fixture",
    "installer helper",
    "phase2-cross",
)
MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)
CROSS_CHECKER_MARKERS = (
    'ROUTE = "make -C zigux phase2-cross"',
    'ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")',
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


def parse_policy_scope(root: Path) -> list[str]:
    payload = read_json(root / TOOLCHAIN_POLICY.relative_to(ROOT))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / TOOLCHAIN_POLICY.relative_to(ROOT)}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY.relative_to(ROOT)}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(
            f"invalid archive_target_scope in required file: {root / TOOLCHAIN_POLICY.relative_to(ROOT)}"
        )

    normalized: list[str] = []
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(
                f"invalid archive_target_scope in required file: {root / TOOLCHAIN_POLICY.relative_to(ROOT)}"
            )
        target = value.strip()
        if target not in SUPPORTED_TARGETS:
            raise SystemExit(f"unsupported archive_target_scope target in required file: {target}")
        if target in normalized:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {target}")
        normalized.append(target)
    return normalized


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(root / MANIFEST.relative_to(ROOT))
    if not isinstance(payload, dict):
        return [("INVALID_MANIFEST_SHAPE", type(payload).__name__)]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_MANIFEST_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_MANIFEST_FIELD", "status"))

    scope = payload.get("scope")
    if not isinstance(scope, str) or REQUIRED_MANIFEST_SCOPE_FRAGMENT not in scope:
        issues.append(("INVALID_MANIFEST_SCOPE", repr(scope)))

    surfaces = payload.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return issues + [("INVALID_MANIFEST_FIELD", "present_surfaces")]

    cross_route_support = surfaces.get("cross_route_support")
    if cross_route_support != list(REQUIRED_CROSS_ROUTE_SUPPORT):
        issues.append(("INVALID_CROSS_ROUTE_SUPPORT", repr(cross_route_support)))

    bootstrap_helpers = surfaces.get("bootstrap_helpers")
    if not isinstance(bootstrap_helpers, list) or REQUIRED_BOOTSTRAP_HELPER not in bootstrap_helpers:
        issues.append(("MISSING_BOOTSTRAP_HELPER", REQUIRED_BOOTSTRAP_HELPER))

    policy = surfaces.get("policy")
    if not isinstance(policy, list) or policy != [REQUIRED_POLICY_ENTRY]:
        issues.append(("INVALID_POLICY_SURFACE", repr(policy)))

    make_wrappers = surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list):
        issues.append(("INVALID_MAKE_WRAPPERS", repr(make_wrappers)))
    else:
        for marker in REQUIRED_MAKE_WRAPPERS:
            if marker not in make_wrappers:
                issues.append(("MISSING_MAKE_WRAPPER", marker))

    notes = payload.get("notes")
    if not isinstance(notes, list) or not all(isinstance(note, str) for note in notes):
        issues.append(("INVALID_MANIFEST_FIELD", "notes"))
    else:
        joined_notes = "\n".join(notes)
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in joined_notes:
                issues.append(("MISSING_NOTE_MARKER", marker))

    return issues


def collect_fixture_issues(root: Path, policy_scope: list[str]) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    payload = read_json(root / CROSS_TARGETS.relative_to(ROOT))
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    if payload.get("phase") != "Phase 2":
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != "active":
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != policy_scope:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list):
        return issues + [("INVALID_FIXTURE_FIELD", "cross_targets")]

    actual_modes: dict[str, str] = {}
    for entry in cross_targets:
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", repr(entry)))
            continue
        target = entry.get("target")
        mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or target not in SUPPORTED_TARGETS:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", repr(target)))
            continue
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(mode, str):
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        actual_modes[target] = mode

    expected_modes = {
        target: ("archive_required" if target in policy_scope else "route_contract_only")
        for target in SUPPORTED_TARGETS
    }
    if actual_modes != expected_modes:
        issues.append(("INVALID_CROSS_TARGET_MATRIX", json.dumps(actual_modes, sort_keys=True)))

    return issues


def collect_source_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))
    checker_text = read_text(root / CROSS_CHECKER.relative_to(ROOT))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in CROSS_CHECKER_MARKERS:
        count = checker_text.count(marker)
        if count == 0:
            issues.append(("MISSING_CROSS_CHECKER_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_CROSS_CHECKER_MARKER", f"{marker}:count={count}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    policy_scope = parse_policy_scope(root)
    issues: list[tuple[str, str]] = []
    issues.extend(collect_manifest_issues(root))
    issues.extend(collect_fixture_issues(root, policy_scope))
    issues.extend(collect_source_issues(root))
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
        root / MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
                "workflow": ".github/workflows/zigux-bootstrap.yml",
                "present_surfaces": {
                    "cross_route_support": list(REQUIRED_CROSS_ROUTE_SUPPORT),
                    "bootstrap_helpers": [REQUIRED_BOOTSTRAP_HELPER],
                    "policy": [REQUIRED_POLICY_ENTRY],
                    "make_wrappers": list(REQUIRED_MAKE_WRAPPERS),
                },
                "notes": [
                    "Keep the returned installer helper, direct cross-route checker, phase2_cross_targets fixture, and phase2-cross make wrappers explicit through the current Phase 2 tool packet."
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / TOOLCHAIN_POLICY.relative_to(ROOT),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / CROSS_TARGETS.relative_to(ROOT),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
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
            indent=2,
        )
        + "\n",
    )
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(root / CROSS_CHECKER.relative_to(ROOT), "\n".join(CROSS_CHECKER_MARKERS) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        manifest_path = root / MANIFEST.relative_to(ROOT)
        fixture_path = root / CROSS_TARGETS.relative_to(ROOT)
        policy_path = root / TOOLCHAIN_POLICY.relative_to(ROOT)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        checker_path = root / CROSS_CHECKER.relative_to(ROOT)

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["cross_route_support"] = ["scripts/zigux/check-phase2-cross.py"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_ROUTE_SUPPORT", "['scripts/zigux/check-phase2-cross.py']") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["bootstrap_helpers"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_HELPER", REQUIRED_BOOTSTRAP_HELPER) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["notes"] = ["missing cross wording"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_NOTE_MARKER", "direct cross-route checker") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_MATRIX", '{"aarch64-linux": "archive_required", "x86_64-linux": "archive_required"}') in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope target" in str(exc)
            checks += 1
        else:
            raise AssertionError("unsupported archive target scope did not abort")

        build_self_test_root(root)
        makefile_path.write_text("phase2-cross:\n", encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        checker_path.write_text('ROUTE = "make -C zigux phase2-cross"\n', encoding="utf-8")
        assert ("MISSING_CROSS_CHECKER_MARKER", 'ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")') in collect_issues(root)
        checks += 1

    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the live Phase 2 cross packet stays aligned inside the Phase 2 tool manifest.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    policy_scope = parse_policy_scope(args.root.resolve())
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_ARCHIVE_SCOPE={','.join(policy_scope)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_REQUIRED_WRAPPER_COUNT={len(REQUIRED_MAKE_WRAPPERS)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_TARGET_COUNT={len(SUPPORTED_TARGETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
