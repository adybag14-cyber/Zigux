#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"

TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet",
    "- `scripts/zigux/check-genksyms-bridge.py`",
    "- `scripts/zigux/genksyms.zig`",
    "- `make -C zigux phase2-genksyms`",
    "- `zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "- `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
)

MANIFEST_PRESENT_SURFACE_MARKERS = (
    "\"zigux/tests/README.md\"",
    "\"scripts/zigux/check-genksyms-bridge.py\"",
    "\"scripts/zigux/genksyms.zig\"",
    "\"make -C zigux phase2-genksyms\"",
)

MANIFEST_FIXTURE_MARKERS = (
    "\"zigux/tests/fixtures/genksyms_bridge/cases.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/help_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/minimal_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/long_options_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json\"",
    "\"zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json\"",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_README_MARKERS,
            "MISSING_TESTS_README_MARKERS",
        )
    )
    manifest_text = read_text(resolve_path(root, TOOL_MANIFEST))
    issues.extend(
        collect_missing_markers(
            manifest_text,
            MANIFEST_PRESENT_SURFACE_MARKERS,
            "MISSING_MANIFEST_PRESENT_SURFACE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            manifest_text,
            MANIFEST_FIXTURE_MARKERS,
            "MISSING_MANIFEST_FIXTURE_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TESTS_README_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, TESTS_README), "\n".join(TESTS_README_MARKERS) + "\n")
    manifest_payload = (
        "{\n"
        '  "present_surfaces": [\n    '
        + ",\n    ".join(MANIFEST_PRESENT_SURFACE_MARKERS)
        + "\n  ],\n"
        '  "fixture_roster": [\n    '
        + ",\n    ".join(MANIFEST_FIXTURE_MARKERS)
        + "\n  ]\n"
        "}\n"
    )
    write_text(resolve_path(root, TOOL_MANIFEST), manifest_payload)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(TESTS_README_MARKERS) + len(MANIFEST_PRESENT_SURFACE_MARKERS) + len(MANIFEST_FIXTURE_MARKERS) + 2
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_tests_readme_genksyms_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TESTS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_TESTS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in MANIFEST_PRESENT_SURFACE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_PRESENT_SURFACE_MARKERS", marker) in issues
            checks_run += 1

        for marker in MANIFEST_FIXTURE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOL_MANIFEST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_MANIFEST_FIXTURE_MARKERS", marker) in issues
            checks_run += 1

        for rel_path in (TESTS_README, TOOL_MANIFEST):
            build_self_test_root(root)
            resolve_path(root, rel_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel_path}")

    assert checks_run == expected_case_count
    print("PHASE2_TESTS_README_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the tests-root Phase 2 genksyms reminder aligned with the current manifest-backed packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TESTS_README_GENKSYMS_PACKET=pass")
    print(f"PHASE2_TESTS_README_GENKSYMS_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(
        "PHASE2_TESTS_README_GENKSYMS_PACKET_MANIFEST_MARKER_COUNT="
        f"{len(MANIFEST_PRESENT_SURFACE_MARKERS) + len(MANIFEST_FIXTURE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
