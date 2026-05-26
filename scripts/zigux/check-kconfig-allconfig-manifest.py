#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
CASES_PATH = FIXTURE_DIR / "cases.json"
CONF_MANIFEST_PATH = FIXTURE_DIR / "conf_manifest.json"
CONF_BRIDGE_PATH = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"

ALLCONFIG_OVERRIDE_MODES = (
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
)

ALLCONFIG_SENTINEL_MODES = (
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
)

HELPER_ANCHOR = "conf bridge emits explicit empty allconfig override for allmodconfig"
EXPECTED_IMPLICIT_OMISSION_MODES = (
    "allmodconfig",
    "randconfig",
)
EXPECTED_EXPLICIT_OVERRIDE_MODES = (
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
)
EXPECTED_SELF_TEST_CASE_COUNT = 6


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError:
        return None, (issue_code, path.name)


def ordered_conf_bridge_tests(path: Path) -> list[str]:
    return re.findall(r'^test "([^"]+)" \{$', read_text(path), re.M)


def load_conf_cases(path: Path) -> tuple[list[dict[str, object]], list[tuple[str, str]]]:
    payload, issue = read_json(path, "INVALID_CASES_JSON")
    if issue is not None:
        return [], [issue]
    if not isinstance(payload, dict):
        return [], [("INVALID_CASES_PAYLOAD", type(payload).__name__)]

    conf_cases = payload.get("conf_cases")
    if not isinstance(conf_cases, list):
        return [], [("INVALID_CONF_CASES_FIELD", type(conf_cases).__name__)]

    issues: list[tuple[str, str]] = []
    parsed_cases: list[dict[str, object]] = []
    for index, case in enumerate(conf_cases):
        if not isinstance(case, dict):
            issues.append(("INVALID_CONF_CASE_ENTRY", f"{index}:{type(case).__name__}"))
            continue
        for field_name in ("name", "mode", "expected"):
            value = case.get(field_name)
            if not isinstance(value, str):
                issues.append(("INVALID_CONF_CASE_FIELD", f"{index}:{field_name}:{type(value).__name__}"))
        parsed_cases.append(case)

    return parsed_cases, issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    cases_path = fixture_dir / "cases.json"
    manifest_path = fixture_dir / "conf_manifest.json"
    conf_bridge_path = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"

    required_paths = (cases_path, manifest_path, conf_bridge_path)
    issues: list[tuple[str, str]] = []
    for path in required_paths:
        if not path.exists():
            issues.append(("MISSING_REQUIRED_PATH", str(path.relative_to(root))))
    if issues:
        return issues

    conf_cases, case_issues = load_conf_cases(cases_path)
    if case_issues:
        return case_issues

    manifest, manifest_issue = read_json(manifest_path, "INVALID_CONF_MANIFEST_JSON")
    if manifest_issue is not None:
        return [manifest_issue]
    if not isinstance(manifest, dict):
        return [("INVALID_CONF_MANIFEST_PAYLOAD", type(manifest).__name__)]

    source_anchors = ordered_conf_bridge_tests(conf_bridge_path)
    if HELPER_ANCHOR not in source_anchors:
        issues.append(("MISSING_REQUIRED_CONF_BRIDGE_TEST", HELPER_ANCHOR))

    actual_implicit = manifest.get("helper_local_allconfig_implicit_omission_modes")
    if actual_implicit != list(EXPECTED_IMPLICIT_OMISSION_MODES):
        issues.append(
            (
                "CONF_MANIFEST_IMPLICIT_ALLCONFIG_MODES_MISMATCH",
                f"actual={actual_implicit!r}:expected={list(EXPECTED_IMPLICIT_OMISSION_MODES)!r}",
            )
        )

    actual_explicit = manifest.get("helper_local_allconfig_explicit_override_modes")
    if actual_explicit != list(EXPECTED_EXPLICIT_OVERRIDE_MODES):
        issues.append(
            (
                "CONF_MANIFEST_EXPLICIT_ALLCONFIG_MODES_MISMATCH",
                f"actual={actual_explicit!r}:expected={list(EXPECTED_EXPLICIT_OVERRIDE_MODES)!r}",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("KCONFIG_ALLCONFIG_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    write_text(
        root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
        '\n'.join(
            (
                'const std = @import("std");',
                "",
                f'test "{HELPER_ANCHOR}" {{',
                "    try std.testing.expect(true);",
                "}",
                "",
            )
        ),
    )
    conf_cases = [
        {"name": "allnoconfig", "mode": "allnoconfig", "expected": "allnoconfig_expected.json", "allconfig": "mini.config"},
        {"name": "allmodconfig", "mode": "allmodconfig", "expected": "allmodconfig_expected.json", "allconfig": ""},
        {"name": "alldefconfig", "mode": "alldefconfig", "expected": "alldefconfig_expected.json", "allconfig": "mini-all.config"},
        {"name": "randconfig", "mode": "randconfig", "expected": "randconfig_expected.json"},
        {"name": "oldconfig", "mode": "oldconfig", "expected": "oldconfig_expected.json"},
    ]
    write_text(
        fixture_dir / "cases.json",
        json.dumps({"conf_cases": conf_cases, "confdata_cases": []}, indent=2) + "\n",
    )
    write_text(
        fixture_dir / "conf_manifest.json",
        json.dumps(
            {
                "helper_local_allconfig_implicit_omission_modes": ["allmodconfig", "randconfig"],
                "helper_local_allconfig_explicit_override_modes": ["allmodconfig", "allnoconfig", "allyesconfig", "alldefconfig", "randconfig"],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_allconfig_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json", "{broken\n")
        assert ("INVALID_CONF_MANIFEST_JSON", "conf_manifest.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        manifest_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["helper_local_allconfig_implicit_omission_modes"] = []
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_IMPLICIT_ALLCONFIG_MODES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        manifest_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
        manifest = json.loads(read_text(manifest_path))
        manifest["helper_local_allconfig_explicit_override_modes"] = ["allnoconfig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "CONF_MANIFEST_EXPLICIT_ALLCONFIG_MODES_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_self_test_root(root)
        cases_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
        write_text(cases_path, "{broken\n")
        assert ("INVALID_CASES_JSON", "cases.json") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        bridge_path = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
        write_text(bridge_path, 'const std = @import("std");\n')
        assert ("MISSING_REQUIRED_CONF_BRIDGE_TEST", HELPER_ANCHOR) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("KCONFIG_ALLCONFIG_MANIFEST_SELF_TEST=pass")
    print(f"KCONFIG_ALLCONFIG_MANIFEST_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the live kconfig allconfig manifest packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("KCONFIG_ALLCONFIG_MANIFEST=pass")
    print(f"KCONFIG_ALLCONFIG_IMPLICIT_OMISSION_MODE_COUNT={len(EXPECTED_IMPLICIT_OMISSION_MODES)}")
    print(f"KCONFIG_ALLCONFIG_EXPLICIT_OVERRIDE_MODE_COUNT={len(EXPECTED_EXPLICIT_OVERRIDE_MODES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
