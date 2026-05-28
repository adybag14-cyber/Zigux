#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

PHASE2_CLOSURE = "Documentation/zigux/phase2-closure.md"
PHASE2_TOOL_MANIFEST = "zigux/tests/fixtures/phase2_tool_manifest.json"
BRIDGE_CHECKER = "scripts/zigux/check-genksyms-bridge.py"
BRIDGE_CASES = "zigux/tests/fixtures/genksyms_bridge/cases.json"
BRIDGE_MANIFEST = "zigux/tests/fixtures/genksyms_bridge/manifest.json"
INLINE_SHORT_TEST = "scripts/zigux/genksyms_inline_short_option_argument_test.zig"
INLINE_SHORT_EXPECTED = "zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json"

INLINE_SHORT_CASE = "inline_short_option_arguments"
INLINE_SHORT_CASE_MARKER = f'"name": "{INLINE_SHORT_CASE}"'
INLINE_SHORT_EXPECTED_NAME = "inline_short_option_arguments_expected.json"
INLINE_SHORT_TEST_MARKER = 'test "genksyms bridge accepts inline short option arguments" {'

SHARED_STANDALONE_PROOF_PACKET = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

EXPECTED_INLINE_SHORT_PAYLOAD = {
    "tool": "scripts/genksyms/genksyms",
    "stdin": "cpp-stream",
    "stdout": "symversions",
    "argv": [
        "scripts/genksyms/genksyms",
        "-d",
        "-rfoo.symref",
        "-Ttypes.symtypes",
    ],
    "options": {
        "debug_level": 1,
        "warnings": False,
        "dump_defs": False,
        "preserve": False,
        "reference_files": ["foo.symref"],
        "dump_types_file": "types.symtypes",
    },
}

EXPECTED_SELF_TEST_CASE_COUNT = 10


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: str, issue_code: str) -> tuple[object | None, tuple[str, str] | None]:
    try:
        return json.loads(read_text(root, rel)), None
    except json.JSONDecodeError:
        return None, (issue_code, rel)


def count_exact(values: list[str], target: str) -> int:
    return sum(1 for value in values if value == target)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in (
        PHASE2_CLOSURE,
        PHASE2_TOOL_MANIFEST,
        BRIDGE_CHECKER,
        BRIDGE_CASES,
        BRIDGE_MANIFEST,
        INLINE_SHORT_TEST,
        INLINE_SHORT_EXPECTED,
    ):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    closure_text = read_text(root, PHASE2_CLOSURE)
    tool_manifest_payload, tool_manifest_issue = read_json(root, PHASE2_TOOL_MANIFEST, "INVALID_TOOL_MANIFEST_JSON")
    bridge_cases_payload, bridge_cases_issue = read_json(root, BRIDGE_CASES, "INVALID_BRIDGE_CASES_JSON")
    bridge_manifest_payload, bridge_manifest_issue = read_json(root, BRIDGE_MANIFEST, "INVALID_BRIDGE_MANIFEST_JSON")
    inline_short_payload, inline_short_issue = read_json(root, INLINE_SHORT_EXPECTED, "INVALID_INLINE_SHORT_EXPECTED_JSON")
    if tool_manifest_issue is not None:
        issues.append(tool_manifest_issue)
    if bridge_cases_issue is not None:
        issues.append(bridge_cases_issue)
    if bridge_manifest_issue is not None:
        issues.append(bridge_manifest_issue)
    if inline_short_issue is not None:
        issues.append(inline_short_issue)
    if issues:
        return issues

    bridge_checker_text = read_text(root, BRIDGE_CHECKER)
    inline_short_test_text = read_text(root, INLINE_SHORT_TEST)

    if INLINE_SHORT_CASE not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", INLINE_SHORT_CASE))
    if INLINE_SHORT_EXPECTED_NAME not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", INLINE_SHORT_EXPECTED_NAME))
    if INLINE_SHORT_TEST not in bridge_checker_text:
        issues.append(("MISSING_BRIDGE_CHECKER_MARKER", INLINE_SHORT_TEST))

    if inline_short_test_text.count(INLINE_SHORT_TEST_MARKER) != 1:
        issues.append(("INLINE_SHORT_TEST_MARKER_MISMATCH", INLINE_SHORT_TEST_MARKER))

    if inline_short_payload != EXPECTED_INLINE_SHORT_PAYLOAD:
        issues.append(("INLINE_SHORT_EXPECTED_PAYLOAD_MISMATCH", INLINE_SHORT_EXPECTED))

    if not isinstance(bridge_cases_payload, list):
        issues.append(("INVALID_BRIDGE_CASES_PAYLOAD", type(bridge_cases_payload).__name__))
        return issues
    inline_short_cases = [
        item for item in bridge_cases_payload if isinstance(item, dict) and item.get("name") == INLINE_SHORT_CASE
    ]
    if len(inline_short_cases) != 1:
        issues.append(("INLINE_SHORT_CASE_COUNT_MISMATCH", str(len(inline_short_cases))))
    elif inline_short_cases[0].get("expected_file") != INLINE_SHORT_EXPECTED_NAME:
        issues.append(("INLINE_SHORT_CASE_EXPECTED_FILE_MISMATCH", repr(inline_short_cases[0].get("expected_file"))))

    if not isinstance(bridge_manifest_payload, dict):
        issues.append(("INVALID_BRIDGE_MANIFEST_PAYLOAD", type(bridge_manifest_payload).__name__))
        return issues
    manifest_cases = bridge_manifest_payload.get("cases")
    manifest_expected = bridge_manifest_payload.get("bridge_expected_packet")
    standalone_proof_packet = bridge_manifest_payload.get("standalone_proof_packet")
    if not isinstance(manifest_cases, list) or not all(isinstance(item, str) for item in manifest_cases):
        issues.append(("INVALID_BRIDGE_MANIFEST_FIELD", "cases"))
    else:
        if count_exact(manifest_cases, INLINE_SHORT_CASE) != 1:
            issues.append(("MANIFEST_INLINE_SHORT_CASE_MISMATCH", repr(manifest_cases)))
    if not isinstance(manifest_expected, list) or not all(isinstance(item, str) for item in manifest_expected):
        issues.append(("INVALID_BRIDGE_MANIFEST_FIELD", "bridge_expected_packet"))
    else:
        if count_exact(manifest_expected, INLINE_SHORT_EXPECTED_NAME) != 1:
            issues.append(("MANIFEST_INLINE_SHORT_EXPECTED_MISMATCH", repr(manifest_expected)))
    if standalone_proof_packet != list(SHARED_STANDALONE_PROOF_PACKET):
        issues.append(("STANDALONE_PROOF_PACKET_MISMATCH", repr(standalone_proof_packet)))
    if isinstance(standalone_proof_packet, list) and INLINE_SHORT_TEST in standalone_proof_packet:
        issues.append(("INLINE_SHORT_LEAKED_TO_STANDALONE_PROOF_PACKET", INLINE_SHORT_TEST))

    if not isinstance(tool_manifest_payload, dict):
        issues.append(("INVALID_TOOL_MANIFEST_PAYLOAD", type(tool_manifest_payload).__name__))
        return issues
    present_surfaces = tool_manifest_payload.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_TOOL_MANIFEST_FIELD", "present_surfaces"))
        return issues
    bridge_helpers = present_surfaces.get("bridge_helpers")
    if not isinstance(bridge_helpers, list) or not all(isinstance(item, str) for item in bridge_helpers):
        issues.append(("INVALID_TOOL_MANIFEST_FIELD", "bridge_helpers"))
    else:
        for marker in SHARED_STANDALONE_PROOF_PACKET:
            if count_exact(bridge_helpers, marker) != 1:
                issues.append(("TOOL_MANIFEST_BRIDGE_HELPER_MISMATCH", marker))
        if INLINE_SHORT_TEST in bridge_helpers:
            issues.append(("INLINE_SHORT_LEAKED_TO_TOOL_MANIFEST", INLINE_SHORT_TEST))

    for marker in SHARED_STANDALONE_PROOF_PACKET:
        if f"`{marker}`" not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    if INLINE_SHORT_TEST in closure_text:
        issues.append(("INLINE_SHORT_LEAKED_TO_CLOSURE", INLINE_SHORT_TEST))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        PHASE2_CLOSURE,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                f"- `{SHARED_STANDALONE_PROOF_PACKET[0]}`",
                f"- `{SHARED_STANDALONE_PROOF_PACKET[1]}`",
                "",
            )
        ),
    )
    write_text(
        root,
        PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "present_surfaces": {
                    "bridge_helpers": [
                        "scripts/zigux/kconfig/conf_bridge.zig",
                        "scripts/zigux/kconfig/confdata_bridge.zig",
                        "scripts/zigux/genksyms.zig",
                        *SHARED_STANDALONE_PROOF_PACKET,
                    ]
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        BRIDGE_CHECKER,
        "\n".join(
            (
                f'INLINE_SHORT_ARGUMENT_TEST = "{INLINE_SHORT_TEST}"',
                f'CASE_FIXTURE = {INLINE_SHORT_CASE_MARKER}',
                f'EXPECTED_FILE = "{INLINE_SHORT_EXPECTED_NAME}"',
                "",
            )
        ),
    )
    write_text(
        root,
        BRIDGE_CASES,
        json.dumps(
            [
                {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
                {
                    "name": INLINE_SHORT_CASE,
                    "args": ["-d", "-rfoo.symref", "-Ttypes.symtypes"],
                    "expected_file": INLINE_SHORT_EXPECTED_NAME,
                },
            ],
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        BRIDGE_MANIFEST,
        json.dumps(
            {
                "cases": ["minimal", INLINE_SHORT_CASE],
                "bridge_expected_packet": ["minimal_expected.json", INLINE_SHORT_EXPECTED_NAME],
                "standalone_proof_packet": list(SHARED_STANDALONE_PROOF_PACKET),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root, INLINE_SHORT_TEST, INLINE_SHORT_TEST_MARKER + "\n}\n")
    write_text(root, INLINE_SHORT_EXPECTED, json.dumps(EXPECTED_INLINE_SHORT_PAYLOAD, indent=2) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane24_inline_short_locality_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            BRIDGE_MANIFEST,
            json.dumps(
                {
                    "cases": ["minimal", INLINE_SHORT_CASE],
                    "bridge_expected_packet": ["minimal_expected.json", INLINE_SHORT_EXPECTED_NAME],
                    "standalone_proof_packet": [*SHARED_STANDALONE_PROOF_PACKET, INLINE_SHORT_TEST],
                },
                indent=2,
            )
            + "\n",
        )
        assert ("INLINE_SHORT_LEAKED_TO_STANDALONE_PROOF_PACKET", INLINE_SHORT_TEST) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, PHASE2_TOOL_MANIFEST))
        payload["present_surfaces"]["bridge_helpers"].append(INLINE_SHORT_TEST)
        write_text(root, PHASE2_TOOL_MANIFEST, json.dumps(payload, indent=2) + "\n")
        assert ("INLINE_SHORT_LEAKED_TO_TOOL_MANIFEST", INLINE_SHORT_TEST) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, PHASE2_CLOSURE, read_text(root, PHASE2_CLOSURE) + f"- `{INLINE_SHORT_TEST}`\n")
        assert ("INLINE_SHORT_LEAKED_TO_CLOSURE", INLINE_SHORT_TEST) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        cases = json.loads(read_text(root, BRIDGE_CASES))
        cases[1]["expected_file"] = "drifted.json"
        write_text(root, BRIDGE_CASES, json.dumps(cases, indent=2) + "\n")
        assert ("INLINE_SHORT_CASE_EXPECTED_FILE_MISMATCH", "'drifted.json'") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest = json.loads(read_text(root, BRIDGE_MANIFEST))
        manifest["bridge_expected_packet"] = ["minimal_expected.json"]
        write_text(root, BRIDGE_MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "MANIFEST_INLINE_SHORT_EXPECTED_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root, INLINE_SHORT_TEST, "")
        assert ("INLINE_SHORT_TEST_MARKER_MISMATCH", INLINE_SHORT_TEST_MARKER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = EXPECTED_INLINE_SHORT_PAYLOAD.copy()
        payload["options"] = dict(payload["options"])
        payload["options"]["warnings"] = True
        write_text(root, INLINE_SHORT_EXPECTED, json.dumps(payload, indent=2) + "\n")
        assert ("INLINE_SHORT_EXPECTED_PAYLOAD_MISMATCH", INLINE_SHORT_EXPECTED) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, BRIDGE_CHECKER, "")
        assert ("MISSING_BRIDGE_CHECKER_MARKER", INLINE_SHORT_CASE) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, BRIDGE_MANIFEST, "{broken\n")
        assert ("INVALID_BRIDGE_MANIFEST_JSON", BRIDGE_MANIFEST) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 genksyms inline-short replay helper-local while the shared standalone proof packet stays version-only."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a synthetic passing root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET=pass")
    print("PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET_SHARED_PROOF_COUNT=2")
    print("PHASE2_GENKSYMS_INLINE_SHORT_LOCALITY_PACKET_HELPER_LOCAL_CASE_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
