#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE_NOTE = "Documentation/zigux/phase2-closure.md"
SURVEY_NOTE = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"
BRIDGE_CHECKER = "scripts/zigux/check-genksyms-bridge.py"
SELFTEST_ALIGNMENT = "scripts/zigux/check-phase2-genksyms-selftest-alignment.py"
GENKSYMS_HELPER = "scripts/zigux/genksyms.zig"
MANIFEST = "zigux/tests/fixtures/genksyms_bridge/manifest.json"

REQUIRED_CLOSURE_LINES = (
    "## Current Genksyms Evidence",
    "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md` remains the same-family roadmap and ledger truthfulness anchor for the wrapper-first `genksyms` lane.",
    "- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, and `scripts/zigux/genksyms.zig` remain the live checker, closure-alignment guard, and Zig bridge helper on current `master`.",
    "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig` and `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig` remain the standalone version-side-effect proofs carried by the shipped bridge packet.",
    "- `zigux/tests/fixtures/genksyms_bridge/manifest.json` remains the live packet manifest, and `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set instead of sitting only in the helper-local manifest.",
    "- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "- `python3 scripts/zigux/check-genksyms-bridge.py`",
    "- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`",
    "- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "- `zig test scripts/zigux/genksyms.zig`",
    "- `make -C zigux phase2-genksyms`",
)

REQUIRED_SURVEY_LINES = (
    "- The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.",
    "3. If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces so the current wrapper-first packet and the dual-implementation gap statement cannot silently drift apart.",
)

REQUIRED_BRIDGE_CHECKER_LINES = (
    'EXPECTED_PROCESS_OUTPUT_PACKET = (',
    'EXPECTED_HELPER_LOCAL_ANCHORS = (',
    'REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = (',
    'REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES = (',
)

REQUIRED_ALIGNMENT_LINES = (
    'WORKFLOW_LINES = (',
    'MAKEFILE_LINES = (',
    'EXPECTED_PROCESS_OUTPUT_PAYLOADS = {',
)

REQUIRED_GENKSYMS_LINES = (
    'test "genksyms bridge preserves version side effect before invalid long option" {',
    'test "genksyms bridge preserves abbreviated version side effect before invalid long option" {',
    'test "genksyms bridge preserves version side effect before ambiguous long option" {',
    'test "genksyms bridge preserves abbreviated version side effect before ambiguous long option" {',
)

EXPECTED_STANDALONE_PROOFS = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

EXPECTED_PROCESS_OUTPUT_PACKET = (
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
)

EXPECTED_SELF_TEST_CASE_COUNT = 9


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(root: Path, rel: str) -> object:
    return json.loads(read_text(root, rel))


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_exact_lines(text: str, markers: tuple[str, ...], issue_code: str, issues: list[tuple[str, str]]) -> None:
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((issue_code, marker))
        elif count != 1:
            issues.append((f"DUPLICATE_{issue_code}", f"{marker}:count={count}"))


def parse_closure_process_output_packet(closure_text: str) -> tuple[str, ...] | None:
    prefix = "- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
    for line in closure_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix) and stripped.endswith("`"):
            payload = stripped[len(prefix) : -1]
            if payload:
                return tuple(part.split("/")[-1] for part in payload.split(","))
            return ()
    return None


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    required_paths = (
        CLOSURE_NOTE,
        SURVEY_NOTE,
        BRIDGE_CHECKER,
        SELFTEST_ALIGNMENT,
        GENKSYMS_HELPER,
        MANIFEST,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))
    if issues:
        return issues

    closure_text = read_text(root, CLOSURE_NOTE)
    survey_text = read_text(root, SURVEY_NOTE)
    bridge_checker_text = read_text(root, BRIDGE_CHECKER)
    alignment_text = read_text(root, SELFTEST_ALIGNMENT)
    genksyms_text = read_text(root, GENKSYMS_HELPER)

    require_exact_lines(closure_text, REQUIRED_CLOSURE_LINES, "MISSING_CLOSURE_LINE", issues)
    require_exact_lines(survey_text, REQUIRED_SURVEY_LINES, "MISSING_SURVEY_LINE", issues)
    require_exact_lines(bridge_checker_text, REQUIRED_BRIDGE_CHECKER_LINES, "MISSING_BRIDGE_CHECKER_LINE", issues)
    require_exact_lines(alignment_text, REQUIRED_ALIGNMENT_LINES, "MISSING_ALIGNMENT_LINE", issues)
    require_exact_lines(genksyms_text, REQUIRED_GENKSYMS_LINES, "MISSING_GENKSYMS_LINE", issues)

    manifest = read_json(root, MANIFEST)
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_PAYLOAD", type(manifest).__name__))
        return issues

    if manifest.get("tool") != "scripts/zigux/genksyms.zig":
        issues.append(("MANIFEST_FIELD_MISMATCH", "tool"))
    if manifest.get("status") != "closed":
        issues.append(("MANIFEST_FIELD_MISMATCH", "status"))
    if manifest.get("mode") != "bounded wrapper-first dual-implementation bridge":
        issues.append(("MANIFEST_FIELD_MISMATCH", "mode"))

    standalone_proof_packet = manifest.get("standalone_proof_packet")
    if standalone_proof_packet != list(manifest.get("standalone_proof_packet", [])):
        issues.append(("MANIFEST_FIELD_MISMATCH", "standalone_proof_packet_not_list"))
    else:
        for rel in EXPECTED_STANDALONE_PROOFS:
            if rel not in standalone_proof_packet:
                issues.append(("MISSING_STANDALONE_PROOF", rel))

    process_output_packet = manifest.get("process_output_packet")
    if process_output_packet != list(EXPECTED_PROCESS_OUTPUT_PACKET):
        issues.append(("MANIFEST_PROCESS_OUTPUT_PACKET_MISMATCH", "process_output_packet"))

    closure_packet = parse_closure_process_output_packet(closure_text)
    if closure_packet is None:
        issues.append(("MISSING_CLOSURE_SENTINEL", "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET"))
    elif closure_packet != EXPECTED_PROCESS_OUTPUT_PACKET:
        issues.append(("CLOSURE_PROCESS_OUTPUT_PACKET_MISMATCH", ",".join(closure_packet)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CURRENT_GENKSYMS_EVIDENCE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    write_text(
        root,
        CLOSURE_NOTE,
        "# Phase 2 Closure\n\n"
        "## Current Genksyms Evidence\n\n"
        "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md` remains the same-family roadmap and ledger truthfulness anchor for the wrapper-first `genksyms` lane.\n"
        "- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, and `scripts/zigux/genksyms.zig` remain the live checker, closure-alignment guard, and Zig bridge helper on current `master`.\n"
        "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig` and `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig` remain the standalone version-side-effect proofs carried by the shipped bridge packet.\n"
        "- `zigux/tests/fixtures/genksyms_bridge/manifest.json` remains the live packet manifest, and `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set instead of sitting only in the helper-local manifest.\n"
        "- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`\n"
        "- `python3 scripts/zigux/check-genksyms-bridge.py`\n"
        "- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`\n"
        "- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`\n"
        "- `zig test scripts/zigux/genksyms.zig`\n"
        "- `make -C zigux phase2-genksyms`\n"
        "- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
        + ",".join(f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in EXPECTED_PROCESS_OUTPUT_PACKET)
        + "`\n",
    )
    write_text(
        root,
        SURVEY_NOTE,
        "# Phase 2 genksyms dual-implementation survey\n\n"
        "- The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.\n\n"
        "## Next bounded same-family step\n\n"
        "3. If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces so the current wrapper-first packet and the dual-implementation gap statement cannot silently drift apart.\n",
    )
    write_text(
        root,
        BRIDGE_CHECKER,
        "EXPECTED_PROCESS_OUTPUT_PACKET = (\n)\n"
        "EXPECTED_HELPER_LOCAL_ANCHORS = (\n)\n"
        "REQUIRED_VERSION_SIDE_EFFECT_TEST_LINES = (\n)\n"
        "REQUIRED_AMBIGUOUS_VERSION_SIDE_EFFECT_TEST_LINES = (\n)\n",
    )
    write_text(
        root,
        SELFTEST_ALIGNMENT,
        "WORKFLOW_LINES = (\n)\n"
        "MAKEFILE_LINES = (\n)\n"
        "EXPECTED_PROCESS_OUTPUT_PAYLOADS = {\n}\n",
    )
    write_text(
        root,
        GENKSYMS_HELPER,
        "\n".join(REQUIRED_GENKSYMS_LINES) + "\n",
    )
    write_text(
        root,
        MANIFEST,
        json.dumps(
            {
                "tool": "scripts/zigux/genksyms.zig",
                "status": "closed",
                "mode": "bounded wrapper-first dual-implementation bridge",
                "standalone_proof_packet": [
                    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
                    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
                    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
                ],
                "process_output_packet": list(EXPECTED_PROCESS_OUTPUT_PACKET),
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane22_current_genksyms_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        write_sample_root(root)
        write_text(root, CLOSURE_NOTE, read_text(root, CLOSURE_NOTE).replace(REQUIRED_CLOSURE_LINES[1] + "\n", "", 1))
        assert ("MISSING_CLOSURE_LINE", REQUIRED_CLOSURE_LINES[1]) in collect_issues(root)
        checks += 1

        write_sample_root(root)
        write_text(root, SURVEY_NOTE, read_text(root, SURVEY_NOTE).replace(REQUIRED_SURVEY_LINES[0] + "\n", "", 1))
        assert ("MISSING_SURVEY_LINE", REQUIRED_SURVEY_LINES[0]) in collect_issues(root)
        checks += 1

        write_sample_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["process_output_packet"] = ["invalid_option_expected.json"]
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("MANIFEST_PROCESS_OUTPUT_PACKET_MISMATCH", "process_output_packet") in collect_issues(root)
        checks += 1

        write_sample_root(root)
        bad_closure = read_text(root, CLOSURE_NOTE).replace(
            "- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
            + ",".join(f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in EXPECTED_PROCESS_OUTPUT_PACKET)
            + "`",
            "- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
            + ",".join(
                [
                    *(f"zigux/tests/fixtures/genksyms_bridge/{name}" for name in EXPECTED_PROCESS_OUTPUT_PACKET[:-1]),
                    "zigux/tests/fixtures/genksyms_bridge/missing.json",
                ]
            )
            + "`",
            1,
        )
        write_text(root, CLOSURE_NOTE, bad_closure)
        issues = collect_issues(root)
        assert any(code == "CLOSURE_PROCESS_OUTPUT_PACKET_MISMATCH" for code, _ in issues)
        checks += 1

        write_sample_root(root)
        manifest = read_json(root, MANIFEST)
        manifest["standalone_proof_packet"] = ["scripts/zigux/genksyms_inline_short_option_argument_test.zig"]
        write_text(root, MANIFEST, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("MISSING_STANDALONE_PROOF", EXPECTED_STANDALONE_PROOFS[0]) in issues
        checks += 1

        write_sample_root(root)
        write_text(root, BRIDGE_CHECKER, "")
        assert ("MISSING_BRIDGE_CHECKER_LINE", REQUIRED_BRIDGE_CHECKER_LINES[0]) in collect_issues(root)
        checks += 1

        write_sample_root(root)
        write_text(root, SELFTEST_ALIGNMENT, "")
        assert ("MISSING_ALIGNMENT_LINE", REQUIRED_ALIGNMENT_LINES[0]) in collect_issues(root)
        checks += 1

        write_sample_root(root)
        write_text(root, GENKSYMS_HELPER, "")
        assert ("MISSING_GENKSYMS_LINE", REQUIRED_GENKSYMS_LINES[0]) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CURRENT_GENKSYMS_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE2_CURRENT_GENKSYMS_EVIDENCE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the live Phase 2 Current Genksyms Evidence packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a passing sample root for focused replay validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CURRENT_GENKSYMS_EVIDENCE=pass")
    print(f"PHASE2_CURRENT_GENKSYMS_EVIDENCE_REQUIRED_FILE_COUNT=6")
    print(f"PHASE2_CURRENT_GENKSYMS_EVIDENCE_PROCESS_OUTPUT_COUNT={len(EXPECTED_PROCESS_OUTPUT_PACKET)}")
    print(f"PHASE2_CURRENT_GENKSYMS_EVIDENCE_STANDALONE_PROOF_COUNT={len(EXPECTED_STANDALONE_PROOFS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
