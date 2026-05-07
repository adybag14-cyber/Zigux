#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
REQUIRED_CONFDATA_CASES = [
    "sample",
    "escaped_strings",
    "escaped_control_sequences",
    "trailing_escaped_backslash",
    "sample_crlf",
    "explicit_n_tristate",
    "final_trailing_carriage_return",
    "final_unterminated_unset_comment",
    "uppercase_tristate",
    "non_config_lines",
]
REQUIRED_CONF_CASE_MODES = [
    "olddefconfig",
    "syncconfig",
    "alldefconfig",
    "allmodconfig",
    "randconfig",
    "yes2modconfig",
    "mod2yesconfig",
    "mod2noconfig",
    "defconfig",
    "savedefconfig",
    "listnewconfig",
]
EXPECTED_SELF_TEST_CASE_COUNT = 11


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = shutil.which("zig")
    if env:
        return env
    fallback = ROOT.parent / "toolchains" / "zig-master" / "current" / "zig.exe"
    if fallback.exists():
        return str(fallback)
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def compile_tool(zig: str, source: Path, output: Path) -> None:
    run([zig, "build-exe", str(source), "-femit-bin=" + str(output)], cwd=str(ROOT))


def load_cases(fixture_dir: Path) -> dict[str, object]:
    return json.loads((fixture_dir / "cases.json").read_text(encoding="utf-8"))


def ordered_conf_modes(conf_bridge_path: Path) -> list[str]:
    source = conf_bridge_path.read_text(encoding="utf-8")
    match = re.search(r"pub const Mode = enum \{(.*?)\n\s*pub fn parse", source, re.S)
    if not match:
        raise SystemExit("failed to parse conf bridge Mode enum")

    modes: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("pub ") or line.startswith("//"):
            continue
        if line.endswith(","):
            candidate = line[:-1].strip()
            if candidate and candidate.isidentifier():
                modes.append(candidate)
    if not modes:
        raise SystemExit("failed to discover conf bridge modes")
    return modes


def expected_conf_case_order(conf_cases: list[dict[str, object]]) -> list[str]:
    manifest_mode_set = {str(case["mode"]) for case in conf_cases}
    return [mode for mode in REQUIRED_CONF_CASE_MODES if mode in manifest_mode_set]


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    conf_bridge = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
    cases = load_cases(fixture_dir)
    issues: list[tuple[str, str]] = []

    conf_cases = cases["conf_cases"]
    bridge_modes = ordered_conf_modes(conf_bridge)
    bridge_mode_set = set(bridge_modes)
    manifest_modes = {case["mode"] for case in conf_cases}
    for mode in sorted(manifest_modes - bridge_mode_set):
        issues.append(("UNSUPPORTED_CONF_CASE_MODES", mode))

    manifest_mode_order = [str(case["mode"]) for case in conf_cases]
    expected_mode_order = expected_conf_case_order(conf_cases)
    if manifest_mode_order != expected_mode_order:
        issues.append(("CONF_CASE_MODE_ORDER_ACTUAL", ",".join(manifest_mode_order)))
        issues.append(("CONF_CASE_MODE_ORDER_EXPECTED", ",".join(expected_mode_order)))

    manifest_confdata_case_order = [str(case["name"]) for case in cases["confdata_cases"]]
    if manifest_confdata_case_order != REQUIRED_CONFDATA_CASES:
        issues.append(("CONFDATA_CASE_ORDER_ACTUAL", ",".join(manifest_confdata_case_order)))
        issues.append(("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASES)))

    seen_names: dict[str, str] = {}
    for group_name in ("conf_cases", "confdata_cases"):
        for case in cases[group_name]:
            name = case["name"]
            previous_group = seen_names.get(name)
            if previous_group is not None:
                issues.append(("DUPLICATE_KCONFIG_CASE_NAMES", f"{name}:{previous_group},{group_name}"))
                continue
            seen_names[name] = group_name

    for case in conf_cases:
        mode = str(case["mode"])
        name = str(case["name"])
        mode_arg = case.get("mode_arg")
        if mode in ("defconfig", "savedefconfig"):
            if not isinstance(mode_arg, str) or not mode_arg:
                issues.append(("MISSING_CONF_MODE_ARG_FIELDS", f"{name}:{mode}"))
        elif "mode_arg" in case:
            issues.append(("UNEXPECTED_CONF_MODE_ARG_FIELDS", f"{name}:{mode}"))

        if mode != "randconfig":
            for field_name in ("seed", "probability"):
                if field_name in case:
                    issues.append(("INVALID_CONF_CASE_RANDCONFIG_FIELDS", f"{name}:{field_name}"))
        rel_path = case["expected"]
        if not (fixture_dir / rel_path).exists():
            issues.append(("MISSING_CONF_CASE_EXPECTED_PATHS", f"{name}:expected:{rel_path}"))

    for case in cases["confdata_cases"]:
        for field_name in ("input", "expected"):
            rel_path = case[field_name]
            if not (fixture_dir / rel_path).exists():
                issues.append(("MISSING_CONFDATA_CASE_PATHS", f"{case['name']}:{field_name}:{rel_path}"))

    return issues


def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("KCONFIG_BRIDGE_DIFF=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    raise SystemExit(1)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
        """const std = @import(\"std\");

pub const Mode = enum {
    olddefconfig,
    syncconfig,
    randconfig,
    defconfig,
    savedefconfig,
    listnewconfig,

    pub fn parse(input_text: []const u8) ?Mode {
        _ = input_text;
        return null;
    }
};
""",
    )
    write_text(
        root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
        'const std = @import("std");\n',
    )
    write_text(
        root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
        json.dumps(
            {
                "conf_cases": [
                    {
                        "name": "olddefconfig",
                        "mode": "olddefconfig",
                        "kconfig": "Kconfig",
                        "config": ".config",
                        "arch": "x86_64",
                        "expected": "olddefconfig_expected.json",
                    },
                    {
                        "name": "syncconfig",
                        "mode": "syncconfig",
                        "kconfig": "Kconfig",
                        "config": "out/.config",
                        "arch": "riscv64",
                        "expected": "syncconfig_expected.json",
                    },
                    {
                        "name": "randconfig",
                        "mode": "randconfig",
                        "kconfig": "Kconfig",
                        "config": "rand/.config",
                        "arch": "x86_64",
                        "seed": "0xC0FFEE",
                        "probability": "15:25",
                        "expected": "randconfig_expected.json",
                    },
                    {
                        "name": "defconfig",
                        "mode": "defconfig",
                        "kconfig": "Kconfig",
                        "config": "out/.config",
                        "arch": "arm64",
                        "mode_arg": "arch/arm64/configs/defconfig",
                        "expected": "defconfig_expected.json",
                    },
                    {
                        "name": "savedefconfig",
                        "mode": "savedefconfig",
                        "kconfig": "Kconfig",
                        "config": ".config",
                        "arch": "x86_64",
                        "mode_arg": "defconfig.out",
                        "expected": "savedefconfig_expected.json",
                    },
                    {
                        "name": "listnewconfig",
                        "mode": "listnewconfig",
                        "kconfig": "Kconfig",
                        "config": "out/list.config",
                        "arch": "x86_64",
                        "expected": "listnewconfig_expected.json",
                    },
                ],
                "confdata_cases": [
                    {
                        "name": "sample",
                        "input": "sample.config",
                        "expected": "sample_expected.json",
                    },
                    {
                        "name": "escaped_strings",
                        "input": "escaped_strings.config",
                        "expected": "escaped_strings_expected.json",
                    },
                    {
                        "name": "escaped_control_sequences",
                        "input": "escaped_control_sequences.config",
                        "expected": "escaped_control_sequences_expected.json",
                    },
                    {
                        "name": "trailing_escaped_backslash",
                        "input": "trailing_escaped_backslash.config",
                        "expected": "trailing_escaped_backslash_expected.json",
                    },
                    {
                        "name": "sample_crlf",
                        "input": "sample_crlf.config",
                        "expected": "sample_crlf_expected.json",
                    },
                    {
                        "name": "explicit_n_tristate",
                        "input": "explicit_n_tristate.config",
                        "expected": "explicit_n_tristate_expected.json",
                    },
                    {
                        "name": "final_trailing_carriage_return",
                        "input": "final_trailing_carriage_return.config",
                        "expected": "final_trailing_carriage_return_expected.json",
                    },
                    {
                        "name": "final_unterminated_unset_comment",
                        "input": "final_unterminated_unset_comment.config",
                        "expected": "final_unterminated_unset_comment_expected.json",
                    },
                    {
                        "name": "uppercase_tristate",
                        "input": "uppercase_tristate.config",
                        "expected": "uppercase_tristate_expected.json",
                    },
                    {
                        "name": "non_config_lines",
                        "input": "non_config_lines.config",
                        "expected": "non_config_lines_expected.json",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in (
        "olddefconfig_expected.json",
        "syncconfig_expected.json",
        "randconfig_expected.json",
        "defconfig_expected.json",
        "savedefconfig_expected.json",
        "listnewconfig_expected.json",
        "sample_expected.json",
        "escaped_strings_expected.json",
        "escaped_control_sequences_expected.json",
        "trailing_escaped_backslash_expected.json",
        "sample_crlf_expected.json",
        "explicit_n_tristate_expected.json",
        "final_trailing_carriage_return_expected.json",
        "final_unterminated_unset_comment_expected.json",
        "uppercase_tristate_expected.json",
        "non_config_lines_expected.json",
        "sample.config",
        "escaped_strings.config",
        "escaped_control_sequences.config",
        "trailing_escaped_backslash.config",
        "sample_crlf.config",
        "explicit_n_tristate.config",
        "final_trailing_carriage_return.config",
        "final_unterminated_unset_comment.config",
        "uppercase_tristate.config",
        "non_config_lines.config",
    ):
        write_text(root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / rel_path, "{}\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_selftest_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        cases_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"

        build_self_test_root(root)
        assert collect_manifest_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["mode"] = "oldconfig"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("UNSUPPORTED_CONF_CASE_MODES", "oldconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][1], payload["conf_cases"][3] = payload["conf_cases"][3], payload["conf_cases"][1]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert (
            "CONF_CASE_MODE_ORDER_ACTUAL",
            "olddefconfig,defconfig,randconfig,syncconfig,savedefconfig,listnewconfig",
        ) in issues
        assert (
            "CONF_CASE_MODE_ORDER_EXPECTED",
            "olddefconfig,syncconfig,randconfig,defconfig,savedefconfig,listnewconfig",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][1]["mode_arg"] = "unexpected"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("UNEXPECTED_CONF_MODE_ARG_FIELDS", "syncconfig:syncconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        del payload["conf_cases"][3]["mode_arg"]
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONF_MODE_ARG_FIELDS", "defconfig:defconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["conf_cases"][0]["seed"] = "0xBAD"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("INVALID_CONF_CASE_RANDCONFIG_FIELDS", "olddefconfig:seed") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["name"] = "syncconfig"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("DUPLICATE_KCONFIG_CASE_NAMES", "syncconfig:conf_cases,confdata_cases") in issues
        checks_run += 1

        build_self_test_root(root)
        missing_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "listnewconfig_expected.json"
        missing_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONF_CASE_EXPECTED_PATHS", "listnewconfig:expected:listnewconfig_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        missing_path = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "sample_crlf_expected.json"
        missing_path.unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONFDATA_CASE_PATHS", "sample_crlf:expected:sample_crlf_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"].pop()
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert (
            "CONFDATA_CASE_ORDER_ACTUAL",
            ",".join(REQUIRED_CONFDATA_CASES[:-1]),
        ) in issues
        assert (
            "CONFDATA_CASE_ORDER_EXPECTED",
            ",".join(REQUIRED_CONFDATA_CASES),
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(cases_path.read_text(encoding="utf-8"))
        payload["confdata_cases"][1], payload["confdata_cases"][2] = (
            payload["confdata_cases"][2],
            payload["confdata_cases"][1],
        )
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert (
            "CONFDATA_CASE_ORDER_ACTUAL",
            "sample,escaped_control_sequences,escaped_strings,trailing_escaped_backslash,sample_crlf,explicit_n_tristate,final_trailing_carriage_return,final_unterminated_unset_comment,uppercase_tristate,non_config_lines",
        ) in issues
        assert (
            "CONFDATA_CASE_ORDER_EXPECTED",
            ",".join(REQUIRED_CONFDATA_CASES),
        ) in issues
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        print("KCONFIG_BRIDGE_SELF_TEST=fail")
        print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT_ACTUAL={checks_run}")
        print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("KCONFIG_BRIDGE_SELF_TEST=pass")
    print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded kconfig bridge fixture parity.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in manifest coverage without compiling the bridge tools.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_manifest_issues(ROOT)
    if issues:
        emit_manifest_issues(issues)

    zig = find_zig(args.zig)
    cases = load_cases(FIXTURE_DIR)

    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ("conf-bridge.exe" if sys.platform == "win32" else "conf-bridge")
        confdata_exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)

        for case in cases["conf_cases"]:
            actual = tmp_dir / f"{case['name']}.actual.json"
            cmd = [
                str(conf_exe),
                case["mode"],
                case["kconfig"],
                case["config"],
                case["arch"],
            ]
            if "mode_arg" in case:
                cmd.append(case["mode_arg"])
            if "seed" in case:
                cmd.append(f"seed={case['seed']}")
            if "probability" in case:
                cmd.append(f"probability={case['probability']}")
            result = run(cmd, cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding="utf-8", newline="\n")
            run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(FIXTURE_DIR / case["expected"]), str(actual)], cwd=str(ROOT))

        for case in cases["confdata_cases"]:
            actual = tmp_dir / f"{case['name']}.actual.json"
            result = run([str(confdata_exe), str(FIXTURE_DIR / case["input"])], cwd=str(ROOT), capture_output=True)
            actual.write_text(result.stdout, encoding="utf-8", newline="\n")
            run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(FIXTURE_DIR / case["expected"]), str(actual)], cwd=str(ROOT))

    print("KCONFIG_BRIDGE_DIFF=pass")
    print(f"FIXTURE_DIR={FIXTURE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
