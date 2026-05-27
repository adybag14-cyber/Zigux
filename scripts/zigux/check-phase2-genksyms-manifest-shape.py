#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

EXPECTED_MANIFEST = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "bounded wrapper-first dual-implementation bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "case_count": 10,
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
        "dash_prefixed_short_option_arguments_as_data",
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
        "dash_prefixed_short_option_arguments_as_data_expected.json",
    ],
    "help_packet": [
        "help_expected.json",
    ],
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
        "genksyms bridge keeps dash-prefixed long option arguments as data",
        "genksyms bridge keeps dash-prefixed short option arguments as data",
        "genksyms bridge rejects more than sixteen reference files like the C harness",
    ],
}


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest_path = root / MANIFEST_REL
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict):
        return [("INVALID_MANIFEST_SHAPE", "root")]

    issues: list[tuple[str, str]] = []
    for key in ("tool", "status", "mode", "fixture_root", "fixture_case_source", "case_count"):
        if manifest.get(key) != EXPECTED_MANIFEST[key]:
            issues.append(("FIELD_MISMATCH", key))

    for key in (
        "cases",
        "bridge_expected_packet",
        "help_packet",
        "standalone_proof_packet",
        "process_output_packet",
        "helper_local_anchors",
    ):
        if manifest.get(key) != EXPECTED_MANIFEST[key]:
            issues.append(("LIST_MISMATCH", key))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_MANIFEST_SHAPE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_json(root / MANIFEST_REL, EXPECTED_MANIFEST)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_manifest_shape_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = root / MANIFEST_REL
        payload = read_json(path)
        assert isinstance(payload, dict)
        payload["mode"] = "bounded bridge"
        write_json(path, payload)
        assert ("FIELD_MISMATCH", "mode") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / MANIFEST_REL
        payload = read_json(path)
        assert isinstance(payload, dict)
        payload["cases"] = payload["cases"][:-1]
        write_json(path, payload)
        assert ("LIST_MISMATCH", "cases") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / MANIFEST_REL
        payload = read_json(path)
        assert isinstance(payload, dict)
        payload["bridge_expected_packet"][-1] = "dash_prefixed_short_option_arguments_expected.json"
        write_json(path, payload)
        assert ("LIST_MISMATCH", "bridge_expected_packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / MANIFEST_REL
        payload = read_json(path)
        assert isinstance(payload, dict)
        payload["process_output_packet"] = payload["process_output_packet"][:-1]
        write_json(path, payload)
        assert ("LIST_MISMATCH", "process_output_packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / MANIFEST_REL
        payload = read_json(path)
        assert isinstance(payload, dict)
        payload["standalone_proof_packet"] = []
        write_json(path, payload)
        assert ("LIST_MISMATCH", "standalone_proof_packet") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / MANIFEST_REL).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    print("PHASE2_GENKSYMS_MANIFEST_SHAPE_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_MANIFEST_SHAPE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    build_self_test_root(root)
    print(f"PHASE2_GENKSYMS_MANIFEST_SHAPE_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 genksyms manifest packet aligned to current master."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_MANIFEST_SHAPE=pass")
    print(f"PHASE2_GENKSYMS_MANIFEST_SHAPE_CASE_COUNT={len(EXPECTED_MANIFEST['cases'])}")
    print(
        "PHASE2_GENKSYMS_MANIFEST_SHAPE_PROCESS_OUTPUT_COUNT="
        f"{len(EXPECTED_MANIFEST['process_output_packet'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
