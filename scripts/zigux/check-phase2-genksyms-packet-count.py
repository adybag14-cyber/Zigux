#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

COUNT_LINE_TEMPLATE = (
    "- the dedicated `Phase 2 genksyms` bridge packet remains the live `{count}-case` bridge "
    "surface under `zigux/tests/fixtures/genksyms_bridge/`, and the shared reminder surfaces "
    "should keep that fixture-backed bridge evidence explicit without drifting back to older "
    "undercounts or claiming standalone checker scripts that are not present on current `master`"
)
COUNT_LINE_REGEX = re.compile(
    r"the dedicated `Phase 2 genksyms` bridge packet remains the live `(?P<count>\d+)-case` "
    r"bridge surface under `zigux/tests/fixtures/genksyms_bridge/`"
)

REQUIRED_SECTION_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_packet_count(closure_text: str) -> int | None:
    for raw_line in closure_text.splitlines():
        match = COUNT_LINE_REGEX.search(raw_line.strip())
        if match:
            return int(match.group("count"))
    return None


def expected_counts(root: Path) -> tuple[int, int, int, int]:
    manifest_payload = read_json(root / GENKSYMS_MANIFEST_REL)
    cases_payload = read_json(root / GENKSYMS_CASES_REL)

    if not isinstance(manifest_payload, dict):
        raise SystemExit(f"invalid manifest shape: {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(cases_payload, list):
        raise SystemExit(f"invalid cases shape: {root / GENKSYMS_CASES_REL}")

    case_count = manifest_payload.get("case_count")
    case_names = manifest_payload.get("cases")
    bridge_expected_packet = manifest_payload.get("bridge_expected_packet")
    help_packet = manifest_payload.get("help_packet")
    standalone_proof_packet = manifest_payload.get("standalone_proof_packet")
    process_output_packet = manifest_payload.get("process_output_packet")

    if not isinstance(case_count, int):
        raise SystemExit(f"invalid case_count in {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(case_names, list) or not all(isinstance(item, str) for item in case_names):
        raise SystemExit(f"invalid cases list in {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(bridge_expected_packet, list) or not all(
        isinstance(item, str) for item in bridge_expected_packet
    ):
        raise SystemExit(f"invalid bridge_expected_packet in {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(help_packet, list) or not all(isinstance(item, str) for item in help_packet):
        raise SystemExit(f"invalid help_packet in {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(standalone_proof_packet, list) or not all(
        isinstance(item, str) for item in standalone_proof_packet
    ):
        raise SystemExit(f"invalid standalone_proof_packet in {root / GENKSYMS_MANIFEST_REL}")
    if not isinstance(process_output_packet, list) or not all(
        isinstance(item, str) for item in process_output_packet
    ):
        raise SystemExit(f"invalid process_output_packet in {root / GENKSYMS_MANIFEST_REL}")

    total_count = (
        case_count
        + len(help_packet)
        + len(standalone_proof_packet)
        + len(process_output_packet)
    )
    return case_count, len(cases_payload), len(process_output_packet), total_count


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    manifest_payload = read_json(root / GENKSYMS_MANIFEST_REL)
    case_count, fixture_case_count, process_output_count, total_count = expected_counts(root)
    issues: list[tuple[str, str]] = []

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_SECTION_MARKER", marker))

    if not isinstance(manifest_payload, dict):
        raise SystemExit(f"invalid manifest shape: {root / GENKSYMS_MANIFEST_REL}")

    manifest_case_names = manifest_payload.get("cases")
    bridge_expected_packet = manifest_payload.get("bridge_expected_packet")
    help_packet = manifest_payload.get("help_packet")
    standalone_proof_packet = manifest_payload.get("standalone_proof_packet")
    process_output_packet = manifest_payload.get("process_output_packet")

    if case_count != fixture_case_count:
        issues.append(("MANIFEST_CASE_COUNT_DRIFT", f"{case_count}!={fixture_case_count}"))
    if isinstance(manifest_case_names, list) and len(manifest_case_names) != case_count:
        issues.append(("MANIFEST_CASE_NAME_COUNT_DRIFT", f"{len(manifest_case_names)}!={case_count}"))
    if isinstance(bridge_expected_packet, list) and len(bridge_expected_packet) != case_count:
        issues.append(
            ("BRIDGE_EXPECTED_PACKET_COUNT_DRIFT", f"{len(bridge_expected_packet)}!={case_count}")
        )
    if isinstance(help_packet, list) and len(help_packet) != 1:
        issues.append(("HELP_PACKET_COUNT_DRIFT", str(len(help_packet))))
    if isinstance(standalone_proof_packet, list) and len(standalone_proof_packet) != 2:
        issues.append(("STANDALONE_PROOF_COUNT_DRIFT", str(len(standalone_proof_packet))))
    if isinstance(process_output_packet, list) and len(process_output_packet) != process_output_count:
        issues.append(("PROCESS_OUTPUT_COUNT_DRIFT", str(len(process_output_packet))))

    packet_count = extract_packet_count(closure_text)
    if packet_count is None:
        issues.append(("MISSING_PACKET_COUNT_LINE", COUNT_LINE_TEMPLATE.format(count=total_count)))
    elif packet_count != total_count:
        issues.append(("MISMATCHED_PACKET_COUNT_LINE", f"{packet_count}!={total_count}"))

    expected_line = COUNT_LINE_TEMPLATE.format(count=total_count)
    expected_line_count = count_exact_lines(closure_text, expected_line)
    if expected_line_count != 1:
        issues.append(("EXACT_PACKET_COUNT_LINE_COUNT", f"{expected_line_count}::{expected_line}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_PACKET_COUNT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

## Current Closure Packet

- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`

## Current Repo-Reality Gaps

- the dedicated `Phase 2 genksyms` bridge packet remains the live `23-case` bridge surface under `zigux/tests/fixtures/genksyms_bridge/`, and the shared reminder surfaces should keep that fixture-backed bridge evidence explicit without drifting back to older undercounts or claiming standalone checker scripts that are not present on current `master`
"""
    manifest_payload = {
        "case_count": 10,
        "cases": [f"case_{index}" for index in range(10)],
        "bridge_expected_packet": [f"case_{index}_expected.json" for index in range(10)],
        "help_packet": ["help_expected.json"],
        "standalone_proof_packet": [
            "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
            "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
        ],
        "process_output_packet": [
            "abbreviated_version_expected.json",
            "ambiguous_long_option_expected.json",
            "invalid_option_expected.json",
            "missing_long_dump_types_argument_expected.json",
            "missing_long_reference_argument_expected.json",
            "missing_reference_argument_expected.json",
            "too_many_reference_files_expected.json",
            "unsupported_long_option_expected.json",
            "unexpected_long_help_argument_expected.json",
            "abbreviated_unexpected_long_help_argument_expected.json",
        ],
    }
    cases_payload = [
        {"name": f"case_{index}", "args": [], "expected_file": f"case_{index}_expected.json"}
        for index in range(10)
    ]

    write_text(root / PHASE2_CLOSURE_REL, closure_text)
    write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest_payload, indent=2) + "\n")
    write_text(root / GENKSYMS_CASES_REL, json.dumps(cases_payload, indent=2) + "\n")


def write_sample_root(root: Path) -> int:
    build_self_test_root(root)
    print(f"PHASE2_GENKSYMS_PACKET_COUNT_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_packet_count_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_SECTION_MARKER",
            "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`23-case`",
                "`24-case`",
            ),
            encoding="utf-8",
        )
        assert ("MISMATCHED_PACKET_COUNT_LINE", "24!=23") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = root / GENKSYMS_MANIFEST_REL
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_payload["case_count"] = 9
        manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MANIFEST_CASE_COUNT_DRIFT", "9!=10") in issues
        assert ("MISMATCHED_PACKET_COUNT_LINE", "23!=22") in issues
        checks_run += 1

        build_self_test_root(root)
        cases_path = root / GENKSYMS_CASES_REL
        cases_payload = json.loads(cases_path.read_text(encoding="utf-8"))
        cases_path.write_text(json.dumps(cases_payload[:-1], indent=2) + "\n", encoding="utf-8")
        assert ("MANIFEST_CASE_COUNT_DRIFT", "10!=9") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                COUNT_LINE_TEMPLATE.format(count=23),
                COUNT_LINE_TEMPLATE.format(count=23) + "\n" + COUNT_LINE_TEMPLATE.format(count=23),
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "EXACT_PACKET_COUNT_LINE_COUNT",
            f"2::{COUNT_LINE_TEMPLATE.format(count=23)}",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_PACKET_COUNT_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_PACKET_COUNT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note genksyms packet count aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    case_count, fixture_case_count, process_output_count, total_count = expected_counts(args.root.resolve())
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_PACKET_COUNT=pass")
    print(f"PHASE2_GENKSYMS_PACKET_BRIDGE_CASE_COUNT={case_count}")
    print(f"PHASE2_GENKSYMS_PACKET_FIXTURE_CASE_COUNT={fixture_case_count}")
    print(f"PHASE2_GENKSYMS_PACKET_PROCESS_OUTPUT_COUNT={process_output_count}")
    print(f"PHASE2_GENKSYMS_PACKET_TOTAL_COUNT={total_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
