#!/usr/bin/env python3
"""Guard the shipped Lane 24 abbreviated-unexpected-help process-output packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase2.py")
TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
FIXTURE_REL = Path(
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json"
)

VALIDATOR_MARKER = f'"{FIXTURE_REL.as_posix()}",'
TOOL_MANIFEST_PACKET = "fixture_roster"
GENKSYMS_PROCESS_PACKET = "process_output_packet"
GENKSYMS_FIXTURE_BASENAME = FIXTURE_REL.name


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_string_list(
    issues: list[tuple[str, str]], payload: dict[str, object], key: str
) -> list[str] | None:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_PACKET", key))
        return None
    return list(value)


def require_present_surfaces_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_TOOL_MANIFEST", "present_surfaces"))
        return None
    return require_string_list(issues, surfaces, key)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    validator_path = resolve(root, VALIDATOR_REL)
    tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
    genksyms_manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
    fixture_path = resolve(root, FIXTURE_REL)

    for path in (validator_path, tool_manifest_path, genksyms_manifest_path, fixture_path):
        if not path.exists():
            issues.append(("MISSING_REQUIRED_FILE", path.relative_to(root).as_posix()))
    if issues:
        return issues

    validator_text = read_text(validator_path)
    tool_manifest = read_json(tool_manifest_path)
    genksyms_manifest = read_json(genksyms_manifest_path)

    if not isinstance(tool_manifest, dict):
        issues.append(("INVALID_TOOL_MANIFEST", "root"))
        return issues
    if not isinstance(genksyms_manifest, dict):
        issues.append(("INVALID_GENKSYMS_MANIFEST", "root"))
        return issues

    validator_count = count_exact_lines(validator_text, VALIDATOR_MARKER)
    if validator_count == 0:
        issues.append(("MISSING_VALIDATOR_MARKER", VALIDATOR_MARKER))
    elif validator_count != 1:
        issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{VALIDATOR_MARKER}:count={validator_count}"))

    fixture_roster = require_present_surfaces_list(issues, tool_manifest, TOOL_MANIFEST_PACKET)
    if fixture_roster is not None:
        roster_count = fixture_roster.count(FIXTURE_REL.as_posix())
        if roster_count == 0:
            issues.append(("MISSING_TOOL_MANIFEST_FIXTURE", FIXTURE_REL.as_posix()))
        elif roster_count != 1:
            issues.append(("DUPLICATE_TOOL_MANIFEST_FIXTURE", f"{FIXTURE_REL.as_posix()}:count={roster_count}"))

    process_output_packet = require_string_list(issues, genksyms_manifest, GENKSYMS_PROCESS_PACKET)
    if process_output_packet is not None:
        packet_count = process_output_packet.count(GENKSYMS_FIXTURE_BASENAME)
        if packet_count == 0:
            issues.append(("MISSING_GENKSYMS_PACKET_FIXTURE", GENKSYMS_FIXTURE_BASENAME))
        elif packet_count != 1:
            issues.append(("DUPLICATE_GENKSYMS_PACKET_FIXTURE", f"{GENKSYMS_FIXTURE_BASENAME}:count={packet_count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    validator_text = "\n".join(
        (
            "GENKSYMS_PROCESS_OUTPUT_FIXTURES = (",
            "    \"zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json\",",
            f"    {VALIDATOR_MARKER}",
            ")",
            "",
        )
    )
    tool_manifest = {
        "present_surfaces": {
            TOOL_MANIFEST_PACKET: [
                "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
                FIXTURE_REL.as_posix(),
            ]
        }
    }
    genksyms_manifest = {
        GENKSYMS_PROCESS_PACKET: [
            "unexpected_long_help_argument_expected.json",
            GENKSYMS_FIXTURE_BASENAME,
        ]
    }

    write_text(resolve(root, VALIDATOR_REL), validator_text)
    write_text(resolve(root, TOOL_MANIFEST_REL), json.dumps(tool_manifest, indent=2) + "\n")
    write_text(resolve(root, GENKSYMS_MANIFEST_REL), json.dumps(genksyms_manifest, indent=2) + "\n")
    write_text(resolve(root, FIXTURE_REL), "{}\n")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane24_abbrev_unexpected_help_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            replace_exact_line(validator_path.read_text(encoding="utf-8"), VALIDATOR_MARKER, "    \"other.json\","),
            encoding="utf-8",
        )
        assert ("MISSING_VALIDATOR_MARKER", VALIDATOR_MARKER) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
        payload = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"][TOOL_MANIFEST_PACKET].remove(FIXTURE_REL.as_posix())
        tool_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_TOOL_MANIFEST_FIXTURE", FIXTURE_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        genksyms_manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
        payload = json.loads(genksyms_manifest_path.read_text(encoding="utf-8"))
        payload[GENKSYMS_PROCESS_PACKET].remove(GENKSYMS_FIXTURE_BASENAME)
        genksyms_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_GENKSYMS_PACKET_FIXTURE", GENKSYMS_FIXTURE_BASENAME) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        resolve(root, FIXTURE_REL).unlink()
        assert ("MISSING_REQUIRED_FILE", FIXTURE_REL.as_posix()) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(VALIDATOR_MARKER, f"{VALIDATOR_MARKER}\n{VALIDATOR_MARKER}"),
            encoding="utf-8",
        )
        duplicate_issue = (
            "DUPLICATE_VALIDATOR_MARKER",
            f"{VALIDATOR_MARKER}:count=2",
        )
        assert duplicate_issue in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        tool_manifest_path = resolve(root, TOOL_MANIFEST_REL)
        payload = json.loads(tool_manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"][TOOL_MANIFEST_PACKET].append(FIXTURE_REL.as_posix())
        tool_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        duplicate_manifest_issue = (
            "DUPLICATE_TOOL_MANIFEST_FIXTURE",
            f"{FIXTURE_REL.as_posix()}:count=2",
        )
        assert duplicate_manifest_issue in collect_issues(root)
        checks_run += 1

    print("PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the shipped Lane 24 abbreviated-unexpected-help process-output packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local packet validation",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET=pass")
    print("PHASE2_GENKSYMS_ABBREVIATED_UNEXPECTED_HELP_PACKET_REQUIRED_FILE_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
