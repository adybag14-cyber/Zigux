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

REQUIRED_CONF_HELPER_ANCHORS = [
    "conf bridge mode surface stays aligned with conf.c long options",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "conf bridge emits syncconfig nosilentupdate when present",
    "conf bridge omits empty syncconfig nosilentupdate",
    "conf bridge emits silent flag before mode flag",
    "conf bridge emits alldefconfig argv and env",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
    "conf bridge emits yes2modconfig argv and env",
    "conf bridge emits defconfig mode argument before kconfig",
    "conf bridge emits savedefconfig mode argument before kconfig",
    "conf bridge escapes low control bytes in JSON strings",
    "mode argument validation rejects bridge option shaped defconfig payload",
    "mode argument validation accepts defconfig path that only starts with silent",
    "mode argument validation still accepts ordinary path text with equals",
    "bridge options parser accepts explicit allconfig override for allmodconfig",
    "bridge options parser accepts syncconfig nosilentupdate",
    "bridge options parser keeps empty syncconfig nosilentupdate unset",
    "bridge options parser accepts generic silent flag",
    "bridge options parser accepts silent alongside randconfig options",
    "bridge options parser rejects duplicate silent flag",
    "bridge options parser rejects duplicate randconfig probability",
    "bridge options parser rejects unexpected options for mode",
    "bridge options parser keeps empty randconfig tunables unset",
    "bridge options parser rejects duplicate mode specific options",
]

REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES = [
    "allmodconfig",
    "randconfig",
]

REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES = [
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
]

REQUIRED_CONFDATA_HELPER_ANCHORS = [
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge decodes escaped quoted strings",
    "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
    "confdata bridge escapes low control bytes in json output",
    "confdata bridge accepts CRLF config lines",
    "confdata bridge preserves trailing carriage return on final unterminated value line",
    "confdata bridge ignores unterminated unset comment with trailing carriage return",
    "confdata bridge ignores suffix bytes after an embedded NUL",
    "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
    "confdata bridge keeps explicit n assignments as tristate values",
    "confdata bridge recognizes uppercase tristate assignments",
    "confdata bridge ignores non-CONFIG lines like upstream confdata",
    "confdata bridge ignores empty CONFIG symbol names",
    "confdata bridge ignores malformed unset comments with extra tokens",
    "confdata bridge keeps trailing escaped backslashes in quoted strings",
    "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
    "confdata bridge ignores malformed quoted values like upstream confdata",
    "confdata bridge emits no entries for empty CONFIG symbol names",
    "confdata bridge keeps only the last assignment for duplicate symbols",
    "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
    "confdata bridge emits the preserved duplicate state after later malformed quoted assignments",
    "confdata bridge keeps only the last state across unset and set transitions",
    "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
    "confdata bridge emits explicit empty assignments distinctly in json output",
    "confdata bridge escapes parsed string bytes in json output",
    "confdata bridge emits auto.conf symbol export lines",
    "confdata bridge emits autoconf header symbol export lines",
    "confdata bridge keeps explicit n out of autoconf header exports",
    "confdata bridge parses explicit output modes",
    "confdata bridge rejects unknown output modes",
    "confdata bridge emits auto.conf output through the explicit mode surface",
    "confdata bridge emits autoconf header output through the explicit mode surface",
    "confdata bridge file reader accepts config inputs beyond one mebibyte",
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
]

SAMPLE_CONF_CASES = [
    {"name": "oldaskconfig", "mode": "oldaskconfig", "kconfig": "Kconfig", "config": "ask/.config", "arch": "x86_64", "expected": "oldaskconfig_expected.json"},
    {"name": "syncconfig", "mode": "syncconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "riscv64", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
    {"name": "oldconfig", "mode": "oldconfig", "kconfig": "Kconfig", "config": "refresh/.config", "arch": "x86", "expected": "oldconfig_expected.json"},
    {"name": "allnoconfig", "mode": "allnoconfig", "kconfig": "Kconfig", "config": "none/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "allnoconfig_expected.json"},
    {"name": "allyesconfig", "mode": "allyesconfig", "kconfig": "Kconfig", "config": "yes/.config", "arch": "arm64", "expected": "allyesconfig_expected.json"},
    {"name": "allmodconfig", "mode": "allmodconfig", "kconfig": "Kconfig", "config": "mod/.config", "arch": "arm", "allconfig": "", "expected": "allmodconfig_expected.json"},
    {"name": "alldefconfig", "mode": "alldefconfig", "kconfig": "Kconfig", "config": "build/.config", "arch": "arm64", "allconfig": "mini-all.config", "expected": "alldefconfig_expected.json"},
    {"name": "randconfig", "mode": "randconfig", "kconfig": "Kconfig", "config": "rand/.config", "arch": "x86_64", "allconfig": "", "seed": "0xC0FFEE", "probability": "15:25", "expected": "randconfig_expected.json"},
    {"name": "defconfig", "mode": "defconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "arm64", "mode_arg": "arch/arm64/configs/defconfig", "expected": "defconfig_expected.json"},
    {"name": "savedefconfig", "mode": "savedefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "mode_arg": "silent=debug_defconfig", "expected": "savedefconfig_expected.json"},
    {"name": "listnewconfig", "mode": "listnewconfig", "kconfig": "Kconfig", "config": "out/list.config", "arch": "x86_64", "silent": True, "expected": "listnewconfig_expected.json"},
    {"name": "helpnewconfig", "mode": "helpnewconfig", "kconfig": "Kconfig", "config": "out/help.config", "arch": "riscv64", "silent": True, "expected": "helpnewconfig_expected.json"},
    {"name": "olddefconfig", "mode": "olddefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "expected": "olddefconfig_expected.json"},
    {"name": "yes2modconfig", "mode": "yes2modconfig", "kconfig": "Kconfig", "config": "rewrite/.config", "arch": "x86", "expected": "yes2modconfig_expected.json"},
    {"name": "mod2yesconfig", "mode": "mod2yesconfig", "kconfig": "Kconfig", "config": "promote/.config", "arch": "x86", "expected": "mod2yesconfig_expected.json"},
    {"name": "mod2noconfig", "mode": "mod2noconfig", "kconfig": "Kconfig", "config": "demote/.config", "arch": "x86", "expected": "mod2noconfig_expected.json"},
]

SAMPLE_CONFDATA_CASES = [
    {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
    {"name": "escaped_strings", "input": "escaped_strings.config", "expected": "escaped_strings_expected.json"},
    {"name": "escaped_control_sequences", "input": "escaped_control_sequences.config", "expected": "escaped_control_sequences_expected.json"},
    {"name": "trailing_escaped_backslash", "input": "trailing_escaped_backslash.config", "expected": "trailing_escaped_backslash_expected.json"},
    {"name": "sample_crlf", "input": "sample_crlf.config", "expected": "sample_crlf_expected.json"},
    {"name": "explicit_n_tristate", "input": "explicit_n_tristate.config", "expected": "explicit_n_tristate_expected.json"},
    {"name": "final_trailing_carriage_return", "input": "final_trailing_carriage_return.config", "expected": "final_trailing_carriage_return_expected.json"},
    {"name": "final_unterminated_unset_comment", "input": "final_unterminated_unset_comment.config", "expected": "final_unterminated_unset_comment_expected.json"},
    {"name": "uppercase_tristate", "input": "uppercase_tristate.config", "expected": "uppercase_tristate_expected.json"},
    {"name": "non_config_lines", "input": "non_config_lines.config", "expected": "non_config_lines_expected.json"},
    {"name": "empty_config_symbol_names", "input": "empty_config_symbol_names.config", "expected": "empty_config_symbol_names_expected.json"},
    {"name": "malformed_unset_comment_tokens", "input": "malformed_unset_comment_tokens.config", "expected": "malformed_unset_comment_tokens_expected.json"},
    {"name": "last_state_transitions", "input": "last_state_transitions.config", "expected": "last_state_transitions_expected.json"},
    {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
    {"name": "duplicate_malformed_quoted_assignment", "input": "duplicate_malformed_quoted_assignment.config", "expected": "duplicate_malformed_quoted_assignment_expected.json"},
    {"name": "explicit_empty_assignments", "input": "explicit_empty_assignments.config", "expected": "explicit_empty_assignments_expected.json"},
]

ALLCONFIG_SENTINEL_MODES = {"allnoconfig", "allyesconfig", "alldefconfig"}
EXPECTED_SELF_TEST_CASE_COUNT = 6


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


def ordered_test_anchors(path: Path) -> list[str]:
    return re.findall(r'^test "([^"]+)" \{$', path.read_text(encoding="utf-8"), re.M)


def validate_case_mapping(raw_cases: list[object], *, group_name: str) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for case in raw_cases:
        if not isinstance(case, dict):
            raise SystemExit(f"invalid case entry in {group_name}")
        if group_name == "conf_cases" and "silent" in case and not isinstance(case["silent"], bool):
            raise SystemExit("invalid conf case silent field")
        if "silent" in case and case["silent"] is not True:
            raise SystemExit("invalid silent flag shape")
        normalized.append(case)
    return normalized


def build_conf_command(case: dict[str, object]) -> list[str]:
    cmd = [str(case["mode"]), str(case["kconfig"]), str(case["config"]), str(case["arch"])]
    if case.get("silent"):
        cmd.append("silent")
    if "mode_arg" in case:
        cmd.append(str(case["mode_arg"]))
    if "allconfig" in case:
        cmd.append(f"allconfig={case['allconfig']}")
    if "seed" in case:
        cmd.append(f"seed={case['seed']}")
    if "probability" in case:
        cmd.append(f"probability={case['probability']}")
    if "nosilentupdate" in case:
        cmd.append(f"nosilentupdate={case['nosilentupdate']}")
    return cmd


def build_conf_manifest(conf_cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/conf_bridge.zig",
        "status": "closed",
        "mode": "bounded request-plan bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(conf_cases),
        "cases": [str(case["name"]) for case in conf_cases],
        "stdout_packet": [str(case["expected"]) for case in conf_cases],
        "mode_arg_cases": [str(case["name"]) for case in conf_cases if "mode_arg" in case],
        "silent_request_packet": [str(case["expected"]) for case in conf_cases if case.get("silent") is True],
        "syncconfig_env_packet": [str(case["expected"]) for case in conf_cases if "nosilentupdate" in case],
        "allconfig_sentinel_packet": [str(case["expected"]) for case in conf_cases if str(case["mode"]) in ALLCONFIG_SENTINEL_MODES],
        "allconfig_override_packet": [str(case["expected"]) for case in conf_cases if "allconfig" in case],
        "helper_local_allconfig_implicit_omission_modes": REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES,
        "helper_local_allconfig_explicit_override_modes": REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES,
        "randconfig_env_packet": [str(case["expected"]) for case in conf_cases if "seed" in case or "probability" in case],
        "helper_local_anchors": REQUIRED_CONF_HELPER_ANCHORS,
    }


def build_confdata_manifest(confdata_cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(confdata_cases),
        "cases": [str(case["name"]) for case in confdata_cases],
        "input_packet": [str(case["input"]) for case in confdata_cases],
        "expected_packet": [str(case["expected"]) for case in confdata_cases],
        "helper_local_anchors": REQUIRED_CONFDATA_HELPER_ANCHORS,
    }


def load_case_groups(fixture_dir: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    payload = json.loads((fixture_dir / "cases.json").read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("INVALID_CASES_PAYLOAD")
    conf_cases = validate_case_mapping(payload.get("conf_cases", []), group_name="conf_cases")
    confdata_cases = validate_case_mapping(payload.get("confdata_cases", []), group_name="confdata_cases")
    return conf_cases, confdata_cases


def collect_manifest_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    fixture_dir = root / FIXTURE_DIR.relative_to(ROOT)
    conf_cases, confdata_cases = load_case_groups(fixture_dir)
    if conf_cases != SAMPLE_CONF_CASES:
        issues.append(("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
    if confdata_cases != SAMPLE_CONFDATA_CASES:
        issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))
    if ordered_test_anchors(root / CONF_BRIDGE.relative_to(ROOT)) != REQUIRED_CONF_HELPER_ANCHORS:
        issues.append(("CONF_SOURCE_HELPER_LOCAL_ANCHORS_MISMATCH", "conf_bridge.zig"))
    if ordered_test_anchors(root / CONFDATA_BRIDGE.relative_to(ROOT)) != REQUIRED_CONFDATA_HELPER_ANCHORS:
        issues.append(("CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_MISMATCH", "confdata_bridge.zig"))
    conf_manifest = json.loads((fixture_dir / "conf_manifest.json").read_text(encoding="utf-8"))
    confdata_manifest = json.loads((fixture_dir / "confdata_manifest.json").read_text(encoding="utf-8"))
    if conf_manifest != build_conf_manifest(conf_cases):
        issues.append(("CONF_MANIFEST_MISMATCH", "conf_manifest.json"))
    if confdata_manifest != build_confdata_manifest(confdata_cases):
        issues.append(("CONFDATA_MANIFEST_MISMATCH", "confdata_manifest.json"))
    for case in conf_cases:
        if not (fixture_dir / str(case["expected"])).exists():
            issues.append(("MISSING_CONF_FIXTURE", str(case["expected"])))
    for case in confdata_cases:
        for field in ("input", "expected"):
            if not (fixture_dir / str(case[field])).exists():
                issues.append(("MISSING_CONFDATA_FIXTURE", str(case[field])))
    return issues


def emit_manifest_issues(issues: list[tuple[str, str]]) -> None:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("KCONFIG_BRIDGE_DIFF=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    raise SystemExit(1)


def check_repeatable_json_output(expected: Path, actual: Path, repeat: Path) -> None:
    run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(actual)], cwd=str(ROOT))
    run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(actual), str(repeat)], cwd=str(ROOT))


def build_self_test_root(root: Path) -> None:
    fixture_root = root / FIXTURE_DIR.relative_to(ROOT)
    (root / CONF_BRIDGE.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
    (root / CONFDATA_BRIDGE.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
    (root / FIXTURE_DIR.relative_to(ROOT)).mkdir(parents=True, exist_ok=True)
    (root / ARTIFACT_DIFF.relative_to(ROOT)).parent.mkdir(parents=True, exist_ok=True)
    (root / ARTIFACT_DIFF.relative_to(ROOT)).write_text("import sys\n", encoding="utf-8")
    (root / CONF_BRIDGE.relative_to(ROOT)).write_text("\n".join(f'test \"{anchor}\" {{}}' for anchor in REQUIRED_CONF_HELPER_ANCHORS) + "\n", encoding="utf-8")
    (root / CONFDATA_BRIDGE.relative_to(ROOT)).write_text("\n".join(f'test \"{anchor}\" {{}}' for anchor in REQUIRED_CONFDATA_HELPER_ANCHORS) + "\n", encoding="utf-8")
    (fixture_root / "cases.json").write_text(json.dumps({"conf_cases": SAMPLE_CONF_CASES, "confdata_cases": SAMPLE_CONFDATA_CASES}, indent=2) + "\n", encoding="utf-8")
    (fixture_root / "conf_manifest.json").write_text(json.dumps(build_conf_manifest(SAMPLE_CONF_CASES), indent=2) + "\n", encoding="utf-8")
    (fixture_root / "confdata_manifest.json").write_text(json.dumps(build_confdata_manifest(SAMPLE_CONFDATA_CASES), indent=2) + "\n", encoding="utf-8")
    for case in SAMPLE_CONF_CASES:
        (fixture_root / str(case["expected"])).write_text("{}\n", encoding="utf-8")
    for case in SAMPLE_CONFDATA_CASES:
        (fixture_root / str(case["input"])).write_text("# fixture\n", encoding="utf-8")
        (fixture_root / str(case["expected"])).write_text("{}\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_selftest_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_manifest_issues(root) == []
        checks_run += 1
        build_self_test_root(root)
        (root / FIXTURE_DIR.relative_to(ROOT) / "cases.json").write_text("[]\n", encoding="utf-8")
        assert collect_manifest_issues(root)[0][0] == "INVALID_CASES_PAYLOAD"
        checks_run += 1
        build_self_test_root(root)
        (root / CONFDATA_BRIDGE.relative_to(ROOT)).write_text("test \"wrong\" {}\n", encoding="utf-8")
        assert any(code == "CONFDATA_SOURCE_HELPER_LOCAL_ANCHORS_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / FIXTURE_DIR.relative_to(ROOT) / "confdata_manifest.json").write_text("{}\n", encoding="utf-8")
        assert any(code == "CONFDATA_MANIFEST_MISMATCH" for code, _ in collect_manifest_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / FIXTURE_DIR.relative_to(ROOT) / str(SAMPLE_CONFDATA_CASES[0]["input"])).unlink()
        assert any(code == "MISSING_CONFDATA_FIXTURE" for code, _ in collect_manifest_issues(root))
        checks_run += 1
        build_self_test_root(root)
        (root / FIXTURE_DIR.relative_to(ROOT) / str(SAMPLE_CONF_CASES[0]["expected"])).unlink()
        assert any(code == "MISSING_CONF_FIXTURE" for code, _ in collect_manifest_issues(root))
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
    parser.add_argument("--self-test", action="store_true", help="Run built-in manifest coverage without compiling the bridge tools.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_manifest_issues(ROOT)
    if issues:
        emit_manifest_issues(issues)
    zig = find_zig(args.zig)
    conf_cases, confdata_cases = load_case_groups(FIXTURE_DIR)
    with tempfile.TemporaryDirectory(prefix="zigux_kconfig_bridge_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        conf_exe = tmp_dir / ("conf-bridge.exe" if sys.platform == "win32" else "conf-bridge")
        confdata_exe = tmp_dir / ("confdata-bridge.exe" if sys.platform == "win32" else "confdata-bridge")
        compile_tool(zig, CONF_BRIDGE, conf_exe)
        compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)
        for case in conf_cases:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            cmd = [str(conf_exe), *build_conf_command(case)]
            actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            check_repeatable_json_output(FIXTURE_DIR / str(case["expected"]), actual, repeat)
        for case in confdata_cases:
            actual = tmp_dir / f"{case['name']}.actual.json"
            repeat = tmp_dir / f"{case['name']}.repeat.json"
            cmd = [str(confdata_exe), str(FIXTURE_DIR / str(case["input"]))]
            actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\n")
            check_repeatable_json_output(FIXTURE_DIR / str(case["expected"]), actual, repeat)
    print("KCONFIG_BRIDGE_DETERMINISM=pass")
    print("KCONFIG_BRIDGE_DIFF=pass")
    print(f"FIXTURE_DIR={FIXTURE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
