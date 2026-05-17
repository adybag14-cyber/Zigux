#!/usr/bin/env python3
"""Guard the Phase 2 conf_bridge helper-anchor packet against live fixture drift."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONF_BRIDGE = Path("scripts/zigux/kconfig/conf_bridge.zig")
CASES = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")

TEST_PATTERN = re.compile(r'^test "([^"]+)" \{$')
MODE_ENUM_PATTERN = re.compile(r"pub const Mode = enum \{(.*?)\n\};", re.S)
MODE_FIELD_PATTERN = re.compile(r"^\s*([a-z0-9_]+),\s*$", re.M)

GENERAL_ANCHORS = {
    "mode surface": "conf bridge mode surface stays aligned with conf.c long options",
    "silent argv": "conf bridge emits silent flag before mode flag",
    "mode arg rejects option": "mode argument validation rejects bridge option shaped defconfig payload",
    "syncconfig nosilentupdate": "bridge options parser accepts syncconfig nosilentupdate",
    "unexpected option rejection": "bridge options parser rejects unexpected options for mode",
}

MODE_SPECIFIC_ANCHORS = {
    "defconfig": "conf bridge emits defconfig mode argument before kconfig",
    "savedefconfig": "conf bridge emits savedefconfig mode argument before kconfig",
    "randconfig override": "conf bridge emits explicit randconfig allconfig override when present",
    "randconfig sentinel omission": "conf bridge omits randconfig allconfig sentinel without explicit override",
    "allconfig sentinel": "conf bridge emits alldefconfig argv and env",
    "allconfig explicit override": "conf bridge emits explicit empty allconfig override for allmodconfig",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing required file: {rel.as_posix()}") from exc


def read_json(root: Path, rel: Path) -> object:
    try:
        return json.loads(read_text(root, rel))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {rel.as_posix()}: {exc}") from exc


def collect_test_anchors(source: str) -> set[str]:
    anchors: set[str] = set()
    for line in source.splitlines():
        match = TEST_PATTERN.match(line.strip())
        if match:
            anchors.add(match.group(1))
    return anchors


def collect_mode_enum(source: str) -> list[str]:
    match = MODE_ENUM_PATTERN.search(source)
    if not match:
        raise RuntimeError(f"unable to locate Mode enum in {CONF_BRIDGE.as_posix()}")
    return MODE_FIELD_PATTERN.findall(match.group(1))


def collect_conf_cases(root: Path) -> list[dict[str, object]]:
    payload = read_json(root, CASES)
    if not isinstance(payload, dict):
        raise RuntimeError(f"{CASES.as_posix()}: expected object root")
    conf_cases = payload.get("conf_cases")
    if not isinstance(conf_cases, list):
        raise RuntimeError(f"{CASES.as_posix()}: expected conf_cases array")

    typed_cases: list[dict[str, object]] = []
    for index, case in enumerate(conf_cases):
        if not isinstance(case, dict):
            raise RuntimeError(f"{CASES.as_posix()}[{index}]: expected object case")
        typed_cases.append(case)
    return typed_cases


def expect_anchor(issues: list[str], anchors: set[str], key: str, anchor: str) -> None:
    if anchor not in anchors:
        issues.append(f"{key}: missing helper anchor {anchor!r}")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    source = read_text(root, CONF_BRIDGE)
    anchors = collect_test_anchors(source)
    enum_modes = collect_mode_enum(source)
    conf_cases = collect_conf_cases(root)

    case_modes: list[str] = []
    silent_case_count = 0
    mode_arg_case_count = 0
    randconfig_override_case_count = 0
    randconfig_plain_case_count = 0
    allconfig_sentinel_case_count = 0
    allconfig_override_case_count = 0
    syncconfig_nosilent_case_count = 0

    for index, case in enumerate(conf_cases):
        mode = case.get("mode")
        expected = case.get("expected")
        if not isinstance(mode, str):
            issues.append(f"conf_cases[{index}]: missing string mode")
            continue
        if not isinstance(expected, str):
            issues.append(f"conf_cases[{index}]: missing string expected")
            continue

        case_modes.append(mode)
        if case.get("silent") is True:
            silent_case_count += 1
        if "mode_arg" in case:
            mode_arg_case_count += 1
        if mode == "syncconfig" and "nosilentupdate" in case:
            syncconfig_nosilent_case_count += 1
        if mode == "randconfig" and "allconfig" in case:
            randconfig_override_case_count += 1
        if mode == "randconfig" and "allconfig" not in case:
            randconfig_plain_case_count += 1
        if mode in {"allnoconfig", "allyesconfig", "allmodconfig", "alldefconfig"} and "allconfig" not in case:
            allconfig_sentinel_case_count += 1
        if mode in {"allnoconfig", "allyesconfig", "allmodconfig", "alldefconfig"} and "allconfig" in case:
            allconfig_override_case_count += 1

    if case_modes != enum_modes:
        issues.append(f"conf case modes drift from Mode enum: expected {enum_modes!r}, got {case_modes!r}")

    expect_anchor(issues, anchors, "mode surface", GENERAL_ANCHORS["mode surface"])

    if silent_case_count > 0:
        expect_anchor(issues, anchors, "silent packet", GENERAL_ANCHORS["silent argv"])
    if mode_arg_case_count > 0:
        expect_anchor(issues, anchors, "mode arg rejection packet", GENERAL_ANCHORS["mode arg rejects option"])
        expect_anchor(issues, anchors, "defconfig mode arg anchor", MODE_SPECIFIC_ANCHORS["defconfig"])
        expect_anchor(issues, anchors, "savedefconfig mode arg anchor", MODE_SPECIFIC_ANCHORS["savedefconfig"])
    if syncconfig_nosilent_case_count > 0:
        expect_anchor(issues, anchors, "syncconfig nosilent packet", GENERAL_ANCHORS["syncconfig nosilentupdate"])
    if randconfig_override_case_count > 0:
        expect_anchor(issues, anchors, "randconfig allconfig override packet", MODE_SPECIFIC_ANCHORS["randconfig override"])
    if randconfig_plain_case_count > 0:
        expect_anchor(issues, anchors, "randconfig no-sentinel packet", MODE_SPECIFIC_ANCHORS["randconfig sentinel omission"])
    if allconfig_sentinel_case_count > 0:
        expect_anchor(issues, anchors, "allconfig sentinel packet", MODE_SPECIFIC_ANCHORS["allconfig sentinel"])
    if allconfig_override_case_count > 0:
        expect_anchor(issues, anchors, "allconfig explicit override packet", MODE_SPECIFIC_ANCHORS["allconfig explicit override"])

    expect_anchor(issues, anchors, "unexpected-option packet", GENERAL_ANCHORS["unexpected option rejection"])
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CONF_BRIDGE,
        """const std = @import("std");

pub const Mode = enum {
    oldaskconfig,
    syncconfig,
    oldconfig,
    allnoconfig,
    allyesconfig,
    allmodconfig,
    alldefconfig,
    randconfig,
    defconfig,
    savedefconfig,
    listnewconfig,
    helpnewconfig,
    olddefconfig,
    yes2modconfig,
    mod2yesconfig,
    mod2noconfig,
};

test "conf bridge mode surface stays aligned with conf.c long options" {
}
test "conf bridge emits silent flag before mode flag" {
}
test "mode argument validation rejects bridge option shaped defconfig payload" {
}
test "bridge options parser accepts syncconfig nosilentupdate" {
}
test "bridge options parser rejects unexpected options for mode" {
}
test "conf bridge emits defconfig mode argument before kconfig" {
}
test "conf bridge emits savedefconfig mode argument before kconfig" {
}
test "conf bridge emits explicit randconfig allconfig override when present" {
}
test "conf bridge omits randconfig allconfig sentinel without explicit override" {
}
test "conf bridge emits alldefconfig argv and env" {
}
test "conf bridge emits explicit empty allconfig override for allmodconfig" {
}
""",
    )
    write_text(
        root / CASES,
        json.dumps(
            {
                "conf_cases": [
                    {"mode": "oldaskconfig", "expected": "oldaskconfig_expected.json"},
                    {"mode": "syncconfig", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
                    {"mode": "oldconfig", "expected": "oldconfig_expected.json"},
                    {"mode": "allnoconfig", "expected": "allnoconfig_expected.json"},
                    {"mode": "allyesconfig", "expected": "allyesconfig_expected.json"},
                    {"mode": "allmodconfig", "allconfig": "", "expected": "allmodconfig_expected.json"},
                    {"mode": "alldefconfig", "expected": "alldefconfig_expected.json"},
                    {
                        "mode": "randconfig",
                        "allconfig": "allrandom.config",
                        "expected": "randconfig_expected.json",
                    },
                    {"mode": "defconfig", "mode_arg": "mini_defconfig", "expected": "defconfig_expected.json"},
                    {"mode": "savedefconfig", "mode_arg": "defconfig.out", "expected": "savedefconfig_expected.json"},
                    {"mode": "listnewconfig", "silent": true, "expected": "listnewconfig_expected.json"},
                    {"mode": "helpnewconfig", "silent": true, "expected": "helpnewconfig_expected.json"},
                    {"mode": "olddefconfig", "expected": "olddefconfig_expected.json"},
                    {"mode": "yes2modconfig", "expected": "yes2modconfig_expected.json"},
                    {"mode": "mod2yesconfig", "expected": "mod2yesconfig_expected.json"},
                    {"mode": "mod2noconfig", "expected": "mod2noconfig_expected.json"},
                ]
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_conf_helper_anchor_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        source = (root / CONF_BRIDGE).read_text(encoding="utf-8")
        source = source.replace(
            'test "conf bridge emits explicit randconfig allconfig override when present" {\n}\n',
            "",
            1,
        )
        (root / CONF_BRIDGE).write_text(source, encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("randconfig allconfig override packet:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        source = (root / CONF_BRIDGE).read_text(encoding="utf-8")
        source = source.replace(
            'test "conf bridge emits defconfig mode argument before kconfig" {\n}\n',
            "",
            1,
        )
        (root / CONF_BRIDGE).write_text(source, encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("defconfig mode arg anchor:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        source = (root / CONF_BRIDGE).read_text(encoding="utf-8")
        source = source.replace(
            'test "conf bridge emits silent flag before mode flag" {\n}\n',
            "",
            1,
        )
        (root / CONF_BRIDGE).write_text(source, encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("silent packet:") for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        cases = json.loads((root / CASES).read_text(encoding="utf-8"))
        cases["conf_cases"] = list(reversed(cases["conf_cases"]))
        (root / CASES).write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(issue.startswith("conf case modes drift from Mode enum:") for issue in issues)
        checks_run += 1

    print("PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_CONF_HELPER_ALIGNMENT=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CONF_HELPER_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
