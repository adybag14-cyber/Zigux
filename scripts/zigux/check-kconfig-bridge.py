#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
CASES_PATH = FIXTURE_DIR / "cases.json"

EXPECTED_SELF_TEST_CASE_COUNT = 8
REQUIRED_CONF_CASE_NAMES = ["olddefconfig", "syncconfig"]
REQUIRED_CONFDATA_CASE_NAMES = ["sample"]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("zig")
    if found:
        return found
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def compile_tool(zig: str, source: Path, output: Path) -> None:
    run([zig, "build-exe", str(source), "-femit-bin=" + str(output)], cwd=str(ROOT))


def load_cases(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    fixture_dir = root / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
    cases_path = fixture_dir / "cases.json"
    conf_bridge = root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
    confdata_bridge = root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
    issues: list[tuple[str, str]] = []

    if not conf_bridge.exists():
        issues.append(("MISSING_CONF_BRIDGE", str(conf_bridge.relative_to(root))))
    if not confdata_bridge.exists():
        issues.append(("MISSING_CONFDATA_BRIDGE", str(confdata_bridge.relative_to(root))))
    if not cases_path.exists():
        issues.append(("MISSING_CASES", str(cases_path.relative_to(root))))
        return issues

    payload = load_cases(cases_path)
    conf_cases = payload.get("conf_cases")
    confdata_cases = payload.get("confdata_cases")

    if not isinstance(conf_cases, list):
        issues.append(("INVALID_CONF_CASES", "conf_cases must be a list"))
        conf_cases = []
    if not isinstance(confdata_cases, list):
        issues.append(("INVALID_CONFDATA_CASES", "confdata_cases must be a list"))
        confdata_cases = []

    conf_names = [str(case.get("name", "")) for case in conf_cases]
    confdata_names = [str(case.get("name", "")) for case in confdata_cases]

    if conf_names != REQUIRED_CONF_CASE_NAMES:
        issues.append(("CONF_CASE_ORDER", ",".join(conf_names)))
        issues.append(("CONF_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONF_CASE_NAMES)))
    if confdata_names != REQUIRED_CONFDATA_CASE_NAMES:
        issues.append(("CONFDATA_CASE_ORDER", ",".join(confdata_names)))
        issues.append(("CONFDATA_CASE_ORDER_EXPECTED", ",".join(REQUIRED_CONFDATA_CASE_NAMES)))

    for case in conf_cases:
        name = str(case.get("name", ""))
        mode = str(case.get("mode", ""))
        if name != mode:
            issues.append(("NONCANONICAL_CONF_CASE", f"{name}:{mode}"))
        if name == "syncconfig" and case.get("nosilentupdate") != "1":
            issues.append(("SYNC_CONFIG_ENV_DRIFT", f"{name}:{case.get('nosilentupdate')!r}"))
        if name == "olddefconfig" and "mode_arg" in case:
            issues.append(("UNEXPECTED_CONF_MODE_ARG", name))
        expected = case.get("expected")
        if not isinstance(expected, str) or not expected:
            issues.append(("MISSING_CONF_EXPECTED", name))
        elif not (fixture_dir / expected).exists():
            issues.append(("MISSING_CONF_EXPECTED_PATH", expected))

    for case in confdata_cases:
        name = str(case.get("name", ""))
        input_path = case.get("input")
        expected = case.get("expected")
        if not isinstance(input_path, str) or not input_path:
            issues.append(("MISSING_CONFDATA_INPUT", name))
        elif not (fixture_dir / input_path).exists():
            issues.append(("MISSING_CONFDATA_INPUT_PATH", input_path))
        if not isinstance(expected, str) or not expected:
            issues.append(("MISSING_CONFDATA_EXPECTED", name))
        elif not (fixture_dir / expected).exists():
            issues.append(("MISSING_CONFDATA_EXPECTED_PATH", expected))

    return issues


def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    print("KCONFIG_BRIDGE_DIFF=fail")
    for block, value in issues:
        print(f"{block}={value}")
    raise SystemExit(1)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(root / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig", "pub fn main() void {}\n")
    write_text(root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig", "pub fn main() void {}\n")
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
                        "nosilentupdate": "1",
                        "expected": "syncconfig_expected.json",
                    },
                ],
                "confdata_cases": [
                    {
                        "name": "sample",
                        "input": "sample.config",
                        "expected": "sample_expected.json",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )
    for rel_path in (
        "olddefconfig_expected.json",
        "syncconfig_expected.json",
        "sample.config",
        "sample_expected.json",
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
        payload = load_cases(cases_path)
        payload["conf_cases"][0]["mode"] = "syncconfig"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("NONCANONICAL_CONF_CASE", "olddefconfig:syncconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = load_cases(cases_path)
        payload["conf_cases"].reverse()
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("CONF_CASE_ORDER", "syncconfig,olddefconfig") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = load_cases(cases_path)
        payload["conf_cases"][1]["nosilentupdate"] = "0"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("SYNC_CONFIG_ENV_DRIFT", "syncconfig:'0'") in issues
        checks_run += 1

        build_self_test_root(root)
        payload = load_cases(cases_path)
        payload["confdata_cases"][0]["input"] = "missing.config"
        write_text(cases_path, json.dumps(payload, indent=2) + "\n")
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONFDATA_INPUT_PATH", "missing.config") in issues
        checks_run += 1

        build_self_test_root(root)
        (root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "sample_expected.json").unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CONFDATA_EXPECTED_PATH", "sample_expected.json") in issues
        checks_run += 1

        build_self_test_root(root)
        (root / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig").unlink()
        issues = collect_manifest_issues(root)
        assert any(issue[0] == "MISSING_CONFDATA_BRIDGE" for issue in issues)
        checks_run += 1

        build_self_test_root(root)
        (root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json").unlink()
        issues = collect_manifest_issues(root)
        assert ("MISSING_CASES", "zigux/tests/fixtures/kconfig_bridge/cases.json") in issues
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
    parser = argparse.ArgumentParser(description="Check bounded kconfig bridge scaffold parity.")
    parser.add_argument("--zig", help="Explicit zig executable path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_manifest_issues(ROOT)
    if issues:
        emit_manifest_issues(issues)

    zig = find_zig(args.zig)
    cases = load_cases(CASES_PATH)

    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ("conf-bridge.exe" if sys.platform == "win32" else "conf-bridge")
        confdata_exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)

        for case in cases["conf_cases"]:
            actual = tmp_dir / f"{case['name']}.actual.json"
            cmd = [str(conf_exe), case["mode"], case["kconfig"], case["config"], case["arch"]]
            if "nosilentupdate" in case:
                cmd.append(f"nosilentupdate={case['nosilentupdate']}")
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
