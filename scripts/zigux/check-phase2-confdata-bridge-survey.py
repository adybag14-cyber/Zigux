#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
CASES = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json"
MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json"
SURVEY = ROOT / "Documentation" / "zigux" / "phase2-confdata-bridge-survey.md"

EXPECTED_SELF_TEST_CASE_COUNT = 4


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(read_text(path))


def count_test_anchors(bridge_text: str) -> list[str]:
    anchors = re.findall(r'^test "([^"]+)" \{$', bridge_text, re.M)
    if not anchors:
        raise SystemExit("failed to discover confdata bridge test anchors")
    return anchors


def load_confdata_cases(payload: object) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        raise SystemExit("cases payload must be a JSON object")
    raw_cases = payload.get("confdata_cases")
    if not isinstance(raw_cases, list):
        raise SystemExit("confdata_cases must be a JSON array")

    cases: list[dict[str, str]] = []
    for index, case in enumerate(raw_cases):
        if not isinstance(case, dict):
            raise SystemExit(f"confdata_cases[{index}] must be a JSON object")
        name = case.get("name")
        input_name = case.get("input")
        expected_name = case.get("expected")
        if not all(isinstance(value, str) for value in (name, input_name, expected_name)):
            raise SystemExit(f"confdata_cases[{index}] must use string name/input/expected fields")
        cases.append({"name": name, "input": input_name, "expected": expected_name})
    return cases


def required_survey_markers(anchor_count: int, case_count: int, case_names: list[str]) -> tuple[str, ...]:
    return (
        "scripts/zigux/kconfig/confdata_bridge.zig",
        f"`{anchor_count}` helper-local tests",
        f"`confdata_cases` packet with {case_count} fixture cases",
        f"The live `{anchor_count}`-anchor and `{case_count}`-case confdata packet",
        "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
        "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "zig test scripts/zigux/kconfig/confdata_bridge.zig",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        case_names[-2],
        case_names[-1],
    )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    bridge_text = read_text(root / BRIDGE.relative_to(ROOT))
    survey_text = read_text(root / SURVEY.relative_to(ROOT))
    cases_payload = read_json(root / CASES.relative_to(ROOT))
    manifest = read_json(root / MANIFEST.relative_to(ROOT))

    issues: list[tuple[str, str]] = []
    anchors = count_test_anchors(bridge_text)
    cases = load_confdata_cases(cases_payload)

    if not isinstance(manifest, dict):
        return [("INVALID_CONFDATA_MANIFEST_PAYLOAD", type(manifest).__name__)]

    case_names = [case["name"] for case in cases]
    input_packet = [case["input"] for case in cases]
    expected_packet = [case["expected"] for case in cases]

    expected_manifest_fields = {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": len(cases),
        "cases": case_names,
        "input_packet": input_packet,
        "expected_packet": expected_packet,
        "helper_local_anchors": anchors,
    }

    for field_name, expected_value in expected_manifest_fields.items():
        if manifest.get(field_name) != expected_value:
            issues.append(
                (
                    "CONFDATA_MANIFEST_FIELD_MISMATCH",
                    f"{field_name}:actual={manifest.get(field_name)!r}:expected={expected_value!r}",
                )
            )

    for marker in required_survey_markers(len(anchors), len(cases), case_names):
        if marker not in survey_text:
            issues.append(("MISSING_CONFDATA_SURVEY_MARKERS", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CONFDATA_SURVEY_ALIGNMENT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    bridge = """\
test \"confdata bridge parses bounded config states\" {
}
test \"confdata bridge emits bounded json output\" {
}
test \"confdata bridge duplicate assignments coverage\" {
}
test \"confdata bridge duplicate malformed quoted assignment coverage\" {
}
"""
    cases = {
        "confdata_cases": [
            {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
            {
                "name": "duplicate_assignments",
                "input": "duplicate_assignments.config",
                "expected": "duplicate_assignments_expected.json",
            },
            {
                "name": "duplicate_malformed_quoted_assignment",
                "input": "duplicate_malformed_quoted_assignment.config",
                "expected": "duplicate_malformed_quoted_assignment_expected.json",
            },
        ]
    }
    manifest = {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": 3,
        "cases": [
            "sample",
            "duplicate_assignments",
            "duplicate_malformed_quoted_assignment",
        ],
        "input_packet": [
            "sample.config",
            "duplicate_assignments.config",
            "duplicate_malformed_quoted_assignment.config",
        ],
        "expected_packet": [
            "sample_expected.json",
            "duplicate_assignments_expected.json",
            "duplicate_malformed_quoted_assignment_expected.json",
        ],
        "helper_local_anchors": [
            "confdata bridge parses bounded config states",
            "confdata bridge emits bounded json output",
            "confdata bridge duplicate assignments coverage",
            "confdata bridge duplicate malformed quoted assignment coverage",
        ],
    }
    survey = """\
# Phase 2 Confdata Bridge Survey

`scripts/zigux/kconfig/confdata_bridge.zig` ships `4` helper-local tests.
The current `confdata_cases` packet with 3 fixture cases stays aligned to `zigux/tests/fixtures/kconfig_bridge/cases.json`.
The live `4`-anchor and `3`-case confdata packet remains reviewable through `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`.
Duplicate packet coverage includes `duplicate_assignments` and `duplicate_malformed_quoted_assignment`.
Replay routes: `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig`.
"""

    write_text(root / BRIDGE.relative_to(ROOT), bridge)
    write_text(root / CASES.relative_to(ROOT), json.dumps(cases, indent=2) + "\n")
    write_text(root / MANIFEST.relative_to(ROOT), json.dumps(manifest, indent=2) + "\n")
    write_text(root / SURVEY.relative_to(ROOT), survey)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_confdata_survey_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        survey_path = root / SURVEY.relative_to(ROOT)
        survey_path.write_text(survey_path.read_text(encoding="utf-8").replace("`4` helper-local tests", "`3` helper-local tests"), encoding="utf-8")
        assert ("MISSING_CONFDATA_SURVEY_MARKERS", "`4` helper-local tests") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / MANIFEST.relative_to(ROOT)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["case_count"] = 2
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "CONFDATA_MANIFEST_FIELD_MISMATCH" and value.startswith("case_count:") for code, value in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        survey_path = root / SURVEY.relative_to(ROOT)
        survey_path.write_text(survey_path.read_text(encoding="utf-8").replace("duplicate_malformed_quoted_assignment", "missing_duplicate_case"), encoding="utf-8")
        assert ("MISSING_CONFDATA_SURVEY_MARKERS", "duplicate_malformed_quoted_assignment") in collect_issues(root)
        checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CONFDATA_SURVEY_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CONFDATA_SURVEY_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 confdata bridge survey stays aligned with the live bridge, fixture, and manifest packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    bridge_text = read_text((args.root.resolve() / BRIDGE.relative_to(ROOT)))
    cases = load_confdata_cases(read_json(args.root.resolve() / CASES.relative_to(ROOT)))
    print("PHASE2_CONFDATA_SURVEY_ALIGNMENT=pass")
    print(f"PHASE2_CONFDATA_SURVEY_ALIGNMENT_HELPER_ANCHOR_COUNT={len(count_test_anchors(bridge_text))}")
    print(f"PHASE2_CONFDATA_SURVEY_ALIGNMENT_CASE_COUNT={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
