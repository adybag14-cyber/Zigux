#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
BRIDGE_CHECKER = Path("scripts/zigux/check-genksyms-bridge.py")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
BRIDGE_CASES = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
BRIDGE_MANIFEST = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
BRIDGE_MANIFEST_PATH = "zigux/tests/fixtures/genksyms_bridge/manifest.json"

REQUIRED_BRIDGE_MARKERS = (
    "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
    "print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def load_json(path: Path) -> object:
    return json.loads(read_text(path))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def collect_expected_manifest_payload(root: Path) -> tuple[dict[str, object] | None, list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    cases_path = root / BRIDGE_CASES
    manifest = load_json(cases_path)
    if not isinstance(manifest, dict):
        return None, [("CASE_PAYLOAD_ISSUES", "cases.json:expected_object")]

    cases = manifest.get("cases")
    if not isinstance(cases, list):
        return None, [("CASE_PAYLOAD_ISSUES", "cases.json:cases:expected_list")]

    case_names: list[str] = []
    stdout_packet: list[str] = []
    process_packet: list[str] = []
    normalized_stderr_packet: list[str] = []
    action_abbrev_cases: list[str] = []
    seen_names: set[str] = set()

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            issues.append(("CASE_PAYLOAD_ISSUES", f"cases[{index}]:expected_object"))
            continue

        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(("CASE_PAYLOAD_ISSUES", f"cases[{index}]:name:expected_nonempty_string"))
            continue
        if name in seen_names:
            issues.append(("CASE_PAYLOAD_ISSUES", f"duplicate_case_name:{name}"))
            continue
        seen_names.add(name)

        expected = case.get("expected")
        if not isinstance(expected, str) or not expected:
            issues.append(("CASE_PAYLOAD_ISSUES", f"{name}:expected:expected_nonempty_string"))
            continue

        mode = case.get("mode", "stdout_json")
        if mode not in {"stdout_json", "process_json"}:
            issues.append(("CASE_PAYLOAD_ISSUES", f"{name}:unsupported_mode:{mode}"))
            continue

        case_names.append(name)
        if mode == "stdout_json":
            stdout_packet.append(expected)
        else:
            process_packet.append(expected)
            if bool(case.get("normalize_stderr", False)):
                normalized_stderr_packet.append(expected)
            if name.startswith("abbreviated_"):
                action_abbrev_cases.append(name)

    if issues:
        return None, issues

    payload = {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "wrapper-first bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "harness": "zigux/tests/fixtures/genksyms_bridge/genksyms_bridge_c_harness.c",
        "case_count": len(case_names),
        "cases": case_names,
        "stdout_packet": ordered_unique(stdout_packet),
        "process_packet": ordered_unique(process_packet),
        "normalized_stderr_packet": ordered_unique(normalized_stderr_packet),
        "action_abbrev_cases": ordered_unique(action_abbrev_cases),
    }
    return payload, []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    bridge_text = read_text(root / BRIDGE_CHECKER)
    workflow_text = read_text(root / WORKFLOW)

    for marker in REQUIRED_BRIDGE_MARKERS:
        if marker not in bridge_text:
            issues.append(("MISSING_BRIDGE_MARKERS", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    manifest_path = root / BRIDGE_MANIFEST
    cases_path = root / BRIDGE_CASES
    phase2_tool_manifest_path = root / PHASE2_TOOL_MANIFEST
    for path in (manifest_path, cases_path, phase2_tool_manifest_path):
        if not path.exists():
            issues.append(("MISSING_MANIFEST_FILES", str(path.relative_to(root))))
    if any(block == "MISSING_MANIFEST_FILES" for block, _ in issues):
        return issues

    expected_manifest, manifest_issues = collect_expected_manifest_payload(root)
    issues.extend(manifest_issues)
    if expected_manifest is None:
        return issues

    manifest_payload = load_json(manifest_path)
    if not isinstance(manifest_payload, dict):
        issues.append(("MANIFEST_FIELD_MISMATCHES", "manifest.json:expected_object"))
        return issues

    phase2_tool_manifest = load_json(phase2_tool_manifest_path)
    if not isinstance(phase2_tool_manifest, dict):
        issues.append(("MANIFEST_POINTER_MISMATCH", "phase2_tool_manifest.json:expected_object"))
        return issues

    if phase2_tool_manifest.get("genksyms_bridge_packet") != BRIDGE_MANIFEST_PATH:
        issues.append(
            (
                "MANIFEST_POINTER_MISMATCH",
                f"genksyms_bridge_packet:{phase2_tool_manifest.get('genksyms_bridge_packet')}",
            )
        )

    for key, expected in expected_manifest.items():
        if manifest_payload.get(key) != expected:
            issues.append(
                (
                    "MANIFEST_FIELD_MISMATCHES",
                    f"{key}:expected={json.dumps(expected, sort_keys=True)}:actual={json.dumps(manifest_payload.get(key), sort_keys=True)}",
                )
            )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=fail")
    for block, values in grouped.items():
        print(f"{block}_START")
        for value in values:
            print(value)
        print(f"{block}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / BRIDGE_CHECKER,
        "\n".join(
            (
                "print('GENKSYMS_BRIDGE_SELF_TEST=pass')",
                "print('GENKSYMS_BRIDGE_SELF_TEST_CASE_COUNT=6')",
                "",
            )
        ),
    )
    write_text(
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py --self-test",
                "      - name: Check Phase 2 genksyms bridge alignment",
                "        run: python3 scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
                "      - name: Self-test bounded genksyms bridge parity checker",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "      - name: Check bounded genksyms bridge parity",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py",
                "      - name: Run bounded genksyms bridge unit tests",
                "        run: zig test scripts/zigux/genksyms.zig",
                "",
            )
        ),
    )
    write_text(
        root / BRIDGE_CASES,
        json.dumps(
            {
                "cases": [
                    {"name": "minimal", "argv": [], "expected": "minimal_expected.json"},
                    {
                        "name": "abbreviated_help",
                        "argv": ["--hel"],
                        "mode": "process_json",
                        "expected": "help_expected.json",
                    },
                    {
                        "name": "invalid_option",
                        "argv": ["-x"],
                        "mode": "process_json",
                        "normalize_stderr": True,
                        "expected": "invalid_option_expected.json",
                    },
                ]
            },
            indent=2,
        )
        + "\n",
    )
    expected_manifest, issues = collect_expected_manifest_payload(root)
    assert expected_manifest is not None and issues == []
    write_text(root / BRIDGE_MANIFEST, json.dumps(expected_manifest, indent=2) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps({"genksyms_bridge_packet": BRIDGE_MANIFEST_PATH}, indent=2) + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_genksyms_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / BRIDGE_CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_BRIDGE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_BRIDGE_MARKERS", REQUIRED_BRIDGE_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: python3 other.py"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[1]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[2], "        run: python3 other.py --self-test"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[2]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[3]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[3]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[4], "        run: zig test scripts/zigux/other.zig"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / PHASE2_TOOL_MANIFEST
        path.write_text(json.dumps({"genksyms_bridge_packet": "zigux/tests/fixtures/other.json"}, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MANIFEST_POINTER_MISMATCH", "genksyms_bridge_packet:zigux/tests/fixtures/other.json") in issues
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 99
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("case_count:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["process_packet"] = ["wrong.json"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("process_packet:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["normalized_stderr_packet"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("normalized_stderr_packet:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "open"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("status:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["fixture_root"] = "zigux/tests/fixtures/other_bridge"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("fixture_root:") for block, value in issues)
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_CASES
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][0]["mode"] = "yaml"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "minimal:unsupported_mode:yaml") in issues
        cases += 1

        build_self_test_root(root)
        path = root / BRIDGE_CASES
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cases"][1]["name"] = "minimal"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "duplicate_case_name:minimal") in issues
        cases += 1

        build_self_test_root(root)
        (root / BRIDGE_MANIFEST).unlink()
        issues = collect_issues(root)
        assert ("MISSING_MANIFEST_FILES", str(BRIDGE_MANIFEST)) in issues
        cases += 1

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 genksyms bridge self-test surface stays wired into CI."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT=pass")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_BRIDGE_MARKER_COUNT={len(REQUIRED_BRIDGE_MARKERS)}")
    print(f"PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print("PHASE2_GENKSYMS_BRIDGE_SELFTEST_ALIGNMENT_MANIFEST_PATH=" + BRIDGE_MANIFEST_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
