#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
KCONFIG_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"

EXPECTED_CONF_CASE_ORDER = [
    "oldaskconfig",
    "oldconfig",
    "syncconfig",
    "defconfig",
    "savedefconfig",
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
    "listnewconfig",
    "helpnewconfig",
    "olddefconfig",
    "yes2modconfig",
    "mod2yesconfig",
    "mod2noconfig",
]

EXPECTED_CONFDATA_CASE_ORDER = [
    "duplicate_assignments",
    "empty_string",
    "empty_symbol_names",
    "escaped_control_sequences",
    "escaped_low_control_bytes",
    "escaped_strings",
    "explicit_n_tristate",
    "final_trailing_carriage_return",
    "final_unterminated_unset_comment",
    "ignore_non_config_lines",
    "malformed_quoted_string",
    "negative_signed_numeric_kinds",
    "numeric_kinds",
    "quoted_suffix_bytes",
    "sample",
    "sample_crlf",
    "signed_numeric_kinds",
    "trailing_escaped_backslash",
]

EXPECTED_WORKFLOW_RUN_COUNTS = {
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py": 1,
    "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
}

KCONFIG_CHECKER_MARKERS = [
    "parser.add_argument('--self-test'",
    "print('KCONFIG_BRIDGE_SELF_TEST=pass')",
    "print(f'KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={total_self_test_cases}')",
    "print('KCONFIG_BRIDGE_DETERMINISM=pass')",
    "UNSORTED_CONF_CASE_ORDER_START",
    "UNSORTED_CONFDATA_CASE_ORDER_START",
    "INVALID_KCONFIG_MANIFEST_START",
    "orphaned_fixture:",
    "expected_canonical_name",
]


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing_marker:{marker}")
    return issues


def validate_exact_workflow_runs(text: str) -> list[str]:
    issues: list[str] = []
    for command, expected_count in EXPECTED_WORKFLOW_RUN_COUNTS.items():
        expected_line = f"run: {command}"
        count = sum(1 for line in text.splitlines() if line.strip() == expected_line)
        if count != expected_count:
            issues.append(f"workflow_exact_run:{command}:count={count}:expected={expected_count}")
    return issues


def validate_cases(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []

    conf_cases = payload.get("conf_cases")
    if not isinstance(conf_cases, list):
        return ["cases:conf_cases:expected_list"]
    conf_names = [case.get("name") for case in conf_cases if isinstance(case, dict)]
    if conf_names != EXPECTED_CONF_CASE_ORDER:
        issues.append("cases:conf_cases=expected_exact_order")

    confdata_cases = payload.get("confdata_cases")
    if not isinstance(confdata_cases, list):
        return ["cases:confdata_cases:expected_list"]
    confdata_names = [case.get("name") for case in confdata_cases if isinstance(case, dict)]
    if confdata_names != EXPECTED_CONFDATA_CASE_ORDER:
        issues.append("cases:confdata_cases=expected_exact_order")

    if len(conf_cases) != 16:
        issues.append(f"cases:conf_case_count={len(conf_cases)}:expected=16")
    if len(confdata_cases) != 18:
        issues.append(f"cases:confdata_case_count={len(confdata_cases)}:expected=18")

    by_name = {
        case.get("name"): case
        for case in conf_cases + confdata_cases
        if isinstance(case, dict) and isinstance(case.get("name"), str)
    }

    syncconfig = by_name.get("syncconfig", {})
    if syncconfig.get("autoconfig") != "generated/phase2/auto-sync.conf":
        issues.append("cases:syncconfig:autoconfig=generated/phase2/auto-sync.conf")
    if syncconfig.get("autoheader") != "generated/phase2/autoconf-sync.h":
        issues.append("cases:syncconfig:autoheader=generated/phase2/autoconf-sync.h")
    if syncconfig.get("nosilentupdate") != "1":
        issues.append("cases:syncconfig:nosilentupdate=1")

    allyesconfig = by_name.get("allyesconfig", {})
    if allyesconfig.get("allconfig_env") != "arch/riscv/configs/allyes-seed.config":
        issues.append("cases:allyesconfig:allconfig_env=arch/riscv/configs/allyes-seed.config")

    randconfig = by_name.get("randconfig", {})
    if randconfig.get("allconfig") != "seed/allrandom.config":
        issues.append("cases:randconfig:allconfig=seed/allrandom.config")
    if randconfig.get("seed") != "0xC0FFEE":
        issues.append("cases:randconfig:seed=0xC0FFEE")
    if randconfig.get("probability") != "10:20:30":
        issues.append("cases:randconfig:probability=10:20:30")

    trailing_comment = by_name.get("final_unterminated_unset_comment", {})
    if trailing_comment.get("input") != "final_unterminated_unset_comment.config":
        issues.append(
            "cases:final_unterminated_unset_comment:input=final_unterminated_unset_comment.config"
        )

    trailing_backslash = by_name.get("trailing_escaped_backslash", {})
    if trailing_backslash.get("expected") != "trailing_escaped_backslash_expected.json":
        issues.append(
            "cases:trailing_escaped_backslash:expected=trailing_escaped_backslash_expected.json"
        )

    return issues


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build_valid_cases_json() -> str:
    payload = {
        "conf_cases": [
            {"name": "oldaskconfig"},
            {"name": "oldconfig"},
            {
                "name": "syncconfig",
                "autoconfig": "generated/phase2/auto-sync.conf",
                "autoheader": "generated/phase2/autoconf-sync.h",
                "nosilentupdate": "1",
            },
            {"name": "defconfig"},
            {"name": "savedefconfig"},
            {"name": "allnoconfig"},
            {"name": "allyesconfig", "allconfig_env": "arch/riscv/configs/allyes-seed.config"},
            {"name": "allmodconfig"},
            {"name": "alldefconfig"},
            {
                "name": "randconfig",
                "allconfig": "seed/allrandom.config",
                "seed": "0xC0FFEE",
                "probability": "10:20:30",
            },
            {"name": "listnewconfig"},
            {"name": "helpnewconfig"},
            {"name": "olddefconfig"},
            {"name": "yes2modconfig"},
            {"name": "mod2yesconfig"},
            {"name": "mod2noconfig"},
        ],
        "confdata_cases": [
            {"name": "duplicate_assignments"},
            {"name": "empty_string"},
            {"name": "empty_symbol_names"},
            {"name": "escaped_control_sequences"},
            {"name": "escaped_low_control_bytes"},
            {"name": "escaped_strings"},
            {"name": "explicit_n_tristate"},
            {"name": "final_trailing_carriage_return"},
            {
                "name": "final_unterminated_unset_comment",
                "input": "final_unterminated_unset_comment.config",
            },
            {"name": "ignore_non_config_lines"},
            {"name": "malformed_quoted_string"},
            {"name": "negative_signed_numeric_kinds"},
            {"name": "numeric_kinds"},
            {"name": "quoted_suffix_bytes"},
            {"name": "sample"},
            {"name": "sample_crlf"},
            {"name": "signed_numeric_kinds"},
            {
                "name": "trailing_escaped_backslash",
                "expected": "trailing_escaped_backslash_expected.json",
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def run_self_test() -> int:
    valid_workflow = "\n".join(
        f"run: {command}" for command in EXPECTED_WORKFLOW_RUN_COUNTS
    ) + "\n"
    if validate_exact_workflow_runs(valid_workflow):
        raise SystemExit("phase2-kconfig-alignment:self-test:workflow_counts")

    invalid_workflow = "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test\n"
    workflow_issues = validate_exact_workflow_runs(invalid_workflow)
    if not any(issue.startswith("workflow_exact_run:") for issue in workflow_issues):
        raise SystemExit("phase2-kconfig-alignment:self-test:workflow_missing_failure")

    valid_checker = "\n".join(KCONFIG_CHECKER_MARKERS) + "\n"
    if validate_required_markers(
        valid_checker,
        label="kconfig_checker",
        markers=KCONFIG_CHECKER_MARKERS,
    ):
        raise SystemExit("phase2-kconfig-alignment:self-test:checker_markers")

    marker_issues = validate_required_markers(
        "alpha\nbeta\n",
        label="sample",
        markers=["gamma"],
    )
    if marker_issues != ["sample:missing_marker:gamma"]:
        raise SystemExit("phase2-kconfig-alignment:self-test:marker_failure_shape")

    valid_cases = json.loads(build_valid_cases_json())
    if validate_cases(valid_cases):
        raise SystemExit("phase2-kconfig-alignment:self-test:valid_cases")

    invalid_cases = json.loads(build_valid_cases_json())
    invalid_cases["confdata_cases"][0], invalid_cases["confdata_cases"][1] = (
        invalid_cases["confdata_cases"][1],
        invalid_cases["confdata_cases"][0],
    )
    issues = validate_cases(invalid_cases)
    if "cases:confdata_cases=expected_exact_order" not in issues:
        raise SystemExit("phase2-kconfig-alignment:self-test:confdata_order_failure")

    invalid_cases = json.loads(build_valid_cases_json())
    invalid_cases["conf_cases"][2]["autoconfig"] = "broken"
    issues = validate_cases(invalid_cases)
    if "cases:syncconfig:autoconfig=generated/phase2/auto-sync.conf" not in issues:
        raise SystemExit("phase2-kconfig-alignment:self-test:syncconfig_autoconfig_failure")

    invalid_cases = json.loads(build_valid_cases_json())
    invalid_cases["confdata_cases"] = invalid_cases["confdata_cases"][:-1]
    issues = validate_cases(invalid_cases)
    if "cases:confdata_case_count=17:expected=18" not in issues:
        raise SystemExit("phase2-kconfig-alignment:self-test:confdata_count_failure")

    with tempfile.TemporaryDirectory(prefix="phase2_kconfig_alignment_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write(tmp_root / "scripts" / "zigux" / "check-kconfig-bridge.py", valid_checker)
        write(tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml", valid_workflow)
        write(
            tmp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
            build_valid_cases_json(),
        )

        round_trip = load_json_object(
            tmp_root / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
            label="cases",
        )
        if validate_cases(round_trip):
            raise SystemExit("phase2-kconfig-alignment:self-test:json_round_trip")

    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 kconfig checker, fixture manifest, and workflow gate aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [KCONFIG_CHECKER, WORKFLOW, CASES]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_KCONFIG_ALIGNMENT=fail")
        print("MISSING_PHASE2_KCONFIG_ALIGNMENT_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_KCONFIG_ALIGNMENT_FILES_END")
        return 1

    issues: list[str] = []
    issues.extend(
        validate_required_markers(
            KCONFIG_CHECKER.read_text(encoding="utf-8"),
            label="kconfig_checker",
            markers=KCONFIG_CHECKER_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(WORKFLOW.read_text(encoding="utf-8")))
    issues.extend(validate_cases(load_json_object(CASES, label="cases")))

    if issues:
        print("PHASE2_KCONFIG_ALIGNMENT=fail")
        print("INVALID_PHASE2_KCONFIG_ALIGNMENT_START")
        for item in issues:
            print(item)
        print("INVALID_PHASE2_KCONFIG_ALIGNMENT_END")
        return 1

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
