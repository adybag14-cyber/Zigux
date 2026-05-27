#!/usr/bin/env python3
"""Fail closed when the Phase 2 closure validator drifts from the live genksyms packet."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

VALIDATOR_REL = Path("scripts/zigux/validate-phase2-closure.py")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase2-closure.md")
CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

PROCESS_OUTPUT_PREFIX = "zigux/tests/fixtures/genksyms_bridge/"
OMITTED_FIXTURE = "abbreviated_unexpected_long_help_argument_expected.json"


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


def extract_literal(module: ast.Module, const_name: str, *, source_path: Path) -> object:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == const_name:
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError) as exc:
                        raise SystemExit(
                            f"invalid literal for {const_name} in {source_path}: {exc}"
                        ) from exc
    raise SystemExit(f"missing constant {const_name} in {source_path}")


def extract_path_sequence(module: ast.Module, const_name: str, *, source_path: Path) -> tuple[Path, ...]:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == const_name:
                    value = node.value
                    if not isinstance(value, (ast.Tuple, ast.List)):
                        raise SystemExit(
                            f"expected tuple/list for {const_name} in {source_path}"
                        )
                    paths: list[Path] = []
                    for elt in value.elts:
                        if (
                            not isinstance(elt, ast.Call)
                            or not isinstance(elt.func, ast.Name)
                            or elt.func.id != "Path"
                            or len(elt.args) != 1
                            or not isinstance(elt.args[0], ast.Constant)
                            or not isinstance(elt.args[0].value, str)
                        ):
                            raise SystemExit(
                                f"expected Path(\"...\") entry in {const_name} in {source_path}"
                            )
                        paths.append(Path(elt.args[0].value))
                    return tuple(paths)
    raise SystemExit(f"missing constant {const_name} in {source_path}")


def parse_validator(path: Path) -> dict[str, object]:
    try:
        module = ast.parse(read_text(path), filename=path.as_posix())
    except SyntaxError as exc:
        raise SystemExit(f"invalid python in {path}: {exc}") from exc

    return {
        "genksyms_process_output_rels": extract_path_sequence(
            module, "GENKSYMS_PROCESS_OUTPUT_RELS", source_path=path
        ),
        "expected_manifest_fixture_roster": extract_literal(
            module, "EXPECTED_MANIFEST_FIXTURE_ROSTER", source_path=path
        ),
        "expected_genksyms_cases": extract_literal(
            module, "EXPECTED_GENKSYMS_CASES", source_path=path
        ),
        "expected_genksyms_manifest": extract_literal(
            module, "EXPECTED_GENKSYMS_MANIFEST", source_path=path
        ),
        "required_closure_markers": extract_literal(
            module, "REQUIRED_CLOSURE_MARKERS", source_path=path
        ),
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    validator_path = resolve(root, VALIDATOR_REL)
    closure_note_path = resolve(root, CLOSURE_NOTE_REL)
    cases_path = resolve(root, CASES_REL)
    manifest_path = resolve(root, MANIFEST_REL)

    validator = parse_validator(validator_path)
    closure_text = read_text(closure_note_path)
    cases = read_json(cases_path)
    manifest = read_json(manifest_path)

    issues: list[tuple[str, str]] = []

    if not isinstance(cases, list) or not all(isinstance(item, dict) for item in cases):
        issues.append(("INVALID_CASES_PAYLOAD", CASES_REL.as_posix()))
        return issues
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_PAYLOAD", MANIFEST_REL.as_posix()))
        return issues

    process_output_packet = manifest.get("process_output_packet")
    if not isinstance(process_output_packet, list) or not all(
        isinstance(item, str) for item in process_output_packet
    ):
        issues.append(("INVALID_MANIFEST_PROCESS_OUTPUT_PACKET", MANIFEST_REL.as_posix()))
        return issues

    expected_case_packet = [
        {
            "name": item.get("name"),
            "args": item.get("args"),
            "expected_file": item.get("expected_file"),
        }
        for item in cases
    ]
    if validator["expected_genksyms_cases"] != expected_case_packet:
        issues.append(("STALE_EXPECTED_GENKSYMS_CASES", "EXPECTED_GENKSYMS_CASES"))

    expected_process_output_rels = tuple(
        Path(PROCESS_OUTPUT_PREFIX + item) for item in process_output_packet
    )
    if validator["genksyms_process_output_rels"] != expected_process_output_rels:
        issues.append(
            (
                "STALE_GENKSYMS_PROCESS_OUTPUT_RELS",
                ",".join(item.as_posix() for item in expected_process_output_rels),
            )
        )

    expected_manifest = {
        "tool": manifest.get("tool"),
        "status": manifest.get("status"),
        "mode": manifest.get("mode"),
        "fixture_root": manifest.get("fixture_root"),
        "fixture_case_source": manifest.get("fixture_case_source"),
        "case_count": manifest.get("case_count"),
        "cases": manifest.get("cases"),
        "bridge_expected_packet": manifest.get("bridge_expected_packet"),
        "help_packet": manifest.get("help_packet"),
        "standalone_proof_packet": manifest.get("standalone_proof_packet"),
        "process_output_packet": manifest.get("process_output_packet"),
        "helper_local_anchors": manifest.get("helper_local_anchors"),
    }
    if validator["expected_genksyms_manifest"] != expected_manifest:
        issues.append(("STALE_EXPECTED_GENKSYMS_MANIFEST", "EXPECTED_GENKSYMS_MANIFEST"))

    fixture_roster = validator["expected_manifest_fixture_roster"]
    if not isinstance(fixture_roster, tuple):
        issues.append(("INVALID_EXPECTED_MANIFEST_FIXTURE_ROSTER", "not-a-tuple"))
    else:
        for fixture in process_output_packet:
            prefixed = PROCESS_OUTPUT_PREFIX + fixture
            if prefixed not in fixture_roster:
                issues.append(("MISSING_FIXTURE_ROSTER_ENTRY", prefixed))

    required_markers = validator["required_closure_markers"]
    if not isinstance(required_markers, tuple):
        issues.append(("INVALID_REQUIRED_CLOSURE_MARKERS", "not-a-tuple"))
    else:
        marker = f"`{PROCESS_OUTPUT_PREFIX + OMITTED_FIXTURE}`"
        if OMITTED_FIXTURE in process_output_packet and marker not in required_markers:
            issues.append(("MISSING_REQUIRED_CLOSURE_MARKER", marker))

    note_marker = f"`{PROCESS_OUTPUT_PREFIX + OMITTED_FIXTURE}`"
    if OMITTED_FIXTURE in process_output_packet and note_marker not in closure_text:
        issues.append(("MISSING_CLOSURE_NOTE_FIXTURE", note_marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    validator = """#!/usr/bin/env python3
from pathlib import Path

GENKSYMS_PROCESS_OUTPUT_RELS = (
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json"),
)

EXPECTED_MANIFEST_FIXTURE_ROSTER = (
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

EXPECTED_GENKSYMS_CASES = [
    {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
    {
        "name": "dash_prefixed_short_option_arguments_as_data",
        "args": ["-r", "-d", "-T", "--symtypes"],
        "expected_file": "dash_prefixed_short_option_arguments_as_data_expected.json",
    },
]

EXPECTED_GENKSYMS_MANIFEST = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "bounded wrapper-first dual-implementation bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "case_count": 2,
    "cases": ["minimal", "dash_prefixed_short_option_arguments_as_data"],
    "bridge_expected_packet": [
        "minimal_expected.json",
        "dash_prefixed_short_option_arguments_as_data_expected.json",
    ],
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
    "helper_local_anchors": [
        "genksyms bridge treats pure version requests as version command",
    ],
}

REQUIRED_CLOSURE_MARKERS = (
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`",
)
"""
    closure = """# Phase 2 Closure

- `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
"""
    cases = [
        {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
        {
            "name": "dash_prefixed_short_option_arguments_as_data",
            "args": ["-r", "-d", "-T", "--symtypes"],
            "expected_file": "dash_prefixed_short_option_arguments_as_data_expected.json",
        },
    ]
    manifest = {
        "tool": "scripts/zigux/genksyms.zig",
        "status": "closed",
        "mode": "bounded wrapper-first dual-implementation bridge",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
        "case_count": 2,
        "cases": ["minimal", "dash_prefixed_short_option_arguments_as_data"],
        "bridge_expected_packet": [
            "minimal_expected.json",
            "dash_prefixed_short_option_arguments_as_data_expected.json",
        ],
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
        "helper_local_anchors": [
            "genksyms bridge treats pure version requests as version command",
        ],
    }

    write_text(resolve(root, VALIDATOR_REL), validator)
    write_text(resolve(root, CLOSURE_NOTE_REL), closure)
    write_text(resolve(root, CASES_REL), json.dumps(cases, indent=2) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_genksyms_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(
                '    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json"),\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert any(code == "STALE_GENKSYMS_PROCESS_OUTPUT_RELS" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["mode"] = "bounded bridge"
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("STALE_EXPECTED_GENKSYMS_MANIFEST", "EXPECTED_GENKSYMS_MANIFEST") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve(root, CLOSURE_NOTE_REL)
        closure_path.write_text("# Phase 2 Closure\n", encoding="utf-8")
        assert (
            "MISSING_CLOSURE_NOTE_FIXTURE",
            "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        validator_path = resolve(root, VALIDATOR_REL)
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(
                '"name": "dash_prefixed_short_option_arguments_as_data"',
                '"name": "help"',
                1,
            ),
            encoding="utf-8",
        )
        assert ("STALE_EXPECTED_GENKSYMS_CASES", "EXPECTED_GENKSYMS_CASES") in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the Phase 2 closure validator drifts from the live genksyms packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET_PROCESS_OUTPUT_COUNT=10")
    print(f"PHASE2_CLOSURE_VALIDATOR_GENKSYMS_PACKET_CASE_COUNT=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
