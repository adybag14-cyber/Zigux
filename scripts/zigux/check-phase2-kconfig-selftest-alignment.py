#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2.py"
PHASE2_CLOSURE_VALIDATOR = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
PHASE2_CLOSURE_DOC = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
PHASE2_BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CONFDATA_SURVEY = ROOT / "Documentation" / "zigux" / "phase2-confdata-bridge-survey.md"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
KCONFIG_BRIDGE_CONF_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
)
KCONFIG_BRIDGE_CONFDATA_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
)

VALIDATOR_MARKERS = (
    'ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py"',
    'ROOT / "scripts" / "zigux" / "check-phase2-confdata-helper-anchor-alignment.py"',
    'ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"',
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"',
    '"scripts/zigux/check-phase2-kconfig-selftest-alignment.py"',
    '"scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py --self-test"',
    '"scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py"',
    '"scripts/zigux/check-kconfig-bridge.py --self-test"',
    '"scripts/zigux/check-kconfig-bridge.py"',
    "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 28",
)

CLOSURE_VALIDATOR_MARKERS = (
    "shared kconfig selftest-alignment self-test",
    'KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"',
    "16-case` conf bridge plus `13-case` confdata fixture replay",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: python3 scripts/zigux/validate-phase2-closure.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
)

MAKEFILE_LINES = (
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-tests-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
)

SCRIPTS_README_MARKERS = (
    "check-phase2-kconfig-readme-alignment.py --self-test",
    "dedicated kconfig bridge checker packet documented through the shared Phase 2 reminder surface",
    "`check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, `validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`, `check-phase2-tests-readme-alignment.py`, `check-phase2-kconfig-readme-alignment.py`, `check-phase2-tool-manifest-packets.py`, `check-phase2-fixdep-gate.py`, `check-fixdep-diff.py`, `check-genksyms-bridge.py`, `check-phase2-cross.py`, `check-phase2-cross-selftest-alignment.py`, `check-phase2-kconfig-selftest-alignment.py`, `check-phase2-confdata-helper-anchor-alignment.py`, and `check-kconfig-bridge.py` are the live shared scripts-root Phase 2 helpers on current `master`",
)

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "the shipped direct kconfig bridge replays",
)

REVIEW_CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "make -C zigux phase2-kconfig",
)

PHASE2_CLOSURE_DOC_MARKERS = (
    "shared kconfig selftest-alignment self-test: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "shared kconfig selftest-alignment gate: `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "direct replay owners stay bounded on current `master`: `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` remain the shipped direct Phase 2 Zig replays",
)

PHASE2_BOOTSTRAP_NOTES_MARKERS = (
    "the closure note, tests root, and Makefile keep the committed `zigux/tests/fixtures/phase2_tool_manifest.json` plus `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` packet, the bounded direct `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` replays, and the committed genksyms bridge fixture plus kconfig manifest packet reviewable without reopening the dedicated genksyms or kconfig lanes from this bootstrap note",
    "the active Phase 2 closure note and Makefile keep the validator-routed direct `zig test scripts/zigux/fixdep.zig`, `zig test scripts/zigux/genksyms.zig`, `zig test scripts/zigux/kconfig/conf_bridge.zig`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` replays explicit beside the same bounded Phase 2 tools and kconfig routes",
)

PHASE2_CONFDATA_SURVEY_MARKERS = (
    "`zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 13 fixture cases",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` now keep the already-landed confdata bridge packet reviewable through the shared Phase 2 reminder surface",
)

PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS = (
    "11 fixture cases",
    "same 11-case packet",
)

EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT = 26
EXPECTED_CONF_CASE_COUNT = 16
EXPECTED_CONFDATA_CASE_COUNT = 13
EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT = 20
EXPECTED_SELF_TEST_CASE_COUNT = 18


def under_root(root: Path, path: Path) -> Path:
    return root / path.relative_to(ROOT)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def parse_python_assignments(text: str, names: tuple[str, ...]) -> dict[str, object]:
    module = ast.parse(text)
    values: dict[str, object] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name in names:
            values[name] = ast.literal_eval(node.value)
    return values


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def extract_case_names(cases: object, label: str, issues: list[tuple[str, str]]) -> list[str]:
    if not isinstance(cases, list):
        issues.append(("KCONFIG_CASE_PACKET_INVALID", f"{label}:expected_list"))
        return []
    names: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(("KCONFIG_CASE_PACKET_INVALID", f"{label}[{index}]:expected_object"))
            continue
        name = case.get("name")
        if not isinstance(name, str):
            issues.append(("KCONFIG_CASE_PACKET_INVALID", f"{label}[{index}].name:expected_string"))
            continue
        names.append(name)
    return names


def collect_kconfig_checker_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    assignments = parse_python_assignments(
        read_text(under_root(root, KCONFIG_BRIDGE_CHECKER)),
        (
            "REQUIRED_CONF_CASE_MODES",
            "REQUIRED_CONFDATA_CASES",
            "REQUIRED_CONFDATA_HELPER_ANCHORS",
            "EXPECTED_SELF_TEST_CASE_COUNT",
        ),
    )

    conf_modes = assignments.get("REQUIRED_CONF_CASE_MODES")
    if not isinstance(conf_modes, list) or len(conf_modes) != EXPECTED_CONF_CASE_COUNT:
        issues.append(("KCONFIG_CHECKER_CONF_CASE_COUNT_MISMATCH", repr(conf_modes)))

    confdata_cases = assignments.get("REQUIRED_CONFDATA_CASES")
    if not isinstance(confdata_cases, list) or len(confdata_cases) != EXPECTED_CONFDATA_CASE_COUNT:
        issues.append(("KCONFIG_CHECKER_CONFDATA_CASE_COUNT_MISMATCH", repr(confdata_cases)))

    helper_anchors = assignments.get("REQUIRED_CONFDATA_HELPER_ANCHORS")
    if not isinstance(helper_anchors, list) or len(helper_anchors) != EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT:
        issues.append(("KCONFIG_CHECKER_CONFDATA_HELPER_ANCHOR_COUNT_MISMATCH", repr(helper_anchors)))

    self_test_count = assignments.get("EXPECTED_SELF_TEST_CASE_COUNT")
    if self_test_count != EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT:
        issues.append(
            (
                "KCONFIG_CHECKER_SELF_TEST_COUNT_MISMATCH",
                f"actual={self_test_count!r}:expected={EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT}",
            )
        )

    cases_payload = read_json(under_root(root, KCONFIG_BRIDGE_CASES))
    if not isinstance(cases_payload, dict):
        return [("KCONFIG_CASE_PACKET_INVALID", "cases.json must decode to an object")]

    live_conf_names = extract_case_names(cases_payload.get("conf_cases"), "conf_cases", issues)
    live_confdata_names = extract_case_names(cases_payload.get("confdata_cases"), "confdata_cases", issues)

    if isinstance(conf_modes, list) and live_conf_names != conf_modes:
        issues.append(("KCONFIG_CASE_PACKET_NAME_MISMATCH", f"conf_cases:{live_conf_names!r}:{conf_modes!r}"))
    if isinstance(confdata_cases, list) and live_confdata_names != confdata_cases:
        issues.append(("KCONFIG_CASE_PACKET_NAME_MISMATCH", f"confdata_cases:{live_confdata_names!r}:{confdata_cases!r}"))

    conf_manifest = read_json(under_root(root, KCONFIG_BRIDGE_CONF_MANIFEST))
    confdata_manifest = read_json(under_root(root, KCONFIG_BRIDGE_CONFDATA_MANIFEST))
    if not isinstance(conf_manifest, dict) or conf_manifest.get("case_count") != EXPECTED_CONF_CASE_COUNT:
        issues.append(("KCONFIG_MANIFEST_CASE_COUNT_MISMATCH", "conf_manifest"))
    if not isinstance(confdata_manifest, dict) or confdata_manifest.get("case_count") != EXPECTED_CONFDATA_CASE_COUNT:
        issues.append(("KCONFIG_MANIFEST_CASE_COUNT_MISMATCH", "confdata_manifest"))
    if isinstance(confdata_manifest, dict):
        helper_list = confdata_manifest.get("helper_local_anchors")
        if not isinstance(helper_list, list) or len(helper_list) != EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT:
            issues.append(("KCONFIG_MANIFEST_PACKET_MISMATCH", "confdata_manifest:helper_local_anchors"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validator_text = read_text(under_root(root, PHASE2_VALIDATOR))
    issues.extend(collect_missing_markers(validator_text, VALIDATOR_MARKERS, "MISSING_VALIDATOR_MARKERS"))

    closure_validator_text = read_text(under_root(root, PHASE2_CLOSURE_VALIDATOR))
    issues.extend(
        collect_missing_markers(
            closure_validator_text, CLOSURE_VALIDATOR_MARKERS, "MISSING_CLOSURE_VALIDATOR_MARKERS"
        )
    )

    workflow_text = read_text(under_root(root, WORKFLOW))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    makefile_text = read_text(under_root(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    issues.extend(collect_missing_markers(read_text(under_root(root, SCRIPTS_README)), SCRIPTS_README_MARKERS, "MISSING_SCRIPTS_README_MARKERS"))
    issues.extend(collect_missing_markers(read_text(under_root(root, TESTS_README)), TESTS_README_MARKERS, "MISSING_TESTS_README_MARKERS"))
    issues.extend(collect_missing_markers(read_text(under_root(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_MARKERS, "MISSING_REVIEW_CHECKLIST_MARKERS"))
    issues.extend(collect_missing_markers(read_text(under_root(root, PHASE2_CLOSURE_DOC)), PHASE2_CLOSURE_DOC_MARKERS, "MISSING_CLOSURE_DOC_MARKERS"))
    issues.extend(collect_missing_markers(read_text(under_root(root, PHASE2_BOOTSTRAP_NOTES)), PHASE2_BOOTSTRAP_NOTES_MARKERS, "MISSING_BOOTSTRAP_NOTES_MARKERS"))

    confdata_survey_text = read_text(under_root(root, PHASE2_CONFDATA_SURVEY))
    issues.extend(collect_missing_markers(confdata_survey_text, PHASE2_CONFDATA_SURVEY_MARKERS, "MISSING_CONFDATA_SURVEY_MARKERS"))
    issues.extend(
        collect_forbidden_markers(
            confdata_survey_text,
            PHASE2_CONFDATA_SURVEY_FORBIDDEN_MARKERS,
            "FORBIDDEN_CONFDATA_SURVEY_MARKERS",
        )
    )

    issues.extend(collect_kconfig_checker_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)
    print("PHASE2_KCONFIG_ALIGNMENT=fail")
    for code, details in grouped.items():
        print(f"{code}_START")
        for detail in details:
            print(detail)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(under_root(root, PHASE2_VALIDATOR), "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(under_root(root, PHASE2_CLOSURE_VALIDATOR), "\n".join(CLOSURE_VALIDATOR_MARKERS) + "\n")
    write_text(under_root(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(under_root(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(under_root(root, SCRIPTS_README), "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write_text(under_root(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    write_text(under_root(root, REVIEW_CHECKLIST), "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    write_text(under_root(root, PHASE2_CLOSURE_DOC), "\n".join(PHASE2_CLOSURE_DOC_MARKERS) + "\n")
    write_text(under_root(root, PHASE2_BOOTSTRAP_NOTES), "\n".join(PHASE2_BOOTSTRAP_NOTES_MARKERS) + "\n")
    write_text(under_root(root, PHASE2_CONFDATA_SURVEY), "\n".join(PHASE2_CONFDATA_SURVEY_MARKERS) + "\n")

    checker_source = "\n".join(
        [
            "REQUIRED_CONF_CASE_MODES = [",
            *[f'    "{name}",' for name in ("oldaskconfig", "syncconfig", "oldconfig", "allnoconfig", "allyesconfig", "allmodconfig", "alldefconfig", "randconfig", "defconfig", "savedefconfig", "listnewconfig", "helpnewconfig", "olddefconfig", "yes2modconfig", "mod2yesconfig", "mod2noconfig")],
            "]",
            "REQUIRED_CONFDATA_CASES = [",
            *[f'    "{name}",' for name in ("sample", "escaped_strings", "escaped_control_sequences", "trailing_escaped_backslash", "sample_crlf", "explicit_n_tristate", "final_trailing_carriage_return", "final_unterminated_unset_comment", "uppercase_tristate", "non_config_lines", "empty_config_symbol_names", "last_state_transitions", "duplicate_malformed_quoted_assignment")],
            "]",
            "REQUIRED_CONFDATA_HELPER_ANCHORS = [",
            *[f'    "anchor_{index}",' for index in range(EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT)],
            "]",
            f"EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT}",
            "",
        ]
    )
    write_text(under_root(root, KCONFIG_BRIDGE_CHECKER), checker_source)

    cases_payload = {
        "conf_cases": [{"name": name} for name in ("oldaskconfig", "syncconfig", "oldconfig", "allnoconfig", "allyesconfig", "allmodconfig", "alldefconfig", "randconfig", "defconfig", "savedefconfig", "listnewconfig", "helpnewconfig", "olddefconfig", "yes2modconfig", "mod2yesconfig", "mod2noconfig")],
        "confdata_cases": [{"name": name} for name in ("sample", "escaped_strings", "escaped_control_sequences", "trailing_escaped_backslash", "sample_crlf", "explicit_n_tristate", "final_trailing_carriage_return", "final_unterminated_unset_comment", "uppercase_tristate", "non_config_lines", "empty_config_symbol_names", "last_state_transitions", "duplicate_malformed_quoted_assignment")],
    }
    write_text(under_root(root, KCONFIG_BRIDGE_CASES), json.dumps(cases_payload, indent=2) + "\n")
    write_text(
        under_root(root, KCONFIG_BRIDGE_CONF_MANIFEST),
        json.dumps({"case_count": EXPECTED_CONF_CASE_COUNT, "cases": [case["name"] for case in cases_payload["conf_cases"]]}, indent=2) + "\n",
    )
    write_text(
        under_root(root, KCONFIG_BRIDGE_CONFDATA_MANIFEST),
        json.dumps(
            {
                "case_count": EXPECTED_CONFDATA_CASE_COUNT,
                "cases": [case["name"] for case in cases_payload["confdata_cases"]],
                "helper_local_anchors": [f"anchor_{index}" for index in range(EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT)],
            },
            indent=2,
        ) + "\n",
    )


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, PHASE2_VALIDATOR), replace_once(read_text(under_root(root, PHASE2_VALIDATOR)), VALIDATOR_MARKERS[1], ""))
        assert ("MISSING_VALIDATOR_MARKERS", VALIDATOR_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(
            under_root(root, PHASE2_VALIDATOR),
            replace_once(read_text(under_root(root, PHASE2_VALIDATOR)), VALIDATOR_MARKERS[-1], "PHASE2_VALIDATION_EXPECTED_COMMAND_COUNT = 26"),
        )
        assert ("MISSING_VALIDATOR_MARKERS", VALIDATOR_MARKERS[-1]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, SCRIPTS_README), replace_once(read_text(under_root(root, SCRIPTS_README)), SCRIPTS_README_MARKERS[2], ""))
        assert ("MISSING_SCRIPTS_README_MARKERS", SCRIPTS_README_MARKERS[2]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, WORKFLOW), replace_once(read_text(under_root(root, WORKFLOW)), WORKFLOW_LINES[6], ""))
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[6]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, WORKFLOW), read_text(under_root(root, WORKFLOW)) + WORKFLOW_LINES[2] + "\n")
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{WORKFLOW_LINES[2]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, WORKFLOW), replace_once(read_text(under_root(root, WORKFLOW)), WORKFLOW_LINES[10], ""))
        assert ("MISSING_WORKFLOW_HOOKS", WORKFLOW_LINES[10]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, WORKFLOW), read_text(under_root(root, WORKFLOW)) + WORKFLOW_LINES[11] + "\n")
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{WORKFLOW_LINES[11]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, MAKEFILE), read_text(under_root(root, MAKEFILE)) + MAKEFILE_LINES[3] + "\n")
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{MAKEFILE_LINES[3]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(read_text(under_root(root, KCONFIG_BRIDGE_CASES)))
        payload["conf_cases"].pop()
        write_text(under_root(root, KCONFIG_BRIDGE_CASES), json.dumps(payload, indent=2) + "\n")
        assert any(code == "KCONFIG_CASE_PACKET_NAME_MISMATCH" or code == "KCONFIG_CHECKER_CONF_CASE_COUNT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        payload = json.loads(read_text(under_root(root, KCONFIG_BRIDGE_CASES)))
        payload["confdata_cases"].pop()
        write_text(under_root(root, KCONFIG_BRIDGE_CASES), json.dumps(payload, indent=2) + "\n")
        assert any(code == "KCONFIG_CASE_PACKET_NAME_MISMATCH" or code == "KCONFIG_CHECKER_CONFDATA_CASE_COUNT_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        write_text(
            under_root(root, KCONFIG_BRIDGE_CHECKER),
            replace_once(
                read_text(under_root(root, KCONFIG_BRIDGE_CHECKER)),
                f"EXPECTED_SELF_TEST_CASE_COUNT = {EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT}",
                "EXPECTED_SELF_TEST_CASE_COUNT = 20",
            ),
        )
        assert (
            "KCONFIG_CHECKER_SELF_TEST_COUNT_MISMATCH",
            f"actual=20:expected={EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT}",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, PHASE2_CONFDATA_SURVEY), read_text(under_root(root, PHASE2_CONFDATA_SURVEY)) + "\n11 fixture cases\n")
        assert ("FORBIDDEN_CONFDATA_SURVEY_MARKERS", "11 fixture cases") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(under_root(root, KCONFIG_BRIDGE_CONFDATA_MANIFEST)))
        manifest["helper_local_anchors"] = manifest["helper_local_anchors"][:-1]
        write_text(under_root(root, KCONFIG_BRIDGE_CONFDATA_MANIFEST), json.dumps(manifest, indent=2) + "\n")
        assert ("KCONFIG_MANIFEST_PACKET_MISMATCH", "confdata_manifest:helper_local_anchors") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        write_text(under_root(root, REVIEW_CHECKLIST), replace_once(read_text(under_root(root, REVIEW_CHECKLIST)), REVIEW_CHECKLIST_MARKERS[1], ""))
        assert ("MISSING_REVIEW_CHECKLIST_MARKERS", REVIEW_CHECKLIST_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        for marker in PHASE2_CLOSURE_DOC_MARKERS:
            build_self_test_root(root)
            write_text(
                under_root(root, PHASE2_CLOSURE_DOC),
                replace_once(read_text(under_root(root, PHASE2_CLOSURE_DOC)), marker, ""),
            )
            assert ("MISSING_CLOSURE_DOC_MARKERS", marker) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 kconfig packet stays aligned with the live validator, checker, docs, tests, workflow, and make surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_EXPECTED_CONF_CASE_COUNT={EXPECTED_CONF_CASE_COUNT}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_EXPECTED_CONFDATA_CASE_COUNT={EXPECTED_CONFDATA_CASE_COUNT}")
    print(
        "PHASE2_KCONFIG_ALIGNMENT_EXPECTED_CHECKER_SELF_TEST_CASE_COUNT="
        f"{EXPECTED_KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
