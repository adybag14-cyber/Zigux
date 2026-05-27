#!/usr/bin/env python3
"""Validate the Phase 2 tests README against the genksyms process-output packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3] if len(HERE.parents) >= 4 else Path.cwd()
TESTS_README_REL = Path("zigux/tests/README.md")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
FIXTURE_PREFIX = "zigux/tests/fixtures/genksyms_bridge/"


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


def require_process_output_packet(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        raise SystemExit("genksyms manifest has invalid top-level shape")
    packet = manifest.get("process_output_packet")
    if not isinstance(packet, list) or not all(isinstance(item, str) for item in packet):
        raise SystemExit("genksyms manifest is missing a string-only process_output_packet")
    return list(packet)


def expected_markers(packet: list[str]) -> list[str]:
    return [f"`{FIXTURE_PREFIX}{name}`" for name in packet]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    readme_text = read_text(resolve(root, TESTS_README_REL))
    manifest = read_json(resolve(root, GENKSYMS_MANIFEST_REL))
    packet = require_process_output_packet(manifest)

    issues: list[tuple[str, str]] = []
    for marker in expected_markers(packet):
        if marker not in readme_text:
            issues.append(("MISSING_PROCESS_OUTPUT_MARKER", marker))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    manifest = {
        "tool": "scripts/zigux/genksyms.zig",
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
    lines = [
        "# zigux/tests",
        "",
        "## Phase 2 review packet",
        "",
        *[f"  * `{FIXTURE_PREFIX}{name}`" for name in manifest["process_output_packet"]],
        "",
    ]

    write_text(resolve(root, TESTS_README_REL), "\n".join(lines))
    write_text(
        resolve(root, GENKSYMS_MANIFEST_REL),
        json.dumps(manifest, indent=2) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_tests_readme_process_output_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        readme_path = resolve(root, TESTS_README_REL)
        marker = f"`{FIXTURE_PREFIX}abbreviated_unexpected_long_help_argument_expected.json`"
        readme_path.write_text(read_text(readme_path).replace(f"  * {marker}\n", "", 1), encoding="utf-8")
        assert ("MISSING_PROCESS_OUTPUT_MARKER", marker) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
        manifest = json.loads(read_text(manifest_path))
        manifest["process_output_packet"] = ["invalid_option_expected.json"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert issues == []
        checks_run += 1

        build_sample_root(root)
        manifest_path.write_text("{\"process_output_packet\": [1]}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "process_output_packet" in str(exc)
        else:
            raise AssertionError("invalid manifest shape did not stop validation")
        checks_run += 1

    print("PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in regression checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a passing sample root to the given directory and exit",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    packet = require_process_output_packet(read_json(resolve(args.root.resolve(), GENKSYMS_MANIFEST_REL)))
    print("PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET=pass")
    print(f"PHASE2_TESTS_README_PROCESS_OUTPUT_PACKET_COUNT={len(packet)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
