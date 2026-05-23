#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_ROOT = ROOT

CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

REQUIRED_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`",
)

EXPECTED_PHASE2_BRIDGE_HELPERS = (
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

EXPECTED_PHASE2_CHECKERS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
)

EXPECTED_PHASE2_FIXTURES = (
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
)

EXPECTED_GENKSYMS_MANIFEST = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "bounded wrapper-first dual-implementation bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "case_count": 9,
    "cases": [
        "minimal",
        "debug_reference_types",
        "long_options",
        "abbreviated_long_options",
        "quiet_overrides_warning",
        "explicit_option_terminator",
        "positional_passthrough",
        "lone_dash_passthrough",
        "dash_prefixed_long_option_arguments_as_data",
    ],
    "bridge_expected_packet": [
        "minimal_expected.json",
        "debug_reference_types_expected.json",
        "long_options_expected.json",
        "abbreviated_long_options_expected.json",
        "quiet_overrides_warning_expected.json",
        "explicit_option_terminator_expected.json",
        "positional_passthrough_expected.json",
        "lone_dash_passthrough_expected.json",
        "dash_prefixed_long_option_arguments_as_data_expected.json",
    ],
    "help_packet": ["help_expected.json"],
    "standalone_proof_packet": [
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"
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
    ],
    "helper_local_anchors": [
        "genksyms bridge treats pure version requests as version command",
        "genksyms bridge preserves repeated pure version invocations",
        "genksyms bridge preserves empty inline long reference argument",
        "genksyms bridge preserves empty inline abbreviated dump-types argument",
        "parseArgs reports ambiguous abbreviated long options",
        "genksyms bridge renders ambiguous long option failure like the fixture",
        "genksyms bridge renders invalid short option failure like the fixture",
        "genksyms bridge renders missing long option argument like the fixture",
        "genksyms bridge renders missing short option argument like the fixture",
        "genksyms bridge renders unexpected long option argument like the fixture",
        "genksyms bridge appends usage after getopt-style parse failures",
        "genksyms bridge leaves tool-local reference-limit failure message unchanged",
        "genksyms bridge rejects more than sixteen reference files like the C harness",
    ],
}


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


def require_manifest_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str] | None:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(
    issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]
) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_PHASE2_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(root / CLOSURE_REL)
    phase2_manifest = read_json(root / PHASE2_MANIFEST_REL)
    genksyms_manifest = read_json(root / GENKSYMS_MANIFEST_REL)

    if not isinstance(phase2_manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    expect_subset(
        issues,
        "bridge_helpers",
        require_manifest_list(issues, phase2_manifest, "bridge_helpers"),
        EXPECTED_PHASE2_BRIDGE_HELPERS,
    )
    expect_subset(
        issues,
        "checkers",
        require_manifest_list(issues, phase2_manifest, "checkers"),
        EXPECTED_PHASE2_CHECKERS,
    )
    expect_subset(
        issues,
        "fixture_roster",
        require_manifest_list(issues, phase2_manifest, "fixture_roster"),
        EXPECTED_PHASE2_FIXTURES,
    )

    if genksyms_manifest != EXPECTED_GENKSYMS_MANIFEST:
        issues.append(("GENKSYMS_MANIFEST_MISMATCH", "root"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    closure_lines = [
        "# Phase 2 Closure",
        "",
        *[f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS],
        "",
    ]
    phase2_manifest = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "bridge_helpers": list(EXPECTED_PHASE2_BRIDGE_HELPERS),
            "checkers": list(EXPECTED_PHASE2_CHECKERS),
            "fixture_roster": list(EXPECTED_PHASE2_FIXTURES),
        },
    }

    write_text(root / CLOSURE_REL, "\n".join(closure_lines))
    write_text(root / PHASE2_MANIFEST_REL, json.dumps(phase2_manifest, indent=2) + "\n")
    write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(EXPECTED_GENKSYMS_MANIFEST, indent=2) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane22_closure_genksyms_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        closure_path = root / CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = root / PHASE2_MANIFEST_REL
        phase2_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        phase2_manifest["present_surfaces"]["bridge_helpers"].remove(
            "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
        )
        manifest_path.write_text(json.dumps(phase2_manifest, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_PHASE2_MANIFEST_SURFACE",
            "bridge_helpers:scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest_path = root / PHASE2_MANIFEST_REL
        phase2_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        phase2_manifest["present_surfaces"]["fixture_roster"].remove(
            "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json"
        )
        manifest_path.write_text(json.dumps(phase2_manifest, indent=2) + "\n", encoding="utf-8")
        assert (
            "MISSING_PHASE2_MANIFEST_SURFACE",
            "fixture_roster:zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        genksyms_manifest_path = root / GENKSYMS_MANIFEST_REL
        genksyms_manifest = json.loads(genksyms_manifest_path.read_text(encoding="utf-8"))
        genksyms_manifest["case_count"] = 8
        genksyms_manifest_path.write_text(
            json.dumps(genksyms_manifest, indent=2) + "\n", encoding="utf-8"
        )
        assert ("GENKSYMS_MANIFEST_MISMATCH", "root") in collect_issues(root)
        checks += 1

    print("PHASE2_CLOSURE_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Lane 22 closure-side genksyms packet against the live closure note and manifests."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree for focused validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_GENKSYMS_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_GENKSYMS_PACKET=pass")
    print("PHASE2_CLOSURE_GENKSYMS_VERSION_PROOF_COUNT=2")
    print("PHASE2_CLOSURE_GENKSYMS_CASE_COUNT=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
