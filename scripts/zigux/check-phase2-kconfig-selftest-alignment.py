#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
CONFDATA_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
KCONFIG_BRIDGE_SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    KCONFIG_BRIDGE_CHECKER,
    KCONFIG_BRIDGE_CASES,
    CONF_MANIFEST,
    CONFDATA_MANIFEST,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: make -C zigux phase2-kconfig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
)

WORKFLOW_PATH_LINES = (
    "- 'scripts/kconfig/conf.c'",
    "- 'scripts/kconfig/confdata.c'",
)

MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
)

SCRIPTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "the manifest-backed kconfig fixture roster",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "make -C zigux phase2-kconfig",
)

REVIEW_CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-kconfig",
)

BRIDGE_CHECKER_LINE_MARKERS = (
    'if group_name == "conf_cases" and "silent" in case and not isinstance(case["silent"], bool):',
    'if "silent" in case and case["silent"] is not True:',
    'if case.get("silent"):',
    'cmd.append("silent")',
)

EXPECTED_SILENT_CONF_CASE_NAMES = (
    "listnewconfig",
    "helpnewconfig",
)

CONF_MANIFEST_STATIC_FIELDS = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
}

CONFDATA_MANIFEST_STATIC_FIELDS = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
}

VALID_CASES_PAYLOAD = {
    "conf_cases": [
        {
            "name": "listnewconfig",
            "mode": "listnewconfig",
            "kconfig": "Kconfig",
            "config": "out/list.config",
            "arch": "x86_64",
            "silent": True,
            "expected": "listnewconfig_expected.json",
        },
        {
            "name": "helpnewconfig",
            "mode": "helpnewconfig",
            "kconfig": "Kconfig",
            "config": "out/help.config",
            "arch": "riscv64",
            "silent": True,
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
    ],
    "confdata_cases": [
        {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_PATH_LINES)
    + len(WORKFLOW_PATH_LINES)
    + len(MAKEFILE_LINES)
    + len(MAKEFILE_LINES)
    + len(SCRIPTS_README_MARKERS)
    + len(TESTS_README_MARKERS)
    + len(REVIEW_CHECKLIST_MARKERS)
    + len(KCONFIG_BRIDGE_SURFACE_PATHS)
    + len(BRIDGE_CHECKER_LINE_MARKERS)
    + len(BRIDGE_CHECKER_LINE_MARKERS)
    + 3
    + 6
    + 6
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def build_conf_manifest_payload(conf_cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        **CONF_MANIFEST_STATIC_FIELDS,
        "case_count": len(conf_cases),
        "cases": [case["name"] for case in conf_cases],
        "stdout_packet": [case["expected"] for case in conf_cases],
        "mode_arg_cases": [case["name"] for case in conf_cases if "mode_arg" in case],
        "silent_request_packet": [case["expected"] for case in conf_cases if case.get("silent") is True],
        "syncconfig_env_packet": [case["expected"] for case in conf_cases if case["mode"] == "syncconfig"],
        "allconfig_sentinel_packet": [
            case["expected"] for case in conf_cases if case["mode"] in ("allnoconfig", "allyesconfig", "alldefconfig")
        ],
        "allconfig_override_packet": [case["expected"] for case in conf_cases if "allconfig" in case],
        "randconfig_env_packet": [case["expected"] for case in conf_cases if case["mode"] == "randconfig"],
        "helper_local_anchors": [
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
        ],
    }


def build_confdata_manifest_payload(confdata_cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        **CONFDATA_MANIFEST_STATIC_FIELDS,
        "case_count": len(confdata_cases),
        "cases": [case["name"] for case in confdata_cases],
        "input_packet": [case["input"] for case in confdata_cases],
        "expected_packet": [case["expected"] for case in confdata_cases],
    }


def collect_manifest_field_issues(
    manifest: object,
    *,
    expected_fields: dict[str, object],
    invalid_payload_code: str,
    field_mismatch_code: str,
) -> list[tuple[str, str]]:
    if not isinstance(manifest, dict):
        return [(invalid_payload_code, type(manifest).__name__)]

    issues: list[tuple[str, str]] = []
    for field_name, expected_value in expected_fields.items():
        actual_value = manifest.get(field_name)
        if actual_value != expected_value:
            issues.append(
                (
                    field_mismatch_code,
                    f"{field_name}:actual={actual_value!r}:expected={expected_value!r}",
                )
            )
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    bridge_checker_text = read_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in WORKFLOW_PATH_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_PATH_FILTERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_PATH_FILTERS", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(
        collect_missing_markers(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS")
    )

    for marker in BRIDGE_CHECKER_LINE_MARKERS:
        count = count_exact_lines(bridge_checker_text, marker)
        if count == 0:
            issues.append(("MISSING_BRIDGE_CHECKER_MARKERS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_BRIDGE_CHECKER_MARKERS", f"{marker}:count={count}"))

    conf_cases: list[dict[str, object]] = []
    confdata_cases: list[dict[str, object]] = []
    try:
        cases_payload = read_json(resolve_path(root, KCONFIG_BRIDGE_CASES))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_CASES_JSON", str(exc)))
    else:
        if not isinstance(cases_payload, dict):
            issues.append(("INVALID_CASES_PAYLOAD", type(cases_payload).__name__))
        else:
            raw_conf_cases = cases_payload.get("conf_cases")
            if not isinstance(raw_conf_cases, list):
                issues.append(("INVALID_CONF_CASES_PAYLOAD", type(raw_conf_cases).__name__))
            else:
                conf_cases = [case for case in raw_conf_cases if isinstance(case, dict)]
                silent_case_names = [
                    case.get("name")
                    for case in conf_cases
                    if case.get("silent") is True
                ]
                if silent_case_names != list(EXPECTED_SILENT_CONF_CASE_NAMES):
                    issues.append(
                        (
                            "CONF_CASE_SILENT_PACKET_MISMATCH",
                            f"actual={silent_case_names!r}:expected={list(EXPECTED_SILENT_CONF_CASE_NAMES)!r}",
                        )
                    )

            raw_confdata_cases = cases_payload.get("confdata_cases")
            if not isinstance(raw_confdata_cases, list):
                issues.append(("INVALID_CONFDATA_CASES_PAYLOAD", type(raw_confdata_cases).__name__))
            else:
                confdata_cases = [case for case in raw_confdata_cases if isinstance(case, dict)]

    if conf_cases:
        try:
            conf_manifest = read_json(resolve_path(root, CONF_MANIFEST))
        except json.JSONDecodeError as exc:
            issues.append(("INVALID_CONF_MANIFEST_JSON", str(exc)))
        else:
            issues.extend(
                collect_manifest_field_issues(
                    conf_manifest,
                    expected_fields=build_conf_manifest_payload(conf_cases),
                    invalid_payload_code="INVALID_CONF_MANIFEST_PAYLOAD",
                    field_mismatch_code="CONF_MANIFEST_FIELD_MISMATCH",
                )
            )

    if confdata_cases:
        try:
            confdata_manifest = read_json(resolve_path(root, CONFDATA_MANIFEST))
        except json.JSONDecodeError as exc:
            issues.append(("INVALID_CONFDATA_MANIFEST_JSON", str(exc)))
        else:
            issues.extend(
                collect_manifest_field_issues(
                    confdata_manifest,
                    expected_fields=build_confdata_manifest_payload(confdata_cases),
                    invalid_payload_code="INVALID_CONFDATA_MANIFEST_PAYLOAD",
                    field_mismatch_code="CONFDATA_MANIFEST_FIELD_MISMATCH",
                )
            )

    for bridge_path in KCONFIG_BRIDGE_SURFACE_PATHS:
        if not resolve_path(root, bridge_path).exists():
            issues.append(("MISSING_BRIDGE_SURFACE_PATHS", bridge_path.relative_to(ROOT).as_posix()))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_KCONFIG_ALIGNMENT=fail")
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
    write_text(resolve_path(root, WORKFLOW), "\n".join((*WORKFLOW_PATH_LINES, *WORKFLOW_LINES)) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER), "\n".join(BRIDGE_CHECKER_LINE_MARKERS) + "\n")
    write_text(resolve_path(root, KCONFIG_BRIDGE_CASES), json.dumps(VALID_CASES_PAYLOAD, indent=2) + "\n")
    write_text(
        resolve_path(root, CONF_MANIFEST),
        json.dumps(build_conf_manifest_payload(VALID_CASES_PAYLOAD["conf_cases"]), indent=2) + "\n",
    )
    write_text(
        resolve_path(root, CONFDATA_MANIFEST),
        json.dumps(build_confdata_manifest_payload(VALID_CASES_PAYLOAD["confdata_cases"]), indent=2) + "\n",
    )
    for bridge_path in KCONFIG_BRIDGE_SURFACE_PATHS:
        resolved = resolve_path(root, bridge_path)
        if resolved.exists():
            continue
        content = "{}\n" if bridge_path.suffix == ".json" else "# present\n"
        write_text(resolved, content)


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_HOOKS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in WORKFLOW_PATH_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "- 'scripts/kconfig/other.c'"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_WORKFLOW_PATH_FILTERS", marker) in issues
            checks_run += 1

        for marker in WORKFLOW_PATH_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_WORKFLOW_PATH_FILTERS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/other.py"),
                encoding="utf-8",
            )
            issues = collect_issues(root)
            assert ("MISSING_MAKEFILE_HOOKS", marker) in issues
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count=2") in issues
            checks_run += 1

        for marker in SCRIPTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, SCRIPTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_SCRIPTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in REVIEW_CHECKLIST_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker, ""), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_REVIEW_CHECKLIST_MARKERS", marker) in issues
            checks_run += 1

        for marker in BRIDGE_CHECKER_LINE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "pass"), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_BRIDGE_CHECKER_MARKERS", marker) in issues
            checks_run += 1

        for marker in BRIDGE_CHECKER_LINE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("DUPLICATE_BRIDGE_CHECKER_MARKERS", f"{marker}:count=2") in issues
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["conf_cases"][1].pop("silent")
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CONF_CASE_SILENT_PACKET_MISMATCH",
            "actual=['listnewconfig']:expected=['listnewconfig', 'helpnewconfig']",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_CASES_PAYLOAD", "list") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_CASES_JSON" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONF_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0] = "broken"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "CONF_MANIFEST_FIELD_MISMATCH" and value.startswith("cases:") for code, value in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONF_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["silent_request_packet"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONF_MANIFEST_FIELD_MISMATCH" and value.startswith("silent_request_packet:")
            for code, value in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONF_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["helper_local_anchors"] = ["broken helper anchor"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONF_MANIFEST_FIELD_MISMATCH" and value.startswith("helper_local_anchors:")
            for code, value in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["input_packet"] = ["broken.config"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_MANIFEST_FIELD_MISMATCH" and value.startswith("input_packet:")
            for code, value in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["expected_packet"] = ["broken_expected.json"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_MANIFEST_FIELD_MISMATCH" and value.startswith("expected_packet:")
            for code, value in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONF_MANIFEST)
        path.write_text("{\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_CONF_MANIFEST_JSON" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        path.write_text("[]\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_CONFDATA_MANIFEST_PAYLOAD", "list") in issues
        checks_run += 1

        for bridge_path in KCONFIG_BRIDGE_SURFACE_PATHS:
            if bridge_path in (KCONFIG_BRIDGE_CHECKER, KCONFIG_BRIDGE_CASES, CONF_MANIFEST, CONFDATA_MANIFEST):
                continue
            build_self_test_root(root)
            resolve_path(root, bridge_path).unlink()
            issues = collect_issues(root)
            assert ("MISSING_BRIDGE_SURFACE_PATHS", bridge_path.relative_to(ROOT).as_posix()) in issues
            checks_run += 1

        for rel_path in (
            WORKFLOW,
            MAKEFILE,
            SCRIPTS_README,
            TESTS_README,
            REVIEW_CHECKLIST,
            KCONFIG_BRIDGE_CHECKER,
            KCONFIG_BRIDGE_CASES,
            CONF_MANIFEST,
            CONFDATA_MANIFEST,
        ):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 kconfig bridge packet stays aligned with the live bootstrap lane and reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_PATH_FILTER_COUNT={len(WORKFLOW_PATH_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_BRIDGE_SURFACE_PATH_COUNT={len(KCONFIG_BRIDGE_SURFACE_PATHS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CHECKER_SILENT_MARKER_COUNT={len(BRIDGE_CHECKER_LINE_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SILENT_CASE_COUNT={len(EXPECTED_SILENT_CONF_CASE_NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
