#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
KCONFIG_BRIDGE_CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
CONFDATA_MANIFEST = (
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
)
CONFDATA_SURVEY = ROOT / "Documentation" / "zigux" / "phase2-confdata-bridge-survey.md"

EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT = 20
EXPECTED_CONFDATA_CASE_COUNT = 13
EXPECTED_SELF_TEST_CASE_COUNT = 21

SELFTEST_CONFDATA_CASE_NAMES = (
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
    "empty_config_symbol_names",
    "last_state_transitions",
    "duplicate_malformed_quoted_assignment",
)

SELFTEST_CONFDATA_HELPER_ANCHORS = (
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge decodes escaped quoted strings",
    "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
    "confdata bridge escapes low control bytes in json output",
    "confdata bridge accepts CRLF config lines",
    "confdata bridge preserves trailing carriage return on final unterminated value line",
    "confdata bridge ignores unterminated unset comment with trailing carriage return",
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
    "confdata bridge keeps only the last state across unset and set transitions",
)

REQUIRED_SURVEY_MARKERS = (
    "`20` helper-local tests covering the current bridge-local edge cases.",
    "`confdata_cases` packet with 13 fixture cases:",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
    "`scripts/zigux/check-kconfig-bridge.py` gate plus the direct `zig test scripts/zigux/kconfig/confdata_bridge.zig` replay",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def parse_python_assignments(text: str, names: tuple[str, ...]) -> dict[str, object]:
    module = ast.parse(text)
    values: dict[str, object] = {}
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        target = node.targets[0].id
        if target not in names:
            continue
        values[target] = ast.literal_eval(node.value)
    return values


def extract_zig_test_anchors(text: str) -> list[str]:
    return re.findall(r'^test "([^"]+)" \{$', text, re.M)


def extract_confdata_case_packet(payload: object) -> tuple[list[str], list[str], list[str], list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    names: list[str] = []
    input_packet: list[str] = []
    expected_packet: list[str] = []

    if not isinstance(payload, list):
        issues.append(("CONFDATA_CASE_PACKET_INVALID", "confdata_cases:expected_list"))
        return names, input_packet, expected_packet, issues

    for index, case in enumerate(payload):
        if not isinstance(case, dict):
            issues.append(("CONFDATA_CASE_PACKET_INVALID", f"confdata_cases[{index}]:expected_object"))
            continue

        name = case.get("name")
        if not isinstance(name, str):
            issues.append(("CONFDATA_CASE_PACKET_INVALID", f"confdata_cases[{index}].name:expected_string"))
            continue

        input_path = case.get("input")
        if not isinstance(input_path, str):
            issues.append(("CONFDATA_CASE_PACKET_INVALID", f"confdata_cases[{index}].input:expected_string"))
            continue

        expected_path = case.get("expected")
        if not isinstance(expected_path, str):
            issues.append(("CONFDATA_CASE_PACKET_INVALID", f"confdata_cases[{index}].expected:expected_string"))
            continue

        names.append(name)
        input_packet.append(input_path)
        expected_packet.append(expected_path)

    return names, input_packet, expected_packet, issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    expected_case_names = list(SELFTEST_CONFDATA_CASE_NAMES)

    checker_text = read_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER))
    assignments = parse_python_assignments(
        checker_text,
        ("REQUIRED_CONFDATA_HELPER_ANCHORS", "REQUIRED_CONFDATA_CASES"),
    )

    checker_case_names = assignments.get("REQUIRED_CONFDATA_CASES")
    if not isinstance(checker_case_names, list):
        issues.append(("CONFDATA_CASE_CHECKER_LIST_INVALID", repr(checker_case_names)))
        checker_case_names = []
    else:
        if len(checker_case_names) != EXPECTED_CONFDATA_CASE_COUNT:
            issues.append(
                (
                    "CONFDATA_CASE_CHECKER_COUNT_MISMATCH",
                    f"actual={len(checker_case_names)}:expected={EXPECTED_CONFDATA_CASE_COUNT}",
                )
            )
        if checker_case_names != expected_case_names:
            issues.append(
                (
                    "CONFDATA_CASE_CHECKER_NAME_MISMATCH",
                    f"actual={checker_case_names!r}:expected={expected_case_names!r}",
                )
            )

    checker_helper_anchors = assignments.get("REQUIRED_CONFDATA_HELPER_ANCHORS")
    if not isinstance(checker_helper_anchors, list):
        issues.append(
            ("CONFDATA_HELPER_ANCHOR_CHECKER_LIST_INVALID", repr(checker_helper_anchors))
        )
        checker_helper_anchors = []
    elif len(checker_helper_anchors) != EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT:
        issues.append(
            (
                "CONFDATA_HELPER_ANCHOR_CHECKER_COUNT_MISMATCH",
                "actual="
                f"{len(checker_helper_anchors)}:expected={EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT}",
            )
        )

    source_text = read_text(resolve_path(root, CONFDATA_BRIDGE))
    source_helper_anchors = extract_zig_test_anchors(source_text)
    if len(source_helper_anchors) != EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT:
        issues.append(
            (
                "CONFDATA_HELPER_ANCHOR_SOURCE_COUNT_MISMATCH",
                "actual="
                f"{len(source_helper_anchors)}:expected={EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT}",
            )
        )
    if checker_helper_anchors and source_helper_anchors != checker_helper_anchors:
        issues.append(
            (
                "CONFDATA_HELPER_ANCHOR_SOURCE_NAME_MISMATCH",
                f"actual={source_helper_anchors!r}:expected={checker_helper_anchors!r}",
            )
        )

    cases_payload = read_json(resolve_path(root, KCONFIG_BRIDGE_CASES))
    confdata_case_names: list[str] = []
    confdata_input_packet: list[str] = []
    confdata_expected_packet: list[str] = []
    if not isinstance(cases_payload, dict):
        issues.append(("CONFDATA_CASE_PACKET_INVALID", "cases.json must decode to an object"))
    else:
        (
            confdata_case_names,
            confdata_input_packet,
            confdata_expected_packet,
            case_issues,
        ) = extract_confdata_case_packet(cases_payload.get("confdata_cases"))
        issues.extend(case_issues)

    if len(confdata_case_names) != EXPECTED_CONFDATA_CASE_COUNT:
        issues.append(
            (
                "CONFDATA_CASE_PACKET_COUNT_MISMATCH",
                f"actual={len(confdata_case_names)}:expected={EXPECTED_CONFDATA_CASE_COUNT}",
            )
        )
    if confdata_case_names and confdata_case_names != expected_case_names:
        issues.append(
            (
                "CONFDATA_CASE_PACKET_NAME_MISMATCH",
                f"actual={confdata_case_names!r}:expected={expected_case_names!r}",
            )
        )
    if checker_case_names and confdata_case_names and confdata_case_names != checker_case_names:
        issues.append(
            (
                "CONFDATA_CASE_PACKET_CHECKER_NAME_MISMATCH",
                f"actual={confdata_case_names!r}:expected={checker_case_names!r}",
            )
        )

    manifest = read_json(resolve_path(root, CONFDATA_MANIFEST))
    if not isinstance(manifest, dict):
        issues.append(
            ("CONFDATA_HELPER_ANCHOR_MANIFEST_INVALID", "confdata_manifest.json must decode to an object")
        )
        return issues

    manifest_helper_anchors = manifest.get("helper_local_anchors")
    if not isinstance(manifest_helper_anchors, list):
        issues.append(
            ("CONFDATA_HELPER_ANCHOR_MANIFEST_LIST_INVALID", repr(manifest_helper_anchors))
        )
        manifest_helper_anchors = []
    elif len(manifest_helper_anchors) != EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT:
        issues.append(
            (
                "CONFDATA_HELPER_ANCHOR_MANIFEST_COUNT_MISMATCH",
                "actual="
                f"{len(manifest_helper_anchors)}:expected={EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT}",
            )
        )

    if checker_helper_anchors and manifest_helper_anchors != checker_helper_anchors:
        issues.append(
            (
                "CONFDATA_HELPER_ANCHOR_MANIFEST_NAME_MISMATCH",
                f"actual={manifest_helper_anchors!r}:expected={checker_helper_anchors!r}",
            )
        )

    manifest_case_count = manifest.get("case_count")
    if manifest_case_count != EXPECTED_CONFDATA_CASE_COUNT:
        issues.append(
            (
                "CONFDATA_CASE_MANIFEST_COUNT_MISMATCH",
                f"actual={manifest_case_count!r}:expected={EXPECTED_CONFDATA_CASE_COUNT}",
            )
        )

    manifest_cases = manifest.get("cases")
    if not isinstance(manifest_cases, list):
        issues.append(("CONFDATA_CASE_MANIFEST_CASES_INVALID", repr(manifest_cases)))
    elif manifest_cases != confdata_case_names:
        issues.append(
            (
                "CONFDATA_CASE_MANIFEST_CASES_MISMATCH",
                f"actual={manifest_cases!r}:expected={confdata_case_names!r}",
            )
        )

    manifest_input_packet = manifest.get("input_packet")
    if not isinstance(manifest_input_packet, list):
        issues.append(("CONFDATA_CASE_MANIFEST_INPUT_PACKET_INVALID", repr(manifest_input_packet)))
    elif manifest_input_packet != confdata_input_packet:
        issues.append(
            (
                "CONFDATA_CASE_MANIFEST_INPUT_PACKET_MISMATCH",
                f"actual={manifest_input_packet!r}:expected={confdata_input_packet!r}",
            )
        )

    manifest_expected_packet = manifest.get("expected_packet")
    if not isinstance(manifest_expected_packet, list):
        issues.append(("CONFDATA_CASE_MANIFEST_EXPECTED_PACKET_INVALID", repr(manifest_expected_packet)))
    elif manifest_expected_packet != confdata_expected_packet:
        issues.append(
            (
                "CONFDATA_CASE_MANIFEST_EXPECTED_PACKET_MISMATCH",
                f"actual={manifest_expected_packet!r}:expected={confdata_expected_packet!r}",
            )
        )

    survey_text = read_text(resolve_path(root, CONFDATA_SURVEY))
    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(("CONFDATA_HELPER_ANCHOR_SURVEY_MISSING_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)

    print("PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT=fail")
    for code, details in grouped.items():
        print(f"{code}_START")
        for detail in details:
            print(detail)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_checker_source(
    case_names: tuple[str, ...] = SELFTEST_CONFDATA_CASE_NAMES,
    anchors: tuple[str, ...] = SELFTEST_CONFDATA_HELPER_ANCHORS,
) -> str:
    lines = ["REQUIRED_CONFDATA_CASES = ["]
    lines.extend(f'    "{name}",' for name in case_names)
    lines.append("]")
    lines.append("")
    lines.append("REQUIRED_CONFDATA_HELPER_ANCHORS = [")
    lines.extend(f'    "{anchor}",' for anchor in anchors)
    lines.append("]")
    return "\n".join(lines) + "\n"


def render_confdata_bridge_source(anchors: tuple[str, ...] = SELFTEST_CONFDATA_HELPER_ANCHORS) -> str:
    blocks = [
        'const std = @import("std");\n',
    ]
    for anchor in anchors:
        blocks.append(f'\ntest "{anchor}" {{\n    try std.testing.expect(true);\n}}\n')
    return "".join(blocks)


def render_confdata_survey() -> str:
    return "\n".join(
        (
            "# Phase 2 Confdata Bridge Survey",
            "",
            "- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary, alongside `20` helper-local tests covering the current bridge-local edge cases.",
            "- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 13 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, `last_state_transitions`, and `duplicate_malformed_quoted_assignment`.",
            "- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
            "- `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already describe the same shared kconfig packet and keep the bridge reviewable through the shared `scripts/zigux/check-kconfig-bridge.py` gate plus the direct `zig test scripts/zigux/kconfig/confdata_bridge.zig` replay instead of implying either current-`master` surface is missing.",
            "",
        )
    )


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, KCONFIG_BRIDGE_CHECKER), render_checker_source())
    write_text(resolve_path(root, CONFDATA_BRIDGE), render_confdata_bridge_source())
    write_text(
        resolve_path(root, KCONFIG_BRIDGE_CASES),
        json.dumps(
            {
                "confdata_cases": [
                    {
                        "name": name,
                        "input": f"{name}.config",
                        "expected": f"{name}_expected.json",
                    }
                    for name in SELFTEST_CONFDATA_CASE_NAMES
                ]
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CONFDATA_MANIFEST),
        json.dumps(
            {
                "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
                "case_count": EXPECTED_CONFDATA_CASE_COUNT,
                "cases": list(SELFTEST_CONFDATA_CASE_NAMES),
                "input_packet": [f"{name}.config" for name in SELFTEST_CONFDATA_CASE_NAMES],
                "expected_packet": [f"{name}_expected.json" for name in SELFTEST_CONFDATA_CASE_NAMES],
                "helper_local_anchors": list(SELFTEST_CONFDATA_HELPER_ANCHORS),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, CONFDATA_SURVEY), render_confdata_survey())


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_confdata_anchor_alignment_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                '    "confdata bridge keeps only the last state across unset and set transitions",\n',
                "",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_CHECKER_COUNT_MISMATCH",
            "actual=19:expected=20",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_BRIDGE)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                'test "confdata bridge emits bounded json output" {\n',
                'test "confdata bridge emits reordered json output" {\n',
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_HELPER_ANCHOR_SOURCE_NAME_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["helper_local_anchors"][-1] = "renamed_confdata_anchor"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_HELPER_ANCHOR_MANIFEST_NAME_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["helper_local_anchors"] = payload["helper_local_anchors"][:-1]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_MANIFEST_COUNT_MISMATCH",
            "actual=19:expected=20",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_SURVEY)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                "`20` helper-local tests covering the current bridge-local edge cases.",
                "`19` helper-local tests covering the current bridge-local edge cases.",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_SURVEY_MISSING_MARKER",
            "`20` helper-local tests covering the current bridge-local edge cases.",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_SURVEY)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                "`confdata_cases` packet with 13 fixture cases:",
                "`confdata_cases` packet with 12 fixture cases:",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_SURVEY_MISSING_MARKER",
            "`confdata_cases` packet with 13 fixture cases:",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_SURVEY)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
                "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, records the same packet, and names the helper-local anchor list for the bridge tests.",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_SURVEY_MISSING_MARKER",
            "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_SURVEY)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-kconfig-bridge.py` gate plus the direct `zig test scripts/zigux/kconfig/confdata_bridge.zig` replay",
                "`scripts/zigux/check-kconfig-bridge.py` gate plus the shared confdata replay",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_HELPER_ANCHOR_SURVEY_MISSING_MARKER",
            "`scripts/zigux/check-kconfig-bridge.py` gate plus the direct `zig test scripts/zigux/kconfig/confdata_bridge.zig` replay",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                '    "duplicate_malformed_quoted_assignment",\n',
                "",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert (
            "CONFDATA_CASE_CHECKER_COUNT_MISMATCH",
            "actual=12:expected=13",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CHECKER)
        path.write_text(
            replace_once(
                path.read_text(encoding="utf-8"),
                '    "sample",\n',
                '    "renamed_sample",\n',
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_CASE_CHECKER_NAME_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["confdata_cases"] = payload["confdata_cases"][:-1]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CONFDATA_CASE_PACKET_COUNT_MISMATCH",
            "actual=12:expected=13",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, KCONFIG_BRIDGE_CASES)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0], payload["confdata_cases"][1] = (
            payload["confdata_cases"][1],
            payload["confdata_cases"][0],
        )
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_CASE_PACKET_NAME_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 12
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CONFDATA_CASE_MANIFEST_COUNT_MISMATCH",
            "actual=12:expected=13",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][-1] = "renamed_case"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_CASE_MANIFEST_CASES_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["input_packet"][-1] = "renamed_input.config"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_CASE_MANIFEST_INPUT_PACKET_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CONFDATA_MANIFEST)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["expected_packet"][-1] = "renamed_expected.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(
            code == "CONFDATA_CASE_MANIFEST_EXPECTED_PACKET_MISMATCH"
            for code, _ in issues
        )
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, KCONFIG_BRIDGE_CHECKER).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing checker file did not abort")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, CONFDATA_BRIDGE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing source file did not abort")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, CONFDATA_MANIFEST).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing manifest file did not abort")
        checks_run += 1

        build_self_test_root(root)
        resolve_path(root, CONFDATA_SURVEY).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing survey file did not abort")
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 confdata helper-local anchor and fixture packet stay aligned across the live checker, source, manifest, and survey note."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT=pass")
    print(
        "PHASE2_CONFDATA_HELPER_ANCHOR_ALIGNMENT_EXPECTED_COUNT="
        f"{EXPECTED_CONFDATA_HELPER_ANCHOR_COUNT}"
    )
    print(
        "PHASE2_CONFDATA_CASE_ALIGNMENT_EXPECTED_COUNT="
        f"{EXPECTED_CONFDATA_CASE_COUNT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
