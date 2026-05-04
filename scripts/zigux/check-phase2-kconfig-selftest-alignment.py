#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
KCONFIG_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
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

EXPECTED_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
}

EXPECTED_MAKEFILE_KCONFIG_ROUTE_COUNTS = {
    "scripts/zigux/check-kconfig-bridge.py --self-test": 1,
    "scripts/zigux/check-kconfig-bridge.py": 1,
    "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig": 1,
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
    "allconfig_env is not None and not isinstance(allconfig_env, str)",
    "compare_text_artifacts(actual, repeat)",
    "compare_text_artifacts(actual, rebuild)",
    "compare_text_artifacts(default_actual, default_repeat)",
    "compare_text_artifacts(default_actual, default_rebuild)",
    "input_path=trailing_cr_input",
    "input_path=final_unset_input",
    "env['KCONFIG_ALLCONFIG'] = case['allconfig_env']",
    "env['KCONFIG_AUTOCONFIG'] = case['autoconfig']",
    "env['KCONFIG_AUTOHEADER'] = case['autoheader']",
    "env['KCONFIG_NOSILENTUPDATE'] = case['nosilentupdate']",
    "env['KCONFIG_SEED'] = case['seed']",
    "env['KCONFIG_PROBABILITY'] = case['probability']",
]

PHASE2_VALIDATOR_MARKERS = [
    "KCONFIG_ALIGNMENT_CHECKER = (",
    '"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass"',
    '"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=13"',
    '"phase2_kconfig_alignment_checker"',
    "PHASE2_KCONFIG_REQUIRED_SOURCE_MARKERS = [",
    '"assert total_self_test_cases == 6",',
    '"compare_text_artifacts(default_actual, default_rebuild)",',
    '"input_path=trailing_cr_input",',
    '"input_path=final_unset_input",',
    '"print(\'KCONFIG_BRIDGE_DETERMINISM=pass\')",',
]

PHASE2_CLOSURE_VALIDATOR_MARKERS = [
    "CHECK_PHASE2_KCONFIG_SELFTEST_ALIGNMENT = ROOT / 'scripts' / 'zigux' / 'check-phase2-kconfig-selftest-alignment.py'",
    "'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test': 1,",
    "'python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py': 1,",
    "PHASE2_KCONFIG_BRIDGE_DETERMINISM=check-kconfig-bridge.py replays conf and confdata outputs twice and compares a rebuilt confdata binary against the same JSON artifacts",
    "PHASE2_KCONFIG_BRIDGE_LOW_CONTROL_CASE=zigux/tests/fixtures/kconfig_bridge/escaped_low_control_bytes_expected.json",
    "PHASE2_KCONFIG_BRIDGE_MANIFEST_POLICY=check-kconfig-bridge.py rejects uncovered modes, malformed manifests, duplicate fixture references, orphaned fixture files, and non-canonical confdata names before replay",
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


def validate_exact_makefile_runs(
    text: str,
    *,
    expected_counts: dict[str, int] = EXPECTED_MAKEFILE_RUN_COUNTS,
) -> list[str]:
    issues: list[str] = []
    stripped_lines = [line.strip() for line in text.splitlines()]
    for command, expected_count in expected_counts.items():
        count = sum(1 for line in stripped_lines if line.endswith(command))
        if count != expected_count:
            issues.append(f"makefile_exact_run:{command}:count={count}:expected={expected_count}")
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

    allmodconfig = by_name.get("allmodconfig", {})
    if allmodconfig.get("allconfig_env") != "":
        issues.append("cases:allmodconfig:allconfig_env=empty_string_trigger")

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
            {"name": "allmodconfig", "allconfig_env": ""},
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

    valid_makefile = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        ]
    ) + "\n"
    if validate_exact_makefile_runs(valid_makefile):
        raise SystemExit("phase2-kconfig-alignment:self-test:makefile_counts")

    invalid_makefile = "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test\n"
    makefile_issues = validate_exact_makefile_runs(invalid_makefile)
    if not any(issue.startswith("makefile_exact_run:") for issue in makefile_issues):
        raise SystemExit("phase2-kconfig-alignment:self-test:makefile_missing_failure")

    valid_makefile_kconfig_route = "\n".join(
        [
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
        ]
    ) + "\n"
    if validate_exact_makefile_runs(
        valid_makefile_kconfig_route,
        expected_counts=EXPECTED_MAKEFILE_KCONFIG_ROUTE_COUNTS,
    ):
        raise SystemExit("phase2-kconfig-alignment:self-test:makefile_kconfig_route_counts")

    kconfig_route_failures = [
        (
            "phase2-kconfig-alignment:self-test:makefile_kconfig_selftest_missing",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test\n",
            "makefile_exact_run:scripts/zigux/check-kconfig-bridge.py --self-test:count=0:expected=1",
        ),
        (
            "phase2-kconfig-alignment:self-test:makefile_kconfig_live_missing",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py\n",
            "makefile_exact_run:scripts/zigux/check-kconfig-bridge.py:count=0:expected=1",
        ),
        (
            "phase2-kconfig-alignment:self-test:makefile_conf_bridge_test_missing",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig\n",
            "makefile_exact_run:$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig:count=0:expected=1",
        ),
        (
            "phase2-kconfig-alignment:self-test:makefile_confdata_bridge_test_missing",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig\n",
            "makefile_exact_run:$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig:count=0:expected=1",
        ),
    ]
    for failure_label, removed_line, expected_issue in kconfig_route_failures:
        makefile_issues = validate_exact_makefile_runs(
            valid_makefile_kconfig_route.replace(removed_line, "", 1),
            expected_counts=EXPECTED_MAKEFILE_KCONFIG_ROUTE_COUNTS,
        )
        if expected_issue not in makefile_issues:
            raise SystemExit(failure_label)

    valid_checker = "\n".join(KCONFIG_CHECKER_MARKERS) + "\n"
    if validate_required_markers(
        valid_checker,
        label="kconfig_checker",
        markers=KCONFIG_CHECKER_MARKERS,
    ):
        raise SystemExit("phase2-kconfig-alignment:self-test:checker_markers")

    validator_text = "\n".join(PHASE2_VALIDATOR_MARKERS) + "\n"
    if validate_required_markers(
        validator_text,
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-kconfig-alignment:self-test:validator_markers")

    closure_validator_text = "\n".join(PHASE2_CLOSURE_VALIDATOR_MARKERS) + "\n"
    if validate_required_markers(
        closure_validator_text,
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    ):
        raise SystemExit("phase2-kconfig-alignment:self-test:closure_validator_markers")

    marker_issues = validate_required_markers(
        "alpha\nbeta\n",
        label="sample",
        markers=["gamma"],
    )
    if marker_issues != ["sample:missing_marker:gamma"]:
        raise SystemExit("phase2-kconfig-alignment:self-test:marker_failure_shape")

    validator_marker_issues = validate_required_markers(
        validator_text.replace(PHASE2_VALIDATOR_MARKERS[0] + "\n", "", 1),
        label="phase2_validator",
        markers=PHASE2_VALIDATOR_MARKERS,
    )
    if validator_marker_issues != [
        f"phase2_validator:missing_marker:{PHASE2_VALIDATOR_MARKERS[0]}"
    ]:
        raise SystemExit("phase2-kconfig-alignment:self-test:validator_marker_failure")

    closure_validator_marker_issues = validate_required_markers(
        closure_validator_text.replace(PHASE2_CLOSURE_VALIDATOR_MARKERS[0] + "\n", "", 1),
        label="phase2_closure_validator",
        markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
    )
    if closure_validator_marker_issues != [
        f"phase2_closure_validator:missing_marker:{PHASE2_CLOSURE_VALIDATOR_MARKERS[0]}"
    ]:
        raise SystemExit("phase2-kconfig-alignment:self-test:closure_validator_marker_failure")

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
        write(tmp_root / "scripts" / "zigux" / "validate-phase2.py", validator_text)
        write(
            tmp_root / "scripts" / "zigux" / "validate-phase2-closure.py",
            closure_validator_text,
        )
        write(tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml", valid_workflow)
        write(tmp_root / "zigux" / "Makefile", valid_makefile)
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
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT=13")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 kconfig checker, shared validators, fixture manifest, workflow gate, and Linux-style make route aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in alignment checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    required_files = [KCONFIG_CHECKER, PHASE2_VALIDATOR, PHASE2_CLOSURE_VALIDATOR, WORKFLOW, MAKEFILE, CASES]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        print("PHASE2_KCONFIG_ALIGNMENT=fail")
        print("MISSING_PHASE2_KCONFIG_ALIGNMENT_FILES_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE2_KCONFIG_ALIGNMENT_FILES_END")
        return 1

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    makefile_text = MAKEFILE.read_text(encoding="utf-8")

    issues: list[str] = []
    issues.extend(
        validate_required_markers(
            KCONFIG_CHECKER.read_text(encoding="utf-8"),
            label="kconfig_checker",
            markers=KCONFIG_CHECKER_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_validator",
            markers=PHASE2_VALIDATOR_MARKERS,
        )
    )
    issues.extend(
        validate_required_markers(
            PHASE2_CLOSURE_VALIDATOR.read_text(encoding="utf-8"),
            label="phase2_closure_validator",
            markers=PHASE2_CLOSURE_VALIDATOR_MARKERS,
        )
    )
    issues.extend(validate_exact_workflow_runs(workflow_text))
    issues.extend(validate_exact_makefile_runs(makefile_text))
    issues.extend(
        validate_exact_makefile_runs(
            makefile_text,
            expected_counts=EXPECTED_MAKEFILE_KCONFIG_ROUTE_COUNTS,
        )
    )
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
