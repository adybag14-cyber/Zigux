#!/usr/bin/env python3
"""Guard the documented Phase 2 closure-validator process-output gap."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

GAP_NOTE_REL = Path("Documentation/zigux/phase2-closure-validator-process-output-gap.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")
MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

OMITTED_FIXTURE_BASENAME = "abbreviated_unexpected_long_help_argument_expected.json"
OMITTED_FIXTURE_REL = (
    "zigux/tests/fixtures/genksyms_bridge/" + OMITTED_FIXTURE_BASENAME
)

REQUIRED_NOTE_MARKERS = (
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`scripts/zigux/validate-phase2-closure.py`",
    "`Documentation/zigux/phase2-closure.md`",
    "manifest-backed process-output packet count: `10`",
    "closure-validator process-output packet count: `9`",
    OMITTED_FIXTURE_BASENAME,
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`",
    "`GENKSYMS_PROCESS_OUTPUT_RELS`",
    "`EXPECTED_MANIFEST_FIXTURE_ROSTER`",
    '`EXPECTED_GENKSYMS_MANIFEST["process_output_packet"]`',
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    note_text = read_text(resolve(root, GAP_NOTE_REL))
    validator_text = read_text(resolve(root, VALIDATOR_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    process_output_packet = manifest.get("process_output_packet")
    if not isinstance(process_output_packet, list) or not all(
        isinstance(item, str) for item in process_output_packet
    ):
        issues.append(("INVALID_MANIFEST_SHAPE", "process_output_packet"))
        return issues

    if OMITTED_FIXTURE_BASENAME not in process_output_packet:
        issues.append(("MISSING_MANIFEST_PROCESS_OUTPUT", OMITTED_FIXTURE_BASENAME))

    packet_count = len(process_output_packet)
    if packet_count != 10:
        issues.append(("UNEXPECTED_MANIFEST_PROCESS_OUTPUT_COUNT", str(packet_count)))

    validator_has_fixture = OMITTED_FIXTURE_REL in validator_text
    if validator_has_fixture:
        issues.append(("VALIDATOR_NO_LONGER_OMITS_FIXTURE", OMITTED_FIXTURE_REL))

    if f"manifest-backed process-output packet count: `{packet_count}`" not in note_text:
        issues.append(("STALE_NOTE_MANIFEST_COUNT", str(packet_count)))

    expected_validator_count = packet_count - 1
    if (
        f"closure-validator process-output packet count: `{expected_validator_count}`"
        not in note_text
    ):
        issues.append(("STALE_NOTE_VALIDATOR_COUNT", str(expected_validator_count)))

    if OMITTED_FIXTURE_BASENAME not in note_text:
        issues.append(("STALE_NOTE_OMITTED_FIXTURE", OMITTED_FIXTURE_BASENAME))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    note = """# Phase 2 Closure Validator Process-Output Gap

This note records the current Lane 22 truthfulness gap between the live
genksyms manifest packet and the narrower process-output packet still embedded
in `scripts/zigux/validate-phase2-closure.py` on current `master`.

## Current Live Packet

- authority packet:
  - `zigux/tests/fixtures/genksyms_bridge/manifest.json`
  - `scripts/zigux/validate-phase2-closure.py`
  - `Documentation/zigux/phase2-closure.md`
- manifest-backed process-output packet count: `10`
- closure-validator process-output packet count: `9`

## Current Mismatch

- `zigux/tests/fixtures/genksyms_bridge/manifest.json` includes:
  - abbreviated_unexpected_long_help_argument_expected.json
- `scripts/zigux/validate-phase2-closure.py` currently omits:
  - `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
- `Documentation/zigux/phase2-closure.md` still omits the same fixture from the
  closure-side process-output roster.

## Next Safe Step

- restack `scripts/zigux/validate-phase2-closure.py` so
  `GENKSYMS_PROCESS_OUTPUT_RELS`, `EXPECTED_MANIFEST_FIXTURE_ROSTER`, and
  `EXPECTED_GENKSYMS_MANIFEST["process_output_packet"]` all include
  abbreviated_unexpected_long_help_argument_expected.json
"""
    validator = """GENKSYMS_PROCESS_OUTPUT_RELS = (
    Path(\"zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json\"),
    Path(\"zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json\"),
)
"""
    manifest = {
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
        ]
    }
    write_text(resolve(root, GAP_NOTE_REL), note)
    write_text(resolve(root, VALIDATOR_REL), validator)
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_gap_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        note_path = resolve(root, GAP_NOTE_REL)
        note_path.write_text(
            note_path.read_text(encoding="utf-8").replace(
                f"`{OMITTED_FIXTURE_REL}`", "`zigux/tests/fixtures/genksyms_bridge/different_expected.json`", 1
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_NOTE_MARKER",
            f"`{OMITTED_FIXTURE_REL}`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(
                'Path(\"zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json\"),',
                'Path(\"zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json\"),\n'
                '    Path(\"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json\"),',
                1,
            ),
            encoding="utf-8",
        )
        assert ("VALIDATOR_NO_LONGER_OMITS_FIXTURE", OMITTED_FIXTURE_REL) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["process_output_packet"].remove(OMITTED_FIXTURE_BASENAME)
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_PROCESS_OUTPUT", OMITTED_FIXTURE_BASENAME) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["process_output_packet"].append("extra_expected.json")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_MANIFEST_PROCESS_OUTPUT_COUNT", "11") in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the documented Phase 2 closure-validator process-output gap."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP_OMITTED_FIXTURE={OMITTED_FIXTURE_BASENAME}")
    print("PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP_MANIFEST_COUNT=10")
    print("PHASE2_CLOSURE_VALIDATOR_PROCESS_OUTPUT_GAP_VALIDATOR_COUNT=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
