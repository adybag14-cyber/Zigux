#!/usr/bin/env python3
"""Guard the Phase 2 conf_bridge helper-anchor and allconfig packet contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONF_BRIDGE = Path("scripts/zigux/kconfig/conf_bridge.zig")
CASES = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")
MANIFEST = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")

HELPER_PREFIXES = (
    "conf bridge ",
    "bridge options parser ",
    "mode argument validation ",
)
MODE_ARG_MODES = ("defconfig", "savedefconfig")
SILENT_REQUEST_CASES = ("helpnewconfig_expected.json",)
SYNCCONFIG_ENV_CASES = ("syncconfig_expected.json",)
ALLCONFIG_SENTINEL_MODES = {
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
}

TEST_PATTERN = re.compile(r'^test "([^"]+)" \{$')


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


def collect_helper_anchors(source: str) -> list[str]:
    anchors: list[str] = []
    for line in source.splitlines():
        match = TEST_PATTERN.match(line.strip())
        if not match:
            continue
        test_name = match.group(1)
        if test_name.startswith(HELPER_PREFIXES):
            anchors.append(test_name)
    return anchors


def expected_stdout_packet(cases: list[dict[str, object]]) -> list[str]:
    return [str(case["expected"]) for case in cases]


def expected_case_modes(cases: list[dict[str, object]]) -> list[str]:
    return [str(case["mode"]) for case in cases]


def expected_mode_arg_cases(cases: list[dict[str, object]]) -> list[str]:
    return [str(case["mode"]) for case in cases if case["mode"] in MODE_ARG_MODES]


def expected_allconfig_sentinel_packet(cases: list[dict[str, object]]) -> list[str]:
    packet: list[str] = []
    for case in cases:
        if case["mode"] in ALLCONFIG_SENTINEL_MODES and "allconfig" not in case:
            packet.append(str(case["expected"]))
    return packet


def expected_allconfig_override_packet(cases: list[dict[str, object]]) -> list[str]:
    return [str(case["expected"]) for case in cases if "allconfig" in case]


def expect_equal(issues: list[str], key: str, actual: object, expected: object) -> None:
    if actual != expected:
        issues.append(f"{key}: expected {expected!r}, got {actual!r}")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    manifest = read_json(root, MANIFEST)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST.as_posix()}: expected object root"]
    cases = read_json(root, CASES)
    if not isinstance(cases, list):
        return [f"{CASES.as_posix()}: expected array root"]

    typed_cases: list[dict[str, object]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(f"{CASES.as_posix()}[{index}]: expected object case")
            continue
        typed_cases.append(case)

    source = read_text(root, CONF_BRIDGE)
    helper_anchors = collect_helper_anchors(source)

    expect_equal(issues, "tool", manifest.get("tool"), "scripts/zigux/kconfig/conf_bridge.zig")
    expect_equal(issues, "fixture_case_source", manifest.get("fixture_case_source"), CASES.as_posix())
    expect_equal(issues, "case_count", manifest.get("case_count"), len(typed_cases))
    expect_equal(issues, "cases", manifest.get("cases"), expected_case_modes(typed_cases))
    expect_equal(issues, "stdout_packet", manifest.get("stdout_packet"), expected_stdout_packet(typed_cases))
    expect_equal(issues, "mode_arg_cases", manifest.get("mode_arg_cases"), list(expected_mode_arg_cases(typed_cases)))
    expect_equal(issues, "silent_request_packet", manifest.get("silent_request_packet"), list(SILENT_REQUEST_CASES))
    expect_equal(issues, "syncconfig_env_packet", manifest.get("syncconfig_env_packet"), list(SYNCCONFIG_ENV_CASES))
    expect_equal(
        issues,
        "allconfig_sentinel_packet",
        manifest.get("allconfig_sentinel_packet"),
        expected_allconfig_sentinel_packet(typed_cases),
    )
    expect_equal(
        issues,
        "allconfig_override_packet",
        manifest.get("allconfig_override_packet"),
        expected_allconfig_override_packet(typed_cases),
    )
    expect_equal(issues, "helper_local_anchors", manifest.get("helper_local_anchors"), helper_anchors)
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / CONF_BRIDGE,
        "\n".join(
            (
                'test "conf bridge emits syncconfig auto files" {',
                "}",
                'test "conf bridge emits explicit empty allconfig override for allmodconfig" {',
                "}",
                'test "mode argument validation rejects bridge option shaped defconfig payload" {',
                "}",
                'test "bridge options parser accepts syncconfig nosilentupdate" {',
                "}",
                'test "bridge options parser rejects unexpected options for mode" {',
                "}",
                'test "helper outside scope is ignored" {',
                "}",
            )
        )
        + "\n",
    )
    cases = [
        {
            "mode": "syncconfig",
            "expected": "syncconfig_expected.json",
        },
        {
            "mode": "allmodconfig",
            "expected": "allmodconfig_expected.json",
        },
        {
            "mode": "randconfig",
            "expected": "randconfig_expected.json",
            "allconfig": "allrandom.config",
        },
        {
            "mode": "defconfig",
            "expected": "defconfig_expected.json",
            "mode_arg": "arch/x86/configs/tiny_defconfig",
        },
    ]
    write_text(root / CASES, json.dumps(cases, indent=2) + "\n")
    manifest = {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": 4,
        "cases": ["syncconfig", "allmodconfig", "randconfig", "defconfig"],
        "stdout_packet": [
            "syncconfig_expected.json",
            "allmodconfig_expected.json",
            "randconfig_expected.json",
            "defconfig_expected.json",
        ],
        "mode_arg_cases": ["defconfig"],
        "silent_request_packet": ["helpnewconfig_expected.json"],
        "syncconfig_env_packet": ["syncconfig_expected.json"],
        "allconfig_sentinel_packet": ["allmodconfig_expected.json"],
        "allconfig_override_packet": ["randconfig_expected.json"],
        "helper_local_anchors": [
            "conf bridge emits syncconfig auto files",
            "conf bridge emits explicit empty allconfig override for allmodconfig",
            "mode argument validation rejects bridge option shaped defconfig payload",
            "bridge options parser accepts syncconfig nosilentupdate",
            "bridge options parser rejects unexpected options for mode",
        ],
    }
    write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase2-conf-helper-alignment-") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        cases += 1

        build_self_test_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["allconfig_sentinel_packet"] = []  # type: ignore[index]
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(issue.startswith("allconfig_sentinel_packet:") for issue in issues)
        cases += 1

        build_self_test_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["helper_local_anchors"] = manifest["helper_local_anchors"][:-1]  # type: ignore[index]
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(issue.startswith("helper_local_anchors:") for issue in issues)
        cases += 1

        build_self_test_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["case_count"] = 3  # type: ignore[index]
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(issue.startswith("case_count:") for issue in issues)
        cases += 1

    print("PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CONF_HELPER_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.self_test:
        return run_self_test()

    issues = collect_issues(root)
    if issues:
        print("PHASE2_CONF_HELPER_ALIGNMENT=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_CONF_HELPER_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
