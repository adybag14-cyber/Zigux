#!/usr/bin/env python3
"""Guard the shared Phase 2 genksyms process-output packet in the closure note."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
CLOSURE = Path("Documentation/zigux/phase2-closure.md")
MANIFEST = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")

EXPECTED_PROCESS_OUTPUT_PACKET = (
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
)

REQUIRED_CLOSURE_MARKERS = (
    "## Current Genksyms Evidence",
    "- `zigux/tests/fixtures/genksyms_bridge/manifest.json` remains the live packet manifest, and `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set instead of sitting only in the helper-local manifest.",
    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=" + ",".join(EXPECTED_PROCESS_OUTPUT_PACKET),
)

EXPECTED_SELF_TEST_CASE_COUNT = 5


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def parse_closure_packet(closure_text: str) -> tuple[str, ...] | None:
    prefix = "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
    for line in closure_text.splitlines():
        if line.startswith(prefix):
            payload = line.split("=", 1)[1]
            if not payload:
                return tuple()
            return tuple(part.strip() for part in payload.split(","))
    return None


def parse_manifest_packet(root: Path) -> tuple[str, ...]:
    payload = json.loads(read_text(resolve(root, MANIFEST)))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid manifest shape: {resolve(root, MANIFEST)}")
    fixture_root = payload.get("fixture_root")
    process_output_packet = payload.get("process_output_packet")
    if fixture_root != "zigux/tests/fixtures/genksyms_bridge":
        raise SystemExit(f"unexpected fixture_root in {resolve(root, MANIFEST)}")
    if not isinstance(process_output_packet, list) or not all(isinstance(item, str) for item in process_output_packet):
        raise SystemExit(f"invalid process_output_packet in {resolve(root, MANIFEST)}")
    return tuple(f"{fixture_root}/{entry}" for entry in process_output_packet)


def parse_validator_packet(root: Path) -> tuple[str, ...]:
    validator_text = read_text(resolve(root, VALIDATOR))
    prefix = "GENKSYMS_PROCESS_OUTPUT_FIXTURES = "
    start = validator_text.find(prefix + "(")
    if start == -1:
        raise SystemExit(f"missing GENKSYMS_PROCESS_OUTPUT_FIXTURES in {resolve(root, VALIDATOR)}")
    tuple_start = validator_text.find("(", start)
    depth = 0
    tuple_end = None
    for index in range(tuple_start, len(validator_text)):
        char = validator_text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                tuple_end = index + 1
                break
    if tuple_end is None:
        raise SystemExit(f"unterminated GENKSYMS_PROCESS_OUTPUT_FIXTURES in {resolve(root, VALIDATOR)}")
    tuple_text = validator_text[tuple_start:tuple_end]
    try:
        parsed = ast.literal_eval(tuple_text)
    except (SyntaxError, ValueError) as exc:
        raise SystemExit(f"invalid GENKSYMS_PROCESS_OUTPUT_FIXTURES in {resolve(root, VALIDATOR)}: {exc}") from exc
    if not isinstance(parsed, tuple) or not all(isinstance(item, str) for item in parsed):
        raise SystemExit(f"invalid GENKSYMS_PROCESS_OUTPUT_FIXTURES shape in {resolve(root, VALIDATOR)}")
    return tuple(parsed)


def build_sample_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

## Current Genksyms Evidence

- `zigux/tests/fixtures/genksyms_bridge/manifest.json` remains the live packet manifest, and `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set instead of sitting only in the helper-local manifest.
- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=` is the directly replayable closure-side sentinel for the current process-output roster.
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json
"""
    manifest_payload = {
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
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
    validator_text = """#!/usr/bin/env python3
from __future__ import annotations

GENKSYMS_PROCESS_OUTPUT_FIXTURES = (
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
)
"""
    write_text(resolve(root, CLOSURE), closure_text)
    write_text(resolve(root, MANIFEST), json.dumps(manifest_payload, indent=2) + "\n")
    write_text(resolve(root, VALIDATOR), validator_text)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve(root, CLOSURE))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    closure_packet = parse_closure_packet(closure_text)
    if closure_packet is None:
        issues.append(("MISSING_CLOSURE_PACKET", "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET"))
    elif closure_packet != EXPECTED_PROCESS_OUTPUT_PACKET:
        issues.append(("CLOSURE_PACKET_DRIFT", json.dumps(closure_packet)))

    manifest_packet = parse_manifest_packet(root)
    if manifest_packet != EXPECTED_PROCESS_OUTPUT_PACKET:
        issues.append(("MANIFEST_PACKET_DRIFT", json.dumps(manifest_packet)))

    validator_packet = parse_validator_packet(root)
    if validator_packet != EXPECTED_PROCESS_OUTPUT_PACKET:
        issues.append(("VALIDATOR_PACKET_DRIFT", json.dumps(validator_packet)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET=fail")
    for code, value in issues:
        print(f"{code}={value}")
    return 1


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_process_output_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        closure_path = resolve(root, CLOSURE)
        write_text(closure_path, read_text(closure_path).replace(REQUIRED_CLOSURE_MARKERS[1] + "\n", "", 1))
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = resolve(root, MANIFEST)
        manifest_payload = json.loads(read_text(manifest_path))
        manifest_payload["process_output_packet"].pop()
        write_text(manifest_path, json.dumps(manifest_payload, indent=2) + "\n")
        issues = collect_issues(root)
        assert any(code == "MANIFEST_PACKET_DRIFT" for code, _ in issues)
        checks += 1

        build_sample_root(root)
        validator_path = resolve(root, VALIDATOR)
        write_text(
            validator_path,
            read_text(validator_path).replace(
                '"zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",\n',
                "",
                1,
            ),
        )
        issues = collect_issues(root)
        assert any(code == "VALIDATOR_PACKET_DRIFT" for code, _ in issues)
        checks += 1

        build_sample_root(root)
        resolve(root, VALIDATOR).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
        else:
            raise AssertionError("missing validator did not abort")
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="Write a compact passing sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET=pass")
    print(f"PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET_COUNT={len(EXPECTED_PROCESS_OUTPUT_PACKET)}")
    print(f"PHASE2_GENKSYMS_PROCESS_OUTPUT_PACKET_VALIDATOR_COUNT={len(parse_validator_packet(args.root.resolve()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
