#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CHECK_PHASE2_TESTS_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
CHECK_PHASE2_KCONFIG_README_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-kconfig-readme-alignment.py"
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_MAKEFILE = ROOT / "zigux" / "Makefile"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
KCONFIG_BRIDGE_CONF_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
)

PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "PHASE2_TOOLCHAIN_PIN_SCOPE_GATE=python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
]

PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS = [
    "PHASE2_FIXDEP_EMBEDDED_NUL_GUARD=fixdep.zig truncates depfile parsing at the first embedded NUL and keeps dep parsing skips bytes after the first embedded NUL as the bounded parser guard",
]

PHASE2_GENKSYMS_REQUIRED_SOURCE_MARKERS = [
    "shared genksyms bridge selftest-alignment self-test: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test`",
    "shared genksyms bridge selftest-alignment gate: `python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py`",
    "direct genksyms bridge self-test: `python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "direct genksyms bridge gate: `python3 scripts/zigux/check-genksyms-bridge.py`",
    "the dedicated Phase 2 `genksyms` bridge packet remains the live `22-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`",
]

PHASE2_MAKEFILE_RUN_COUNTS = {
    "scripts/zigux/check-zig-toolchain.py": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test": 1,
    "scripts/zigux/check-phase2-toolchain-pin-scope.py": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-tests-readme-alignment.py": 1,
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test": 1,
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py": 1,
}

EXPECTED_KCONFIG_CONF_CASES = (
    {
        "name": "oldaskconfig",
        "mode": "oldaskconfig",
        "kconfig": "Kconfig",
        "config": "ask/.config",
        "arch": "x86_64",
        "expected": "oldaskconfig_expected.json",
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
    {
        "name": "oldconfig",
        "mode": "oldconfig",
        "kconfig": "Kconfig",
        "config": "refresh/.config",
        "arch": "x86",
        "expected": "oldconfig_expected.json",
    },
    {
        "name": "allnoconfig",
        "mode": "allnoconfig",
        "kconfig": "Kconfig",
        "config": "none/.config",
        "arch": "arm64",
        "expected": "allnoconfig_expected.json",
    },
    {
        "name": "allyesconfig",
        "mode": "allyesconfig",
        "kconfig": "Kconfig",
        "config": "yes/.config",
        "arch": "arm64",
        "expected": "allyesconfig_expected.json",
    },
    {
        "name": "allmodconfig",
        "mode": "allmodconfig",
        "kconfig": "Kconfig",
        "config": "mod/.config",
        "arch": "arm",
        "allconfig": "",
        "expected": "allmodconfig_expected.json",
    },
    {
        "name": "alldefconfig",
        "mode": "alldefconfig",
        "kconfig": "Kconfig",
        "config": "build/.config",
        "arch": "arm64",
        "expected": "alldefconfig_expected.json",
    },
    {
        "name": "randconfig",
        "mode": "randconfig",
        "kconfig": "Kconfig",
        "config": "rand/.config",
        "arch": "x86_64",
        "allconfig": "allrandom.config",
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
    {
        "name": "helpnewconfig",
        "mode": "helpnewconfig",
        "kconfig": "Kconfig",
        "config": "out/help.config",
        "arch": "riscv64",
        "silent": true,
        "expected": "helpnewconfig_expected.json",
    },
    {
        "name": "olddefconfig",
        "mode": "olddefconfig",
        "kconfig": "Kconfig",
        "config": ".config",
        "arch": "x86_64",
        "expected": "olddefconfig_expected.json",
    },
    {
        "name": "yes2modconfig",
        "mode": "yes2modconfig",
        "kconfig": "Kconfig",
        "config": "rewrite/.config",
        "arch": "x86",
        "expected": "yes2modconfig_expected.json",
    },
    {
        "name": "mod2yesconfig",
        "mode": "mod2yesconfig",
        "kconfig": "Kconfig",
        "config": "promote/.config",
        "arch": "x86",
        "expected": "mod2yesconfig_expected.json",
    },
    {
        "name": "mod2noconfig",
        "mode": "mod2noconfig",
        "kconfig": "Kconfig",
        "config": "demote/.config",
        "arch": "x86",
        "expected": "mod2noconfig_expected.json",
    },
)

EXPECTED_KCONFIG_CONF_MANIFEST = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 16,
    "cases": [
        "oldaskconfig",
        "syncconfig",
        "oldconfig",
        "allnoconfig",
        "allyesconfig",
        "allmodconfig",
        "alldefconfig",
        "randconfig",
        "defconfig",
        "savedefconfig",
        "listnewconfig",
        "helpnewconfig",
        "olddefconfig",
        "yes2modconfig",
        "mod2yesconfig",
        "mod2noconfig",
    ],
    "stdout_packet": [
        "oldaskconfig_expected.json",
        "syncconfig_expected.json",
        "oldconfig_expected.json",
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "allmodconfig_expected.json",
        "alldefconfig_expected.json",
        "randconfig_expected.json",
        "defconfig_expected.json",
        "savedefconfig_expected.json",
        "listnewconfig_expected.json",
        "helpnewconfig_expected.json",
        "olddefconfig_expected.json",
        "yes2modconfig_expected.json",
        "mod2yesconfig_expected.json",
        "mod2noconfig_expected.json",
    ],
    "mode_arg_cases": ["defconfig", "savedefconfig"],
    "silent_request_packet": ["helpnewconfig_expected.json"],
    "syncconfig_env_packet": ["syncconfig_expected.json"],
    "allconfig_sentinel_packet": [
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "alldefconfig_expected.json",
    ],
    "allconfig_override_packet": [
        "allmodconfig_expected.json",
        "randconfig_expected.json",
    ],
}


def require_files(paths: list[Path]) -> list[str]:
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    return missing


def validate_required_markers(text: str, markers: list[str], label: str) -> list[str]:
    return [f"{label}:missing:{marker}" for marker in markers if marker not in text]


def validate_exact_makefile_runs(makefile_text: str) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in makefile_text.splitlines()]
    for command, expected in PHASE2_MAKEFILE_RUN_COUNTS.items():
        expected_line = f"cd $(ZIGUX_ROOT) && $(PYTHON) {command}"
        count = sum(1 for line in lines if line == expected_line)
        if count != expected:
            issues.append(f"makefile:exact_count:{command}:count={count}:expected={expected}")
    return issues


def load_json_object(path: Path, label: str) -> tuple[dict[str, object] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{label}:read_error:{exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{label}:invalid_json:{exc.msg}"]

    if not isinstance(payload, dict):
        return None, [f"{label}:expected_object"]
    return payload, []


def collect_conf_case_files(cases_payload: dict[str, object]) -> tuple[list[Path], list[str]]:
    issues: list[str] = []
    cases = cases_payload.get("conf_cases")
    if not isinstance(cases, list):
        return [], ["kconfig_bridge_cases:conf_cases:expected_list"]
    if not cases:
        return [], ["kconfig_bridge_cases:conf_cases:empty"]

    expected_count = len(EXPECTED_KCONFIG_CONF_CASES)
    if len(cases) != expected_count:
        issues.append(
            f"kconfig_bridge_cases:conf_cases:count={len(cases)}:expected={expected_count}"
        )

    expected_files: list[Path] = []
    seen_expected: set[str] = set()
    for index, expected_case in enumerate(EXPECTED_KCONFIG_CONF_CASES):
        if index >= len(cases):
            break

        case = cases[index]
        expected_name = expected_case["name"]
        if not isinstance(case, dict):
            issues.append(f"kconfig_bridge_cases:conf_cases[{index}]:expected_object")
            continue

        for field_name, expected_value in expected_case.items():
            actual_value = case.get(field_name)
            if actual_value != expected_value:
                issues.append(
                    f"kconfig_bridge_cases:{expected_name}:{field_name}:expected={expected_value}:actual={actual_value}"
                )

        unexpected_fields = sorted(set(case.keys()) - set(expected_case.keys()))
        for field_name in unexpected_fields:
            issues.append(
                f"kconfig_bridge_cases:{expected_name}:{field_name}:unexpected={case.get(field_name)}"
            )

        expected = case.get("expected")
        if isinstance(expected, str) and expected:
            if expected in seen_expected:
                issues.append(
                    f"kconfig_bridge_cases:{expected_name}:expected:duplicate_reference:{expected}"
                )
            else:
                seen_expected.add(expected)
                expected_files.append(KCONFIG_BRIDGE_CASES.parent / expected)

    if len(cases) > expected_count:
        for case in cases[expected_count:]:
            extra_name = case.get("name", "<missing>") if isinstance(case, dict) else "<non_object>"
            issues.append(f"kconfig_bridge_cases:conf_cases:unexpected_extra:{extra_name}")

    return expected_files, issues


def collect_conf_manifest_issues(manifest_payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    for field_name, expected_value in EXPECTED_KCONFIG_CONF_MANIFEST.items():
        actual_value = manifest_payload.get(field_name)
        if actual_value != expected_value:
            issues.append(
                f"kconfig_bridge_conf_manifest:{field_name}:expected={expected_value}:actual={actual_value}"
            )
    return issues


def run_self_test_checks() -> list[str]:
    checks = [
        (
            "conf_cases_ok",
            collect_conf_case_files(
                {"conf_cases": [dict(case) for case in EXPECTED_KCONFIG_CONF_CASES]}
            )[1],
            [],
        ),
        (
            "conf_cases_missing_entry",
            collect_conf_case_files(
                {"conf_cases": [dict(case) for case in EXPECTED_KCONFIG_CONF_CASES[:-1]]}
            )[1],
            ["kconfig_bridge_cases:conf_cases:count=15:expected=16"],
        ),
        (
            "conf_cases_missing_mode_arg",
            collect_conf_case_files(
                {
                    "conf_cases": [
                        *[dict(case) for case in EXPECTED_KCONFIG_CONF_CASES[:8]],
                        {
                            "name": "defconfig",
                            "mode": "defconfig",
                            "kconfig": "Kconfig",
                            "config": "out/.config",
                            "arch": "arm64",
                            "expected": "defconfig_expected.json",
                        },
                        *[dict(case) for case in EXPECTED_KCONFIG_CONF_CASES[9:]],
                    ]
                }
            )[1],
            [
                "kconfig_bridge_cases:defconfig:mode_arg:expected=arch/arm64/configs/defconfig:actual=None"
            ],
        ),
        (
            "conf_cases_unexpected_silent",
            collect_conf_case_files(
                {
                    "conf_cases": [
                        {
                            "name": "oldaskconfig",
                            "mode": "oldaskconfig",
                            "kconfig": "Kconfig",
                            "config": "ask/.config",
                            "arch": "x86_64",
                            "silent": True,
                            "expected": "oldaskconfig_expected.json",
                        },
                        *[dict(case) for case in EXPECTED_KCONFIG_CONF_CASES[1:]],
                    ]
                }
            )[1],
            ["kconfig_bridge_cases:oldaskconfig:silent:unexpected=True"],
        ),
        (
            "conf_manifest_ok",
            collect_conf_manifest_issues(dict(EXPECTED_KCONFIG_CONF_MANIFEST)),
            [],
        ),
        (
            "conf_manifest_case_count_mismatch",
            collect_conf_manifest_issues(
                dict(EXPECTED_KCONFIG_CONF_MANIFEST, case_count=15)
            ),
            ["kconfig_bridge_conf_manifest:case_count:expected=16:actual=15"],
        ),
        (
            "conf_manifest_silent_packet_mismatch",
            collect_conf_manifest_issues(
                dict(EXPECTED_KCONFIG_CONF_MANIFEST, silent_request_packet=[])
            ),
            [
                "kconfig_bridge_conf_manifest:silent_request_packet:expected=['helpnewconfig_expected.json']:actual=[]"
            ],
        ),
    ]

    issues: list[str] = []
    for name, actual, expected in checks:
        if actual != expected:
            issues.append(f"self_test:{name}:actual={actual}:expected={expected}")
    return issues


def run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current live Phase 2 closure packet on current master."
    )
    parser.add_argument("--self-test", action="store_true", help="Run closure-validator self coverage.")
    args = parser.parse_args()

    required = [
        CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE,
        CHECK_PHASE2_TESTS_README_ALIGNMENT,
        CHECK_PHASE2_KCONFIG_README_ALIGNMENT,
        PHASE2_CLOSURE_DOC,
        PHASE2_MAKEFILE,
        KCONFIG_BRIDGE_CASES,
        KCONFIG_BRIDGE_CONF_MANIFEST,
    ]
    missing = require_files(required)
    if missing:
        label = "PHASE2_CLOSURE_VALIDATION_SELF_TEST" if args.self_test else "PHASE2_CLOSURE_VALIDATION"
        print(f"{label}=fail")
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE2_CLOSURE_VALIDATION_MISSING_FILES_END")
        return 1

    closure_text = PHASE2_CLOSURE_DOC.read_text(encoding="utf-8")
    makefile_text = PHASE2_MAKEFILE.read_text(encoding="utf-8")

    issues: list[str] = []
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_TOOLCHAIN_PIN_SCOPE_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_FIXDEP_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(
        validate_required_markers(
            closure_text,
            PHASE2_GENKSYMS_REQUIRED_SOURCE_MARKERS,
            "phase2_closure",
        )
    )
    issues.extend(validate_exact_makefile_runs(makefile_text))

    kconfig_bridge_cases_payload, kconfig_bridge_cases_load_issues = load_json_object(
        KCONFIG_BRIDGE_CASES,
        label="kconfig_bridge_cases",
    )
    issues.extend(kconfig_bridge_cases_load_issues)
    if kconfig_bridge_cases_payload is not None:
        conf_case_files, conf_case_issues = collect_conf_case_files(
            kconfig_bridge_cases_payload
        )
        issues.extend(conf_case_issues)
        issues.extend(
            f"kconfig_bridge_cases:missing_expected:{item}"
            for item in require_files(conf_case_files)
        )

    kconfig_bridge_conf_manifest_payload, kconfig_bridge_conf_manifest_load_issues = load_json_object(
        KCONFIG_BRIDGE_CONF_MANIFEST,
        label="kconfig_bridge_conf_manifest",
    )
    issues.extend(kconfig_bridge_conf_manifest_load_issues)
    if kconfig_bridge_conf_manifest_payload is not None:
        issues.extend(
            collect_conf_manifest_issues(kconfig_bridge_conf_manifest_payload)
        )

    if args.self_test:
        issues.extend(run_self_test_checks())
        if issues:
            print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
        print("PHASE2_CLOSURE_VALIDATION_SELF_TEST_CHECK_COUNT=22")
        return 0

    if issues:
        print("PHASE2_CLOSURE_VALIDATION=fail")
        for issue in issues:
            print(issue)
        return 1

    commands = [
        [sys.executable, str(CHECK_PHASE2_TESTS_README_ALIGNMENT)],
        [sys.executable, str(CHECK_PHASE2_KCONFIG_README_ALIGNMENT)],
        [sys.executable, str(CHECK_PHASE2_TOOLCHAIN_PIN_SCOPE)],
    ]
    for command in commands:
        if run(command) != 0:
            print("PHASE2_CLOSURE_VALIDATION=fail")
            print(f"PHASE2_CLOSURE_VALIDATION_FAILED_COMMAND={' '.join(command[1:])}")
            return 1

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_VALIDATION_COMMAND_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
