#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
GENKSYMS_ZIG = Path("scripts/zigux/genksyms.zig")
BRIDGE_CHECKER = Path("scripts/zigux/check-genksyms-bridge.py")
CASES_PATH = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
MANIFEST_PATH = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

REQUIRED_FILES = (
    WORKFLOW,
    GENKSYMS_ZIG,
    BRIDGE_CHECKER,
    CASES_PATH,
    MANIFEST_PATH,
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-current-genksyms-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-current-genksyms-gate.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
)

EXPECTED_MANIFEST_FIELDS = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "wrapper-first bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
}


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


def collect_expected_manifest_fields(cases_payload: object) -> tuple[dict[str, object] | None, list[str]]:
    if not isinstance(cases_payload, list):
        return None, ["cases.json:expected_top_level_list"]

    issues: list[str] = []
    names: list[str] = []
    stdout_packet: list[str] = []
    process_packet: list[str] = []
    normalized_stderr_packet: list[str] = []
    action_abbrev_cases: list[str] = []
    seen_names: set[str] = set()

    for index, case in enumerate(cases_payload):
        if not isinstance(case, dict):
            issues.append(f"cases[{index}]:expected_object")
            continue
        name = case.get("name")
        if not isinstance(name, str) or not name:
            issues.append(f"cases[{index}]:name:expected_nonempty_string")
            continue
        if name in seen_names:
            issues.append(f"duplicate_case_name:{name}")
            continue
        seen_names.add(name)

        expected = case.get("expected")
        if not isinstance(expected, str) or not expected:
            issues.append(f"{name}:expected:expected_nonempty_string")
            continue

        mode = case.get("mode")
        if mode not in {"stdout_json", "process_json"}:
            issues.append(f"{name}:unsupported_mode:{mode}")
            continue

        names.append(name)
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

    return {
        **EXPECTED_MANIFEST_FIELDS,
        "case_count": len(names),
        "cases": names,
        "stdout_packet": ordered_unique(stdout_packet),
        "process_packet": ordered_unique(process_packet),
        "normalized_stderr_packet": ordered_unique(normalized_stderr_packet),
        "action_abbrev_cases": ordered_unique(action_abbrev_cases),
    }, []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_FILES:
        if not (root / path).exists():
            issues.append(("MISSING_REQUIRED_FILES", str(path)))

    if any(block == "MISSING_REQUIRED_FILES" for block, _ in issues):
        return issues

    workflow_text = read_text(root / WORKFLOW)
    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    expected_manifest, case_issues = collect_expected_manifest_fields(load_json(root / CASES_PATH))
    issues.extend(("CASE_PAYLOAD_ISSUES", issue) for issue in case_issues)
    if expected_manifest is None:
        return issues

    manifest_payload = load_json(root / MANIFEST_PATH)
    if not isinstance(manifest_payload, dict):
        issues.append(("MANIFEST_FIELD_MISMATCHES", "manifest.json:expected_object"))
        return issues

    for key, expected in expected_manifest.items():
        if manifest_payload.get(key) != expected:
            issues.append(
                (
                    "MANIFEST_FIELD_MISMATCHES",
                    f"{key}:expected={json.dumps(expected, sort_keys=True)}:"
                    f"actual={json.dumps(manifest_payload.get(key), sort_keys=True)}",
                )
            )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)
    print("PHASE2_CURRENT_GENKSYMS_GATE=fail")
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
        root / WORKFLOW,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 2 genksyms gate",
                "        run: python3 scripts/zigux/check-phase2-current-genksyms-gate.py --self-test",
                "      - name: Check current Phase 2 genksyms gate",
                "        run: python3 scripts/zigux/check-phase2-current-genksyms-gate.py",
                "      - name: Self-test bounded genksyms bridge checker",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
                "      - name: Check bounded genksyms bridge packet",
                "        run: python3 scripts/zigux/check-genksyms-bridge.py",
                "      - name: Run bounded genksyms bridge unit tests",
                "        run: zig test scripts/zigux/genksyms.zig",
                "",
            )
        ),
    )
    write_text(root / GENKSYMS_ZIG, "const std = @import(\"std\");\n")
    write_text(root / BRIDGE_CHECKER, "print('stub bridge checker')\n")
    cases_payload = [
        {"name": "minimal", "argv": [], "mode": "stdout_json", "expected": "minimal_expected.json"},
        {"name": "abbreviated_help", "argv": ["--he"], "mode": "process_json", "expected": "help_expected.json"},
        {
            "name": "invalid_option",
            "argv": ["-x"],
            "mode": "process_json",
            "expected": "invalid_option_expected.json",
            "normalize_stderr": True,
        },
    ]
    write_text(root / CASES_PATH, json.dumps(cases_payload, indent=2) + "\n")
    expected_manifest, issues = collect_expected_manifest_fields(cases_payload)
    assert expected_manifest is not None and not issues
    write_text(root / MANIFEST_PATH, json.dumps(expected_manifest, indent=2) + "\n")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_current_genksyms_gate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "run: python3 other.py"),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(
            duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[2]),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[2]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        (root / GENKSYMS_ZIG).unlink()
        issues = collect_issues(root)
        assert ("MISSING_REQUIRED_FILES", str(GENKSYMS_ZIG)) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CASES_PATH
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[1]["name"] = "minimal"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "duplicate_case_name:minimal") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CASES_PATH
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[2]["mode"] = "yaml"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CASE_PAYLOAD_ISSUES", "invalid_option:unsupported_mode:yaml") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MANIFEST_PATH
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 99
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(block == "MANIFEST_FIELD_MISMATCHES" and value.startswith("case_count:") for block, value in issues)
        cases += 1

    assert cases == 6
    print("PHASE2_CURRENT_GENKSYMS_GATE_SELF_TEST=pass")
    print(f"PHASE2_CURRENT_GENKSYMS_GATE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current-head genksyms bridge gate stays wired into the bootstrap workflow."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CURRENT_GENKSYMS_GATE=pass")
    print(f"PHASE2_CURRENT_GENKSYMS_GATE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_CURRENT_GENKSYMS_GATE_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print("PHASE2_CURRENT_GENKSYMS_GATE_SCOPE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
