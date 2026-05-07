#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()
CHECKER = Path("scripts/zigux/check-kconfig-bridge.py")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE = Path("Documentation/zigux/phase2-closure.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
CONFDATA_PACKET_PATH = "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json"

REQUIRED_CHECKER_MARKERS = (
    "REQUIRED_CONFDATA_CASES = [",
    "EXPECTED_SELF_TEST_CASE_COUNT = 17",
    'print("KCONFIG_BRIDGE_SELF_TEST=pass")',
    'print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}")',
)
REQUIRED_CHECKER_EXACT_COUNTS = {
    "REQUIRED_CONFDATA_CASES = [": 1,
    "EXPECTED_SELF_TEST_CASE_COUNT = 17": 1,
    'print("KCONFIG_BRIDGE_SELF_TEST=pass")': 1,
    'print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}")': 1,
}
REQUIRED_VALIDATOR_MARKERS = (
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
)
REQUIRED_VALIDATOR_EXACT_COUNTS = {
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test": 1,
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py": 1,
    "python3 scripts/zigux/check-kconfig-bridge.py": 1,
    "zig test scripts/zigux/kconfig/conf_bridge.zig": 1,
    "zig test scripts/zigux/kconfig/confdata_bridge.zig": 1,
}
REQUIRED_MAKEFILE_LINES = (
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
)
REQUIRED_CLOSURE_MARKERS = (
    f"`PHASE2_KCONFIG_BRIDGE_CONFDATA_PACKET={CONFDATA_PACKET_PATH}`",
    "`kconfig_confdata_bridge_packet`",
)
REQUIRED_CLOSURE_EXACT_COUNTS = {
    f"`PHASE2_KCONFIG_BRIDGE_CONFDATA_PACKET={CONFDATA_PACKET_PATH}`": 1,
    "`kconfig_confdata_bridge_packet`": 1,
}
EXPECTED_SELF_TEST_CASE_COUNT = 36


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def count_exact_substrings(text: str, marker: str) -> int:
    return text.count(marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    checker_text = read_text(root / CHECKER)
    validator_text = read_text(root / VALIDATOR)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    closure_text = read_text(root / CLOSURE)
    tool_manifest = json.loads(read_text(root / TOOL_MANIFEST))

    for marker in REQUIRED_CHECKER_MARKERS:
        if marker not in checker_text:
            issues.append(("MISSING_CHECKER_MARKERS", marker))
    for marker, expected_count in REQUIRED_CHECKER_EXACT_COUNTS.items():
        count = count_exact_substrings(checker_text, marker)
        if count != expected_count:
            issues.append(("DUPLICATE_CHECKER_MARKERS", f"{marker}:count={count}:expected={expected_count}"))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        count = count_exact_lines(validator_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKERS", marker))
        elif count != REQUIRED_VALIDATOR_EXACT_COUNTS[marker]:
            issues.append(("DUPLICATE_VALIDATOR_MARKERS", f"{marker}:count={count}:expected={REQUIRED_VALIDATOR_EXACT_COUNTS[marker]}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKERS", marker))
    for marker, expected_count in REQUIRED_CLOSURE_EXACT_COUNTS.items():
        count = closure_text.count(marker)
        if count != expected_count:
            issues.append(("DUPLICATE_CLOSURE_MARKERS", f"{marker}:count={count}:expected={expected_count}"))

    if tool_manifest.get("kconfig_confdata_bridge_packet") != CONFDATA_PACKET_PATH:
        issues.append(("INVALID_TOOL_MANIFEST_PACKET", f"kconfig_confdata_bridge_packet={tool_manifest.get('kconfig_confdata_bridge_packet')!r}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for block, value in issues:
        grouped.setdefault(block, []).append(value)

    print("PHASE2_KCONFIG_ALIGNMENT=fail")
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
        root / CHECKER,
        "\n".join(
            (
                "REQUIRED_CONFDATA_CASES = [",
                "    'sample',",
                "]",
                "EXPECTED_SELF_TEST_CASE_COUNT = 17",
                'print("KCONFIG_BRIDGE_SELF_TEST=pass")',
                'print(f"KCONFIG_BRIDGE_SELF_TEST_CASE_COUNT={checks_run}")',
                "",
            )
        ),
    )
    write_text(
        root / VALIDATOR,
        "\n".join(
            (
                "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                "python3 scripts/zigux/check-kconfig-bridge.py",
                "zig test scripts/zigux/kconfig/conf_bridge.zig",
                "zig test scripts/zigux/kconfig/confdata_bridge.zig",
                "",
            )
        ),
    )
    write_text(
        root / MAKEFILE,
        "\n".join(
            (
                "phase2-kconfig:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
                "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
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
                "      - name: Self-test Phase 2 kconfig selftest alignment",
                "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
                "      - name: Check Phase 2 kconfig selftest alignment",
                "        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
                "      - name: Self-test bounded kconfig bridge parity checker",
                "        run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
                "      - name: Check bounded kconfig bridge parity",
                "        run: python3 scripts/zigux/check-kconfig-bridge.py",
                "      - name: Run bounded kconfig bridge unit tests",
                "        run: zig test scripts/zigux/kconfig/conf_bridge.zig",
                "      - name: Run bounded confdata bridge unit tests",
                "        run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
                "",
            )
        ),
    )
    write_text(
        root / CLOSURE,
        "\n".join(
            (
                "## Kconfig Confdata Bridge Closure Packet",
                f"- `PHASE2_KCONFIG_BRIDGE_CONFDATA_PACKET={CONFDATA_PACKET_PATH}`",
                "- the shared Phase 2 tool manifest points at that same tool-local packet through `kconfig_confdata_bridge_packet`",
                "",
            )
        ),
    )
    write_text(
        root / TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "closed",
                "tool_count": 6,
                "kconfig_confdata_bridge_packet": CONFDATA_PACKET_PATH,
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_kconfig_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_CHECKER_MARKERS", REQUIRED_CHECKER_MARKERS[1]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[0], REQUIRED_CHECKER_MARKERS[0] + "\n" + REQUIRED_CHECKER_MARKERS[0], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CHECKER_MARKERS", f"{REQUIRED_CHECKER_MARKERS[0]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[1], REQUIRED_CHECKER_MARKERS[1] + "\n" + REQUIRED_CHECKER_MARKERS[1], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CHECKER_MARKERS", f"{REQUIRED_CHECKER_MARKERS[1]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[2], REQUIRED_CHECKER_MARKERS[2] + "\n" + REQUIRED_CHECKER_MARKERS[2], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CHECKER_MARKERS", f"{REQUIRED_CHECKER_MARKERS[2]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CHECKER
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CHECKER_MARKERS[3], REQUIRED_CHECKER_MARKERS[3] + "\n" + REQUIRED_CHECKER_MARKERS[3], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CHECKER_MARKERS", f"{REQUIRED_CHECKER_MARKERS[3]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[0] + "\n", REQUIRED_VALIDATOR_MARKERS[0] + "\n" + REQUIRED_VALIDATOR_MARKERS[0] + "\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_MARKERS", f"{REQUIRED_VALIDATOR_MARKERS[0]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[1] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[1]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[1] + "\n", REQUIRED_VALIDATOR_MARKERS[1] + "\n" + REQUIRED_VALIDATOR_MARKERS[1] + "\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_MARKERS", f"{REQUIRED_VALIDATOR_MARKERS[1]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[2] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[2]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[2] + "\n", REQUIRED_VALIDATOR_MARKERS[2] + "\n" + REQUIRED_VALIDATOR_MARKERS[2] + "\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_MARKERS", f"{REQUIRED_VALIDATOR_MARKERS[2]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[3] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[3]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[3] + "\n", REQUIRED_VALIDATOR_MARKERS[3] + "\n" + REQUIRED_VALIDATOR_MARKERS[3] + "\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_MARKERS", f"{REQUIRED_VALIDATOR_MARKERS[3]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[4] + "\n", "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_VALIDATOR_MARKERS", REQUIRED_VALIDATOR_MARKERS[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / VALIDATOR
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_VALIDATOR_MARKERS[4] + "\n", REQUIRED_VALIDATOR_MARKERS[4] + "\n" + REQUIRED_VALIDATOR_MARKERS[4] + "\n", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_VALIDATOR_MARKERS", f"{REQUIRED_VALIDATOR_MARKERS[4]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "\ttrue"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[2], "\ttrue"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[2]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[3]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[3]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[4], "\ttrue"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[5]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[5]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[6], "phase2: phase2-validate phase2-tools phase2-cross"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_MAKEFILE_HOOKS", REQUIRED_MAKEFILE_LINES[6]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / MAKEFILE
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[6]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_MAKEFILE_HOOKS", f"{REQUIRED_MAKEFILE_LINES[6]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "        run: python3 other.py"), encoding="utf-8")
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
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[2], "        run: python3 other.py --self-test"), encoding="utf-8")
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
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[4], "        run: zig test scripts/zigux/other.zig"), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_HOOKS", REQUIRED_WORKFLOW_LINES[4]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / WORKFLOW
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[5]), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_WORKFLOW_HOOKS", f"{REQUIRED_WORKFLOW_LINES[5]}:count=2") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CLOSURE
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_CLOSURE_MARKERS", REQUIRED_CLOSURE_MARKERS[0]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CLOSURE
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[1], "", 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_CLOSURE_MARKERS", REQUIRED_CLOSURE_MARKERS[1]) in issues
        cases += 1

        build_self_test_root(root)
        path = root / CLOSURE
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[0], REQUIRED_CLOSURE_MARKERS[0] + "\n" + REQUIRED_CLOSURE_MARKERS[0], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CLOSURE_MARKERS", f"{REQUIRED_CLOSURE_MARKERS[0]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / CLOSURE
        path.write_text(path.read_text(encoding="utf-8").replace(REQUIRED_CLOSURE_MARKERS[1], REQUIRED_CLOSURE_MARKERS[1] + "\n" + REQUIRED_CLOSURE_MARKERS[1], 1), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CLOSURE_MARKERS", f"{REQUIRED_CLOSURE_MARKERS[1]}:count=2:expected=1") in issues
        cases += 1

        build_self_test_root(root)
        path = root / TOOL_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.pop("kconfig_confdata_bridge_packet")
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PACKET", "kconfig_confdata_bridge_packet=None") in issues
        cases += 1

        build_self_test_root(root)
        path = root / TOOL_MANIFEST
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["kconfig_confdata_bridge_packet"] = "zigux/tests/fixtures/kconfig_bridge/other_manifest.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_TOOL_MANIFEST_PACKET", "kconfig_confdata_bridge_packet='zigux/tests/fixtures/kconfig_bridge/other_manifest.json'") in issues
        cases += 1

    assert cases == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_KCONFIG_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the Phase 2 kconfig replay guard stays wired into the shared gate surface.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_ALIGNMENT=pass")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CHECKER_MARKER_COUNT={len(REQUIRED_CHECKER_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_VALIDATOR_MARKER_COUNT={len(REQUIRED_VALIDATOR_MARKERS)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_MAKEFILE_HOOK_COUNT={len(REQUIRED_MAKEFILE_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_WORKFLOW_HOOK_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_KCONFIG_ALIGNMENT_CLOSURE_MARKER_COUNT={len(REQUIRED_CLOSURE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
