#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import tempfile
from pathlib import Path

CONFDATA_BRIDGE_PATH = Path("scripts/zigux/kconfig/confdata_bridge.zig")
CHECKER_PATH = Path("scripts/zigux/check-kconfig-bridge.py")
FIXTURE_DIR = Path("zigux/tests/fixtures/kconfig_bridge")
CASES_PATH = FIXTURE_DIR / "cases.json"
MANIFEST_PATH = FIXTURE_DIR / "confdata_manifest.json"

REQUIRED_PUBLIC_EXPORTS = [
    "pub const EntryKind = enum {",
    "pub const Entry = struct {",
    "pub const Summary = struct {",
    "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
    "pub fn deinitSummary(allocator: std.mem.Allocator, summary: *Summary) void {",
    "pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {",
]

REQUIRED_ENTRY_KINDS = ["tristate", "string", "value", "unset"]
REQUIRED_CONFDATA_CHECKER_LISTS = {
    "REQUIRED_CONFDATA_CASES": [
        "sample",
        "escaped_strings",
        "escaped_control_sequences",
        "trailing_escaped_backslash",
        "sample_crlf",
        "explicit_n_tristate",
        "final_trailing_carriage_return",
        "final_unterminated_unset_comment",
        "uppercase_tristate",
        "non_config_lines",
        "empty_config_symbol_names",
        "malformed_unset_comment_tokens",
        "last_state_transitions",
        "duplicate_assignments",
        "duplicate_malformed_quoted_assignment",
        "explicit_empty_assignments",
    ],
    "REQUIRED_CONFDATA_INPUT_PACKET": [
        "sample.config",
        "escaped_strings.config",
        "escaped_control_sequences.config",
        "trailing_escaped_backslash.config",
        "sample_crlf.config",
        "explicit_n_tristate.config",
        "final_trailing_carriage_return.config",
        "final_unterminated_unset_comment.config",
        "uppercase_tristate.config",
        "non_config_lines.config",
        "empty_config_symbol_names.config",
        "malformed_unset_comment_tokens.config",
        "last_state_transitions.config",
        "duplicate_assignments.config",
        "duplicate_malformed_quoted_assignment.config",
        "explicit_empty_assignments.config",
    ],
    "REQUIRED_CONFDATA_EXPECTED_PACKET": [
        "sample_expected.json",
        "escaped_strings_expected.json",
        "escaped_control_sequences_expected.json",
        "trailing_escaped_backslash_expected.json",
        "sample_crlf_expected.json",
        "explicit_n_tristate_expected.json",
        "final_trailing_carriage_return_expected.json",
        "final_unterminated_unset_comment_expected.json",
        "uppercase_tristate_expected.json",
        "non_config_lines_expected.json",
        "empty_config_symbol_names_expected.json",
        "malformed_unset_comment_tokens_expected.json",
        "last_state_transitions_expected.json",
        "duplicate_assignments_expected.json",
        "duplicate_malformed_quoted_assignment_expected.json",
        "explicit_empty_assignments_expected.json",
    ],
    "REQUIRED_CONFDATA_HELPER_ANCHORS": [
        "confdata bridge parses bounded config states",
        "confdata bridge emits bounded json output",
        "confdata bridge decodes escaped quoted strings",
        "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
        "confdata bridge escapes low control bytes in json output",
        "confdata bridge accepts CRLF config lines",
        "confdata bridge preserves trailing carriage return on final unterminated value line",
        "confdata bridge ignores unterminated unset comment with trailing carriage return",
        "confdata bridge ignores suffix bytes after an embedded NUL",
        "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
        "confdata bridge keeps explicit n assignments as tristate values",
        "confdata bridge recognizes uppercase tristate assignments",
        "confdata bridge ignores non-CONFIG lines like upstream confdata",
        "confdata bridge ignores empty CONFIG symbol names",
        "confdata bridge ignores malformed unset comments with extra tokens",
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
        "confdata bridge ignores malformed quoted values like upstream confdata",
        "confdata bridge emits no entries for empty CONFIG symbol names",
        "confdata bridge keeps only the last assignment for duplicate symbols",
        "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
        "confdata bridge emits the preserved duplicate state after later malformed quoted assignments",
        "confdata bridge keeps only the last state across unset and set transitions",
        "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
        "confdata bridge emits explicit empty assignments distinctly in json output",
        "confdata bridge escapes parsed string bytes in json output",
        "confdata bridge releases appended entry ownership on index-allocation failure",
        "confdata bridge preserves duplicate unset ownership on allocation failure",
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = 7


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise ValidationError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path):
    try:
        return json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json in {relative_path.as_posix()}: {exc.msg}") from exc


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_python_list(source: str, name: str) -> list[str]:
    match = re.search(rf"^{name}\s*=\s*(\[(?:.|\n)*?\])", source, re.M)
    if not match:
        raise ValidationError(f"missing checker list: {name}")
    try:
        return list(ast.literal_eval(match.group(1)))
    except (SyntaxError, ValueError) as exc:
        raise ValidationError(f"unable to parse checker list: {name}") from exc


def extract_entry_kind_names(confdata_source: str) -> list[str]:
    match = re.search(r"pub const EntryKind = enum \{(.*?)\n\s*pub fn text", confdata_source, re.S)
    if not match:
        raise ValidationError("missing EntryKind enum block in confdata bridge")
    names: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if line.endswith(","):
            candidate = line[:-1].strip()
            if candidate.isidentifier():
                names.append(candidate)
    return names


def extract_test_anchors(confdata_source: str) -> list[str]:
    anchors = re.findall(r'^test "([^"]+)" \{$', confdata_source, re.M)
    if not anchors:
        raise ValidationError("no confdata bridge test anchors found")
    return anchors


def collect_confdata_case_lists(payload: dict[str, object]) -> tuple[list[str], list[str], list[str]]:
    confdata_cases = payload.get("confdata_cases")
    if not isinstance(confdata_cases, list):
        raise ValidationError("cases.json is missing confdata_cases list")
    case_names: list[str] = []
    input_packet: list[str] = []
    expected_packet: list[str] = []
    seen_names: set[str] = set()
    for case in confdata_cases:
        if not isinstance(case, dict):
            raise ValidationError("confdata_cases contains a non-object entry")
        name = case.get("name")
        input_name = case.get("input")
        expected_name = case.get("expected")
        if not isinstance(name, str) or not isinstance(input_name, str) or not isinstance(expected_name, str):
            raise ValidationError("confdata_cases entry is missing name/input/expected strings")
        if name in seen_names:
            raise ValidationError(f"duplicate confdata case name: {name}")
        seen_names.add(name)
        case_names.append(name)
        input_packet.append(input_name)
        expected_packet.append(expected_name)
    return case_names, input_packet, expected_packet


def validate(root: Path) -> None:
    confdata_source = read_text(root, CONFDATA_BRIDGE_PATH)
    checker_source = read_text(root, CHECKER_PATH)
    cases_payload = load_json(root, CASES_PATH)
    manifest_payload = load_json(root, MANIFEST_PATH)

    if not isinstance(cases_payload, dict):
        raise ValidationError("cases.json must contain a top-level object")
    if not isinstance(manifest_payload, dict):
        raise ValidationError("confdata_manifest.json must contain a top-level object")

    for export_snippet in REQUIRED_PUBLIC_EXPORTS:
        if export_snippet not in confdata_source:
            raise ValidationError(f"missing required confdata export snippet: {export_snippet}")

    entry_kind_names = extract_entry_kind_names(confdata_source)
    if entry_kind_names != REQUIRED_ENTRY_KINDS:
        raise ValidationError(
            "EntryKind export order drifted: "
            f"actual={entry_kind_names!r} expected={REQUIRED_ENTRY_KINDS!r}"
        )

    for kind in REQUIRED_ENTRY_KINDS:
        if f' => "{kind}"' not in confdata_source:
            raise ValidationError(f"EntryKind.text mapping is missing export label: {kind}")

    actual_anchors = extract_test_anchors(confdata_source)
    checker_anchors = extract_python_list(checker_source, "REQUIRED_CONFDATA_HELPER_ANCHORS")
    if checker_anchors != REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_HELPER_ANCHORS"]:
        raise ValidationError("shared kconfig checker helper-anchor list drifted away from this lane guard")
    if actual_anchors != checker_anchors:
        raise ValidationError("confdata bridge test anchors drifted away from the shared checker list")
    manifest_anchors = manifest_payload.get("helper_local_anchors")
    if manifest_anchors != actual_anchors:
        raise ValidationError("confdata manifest helper_local_anchors drifted away from current source anchors")

    for list_name, expected_values in REQUIRED_CONFDATA_CHECKER_LISTS.items():
        actual_values = extract_python_list(checker_source, list_name)
        if actual_values != expected_values:
            raise ValidationError(
                f"shared kconfig checker list drifted for {list_name}: "
                f"actual={actual_values!r} expected={expected_values!r}"
            )

    case_names, input_packet, expected_packet = collect_confdata_case_lists(cases_payload)
    if case_names != REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_CASES"]:
        raise ValidationError("confdata case-name packet drifted away from the lane export map")
    if input_packet != REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_INPUT_PACKET"]:
        raise ValidationError("confdata input-packet drifted away from the lane export map")
    if expected_packet != REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_EXPECTED_PACKET"]:
        raise ValidationError("confdata expected-packet drifted away from the lane export map")

    if manifest_payload.get("cases") != case_names:
        raise ValidationError("confdata manifest case list drifted away from cases.json")
    if manifest_payload.get("input_packet") != input_packet:
        raise ValidationError("confdata manifest input_packet drifted away from cases.json")
    if manifest_payload.get("expected_packet") != expected_packet:
        raise ValidationError("confdata manifest expected_packet drifted away from cases.json")
    if manifest_payload.get("case_count") != len(case_names):
        raise ValidationError("confdata manifest case_count drifted away from the current confdata case set")

    for relative_name in [*input_packet, *expected_packet]:
        if not (root / FIXTURE_DIR / relative_name).is_file():
            raise ValidationError(f"missing required kconfig fixture artifact: {relative_name}")


def build_fixture_root(root: Path) -> None:
    confdata_source = """const std = @import(\"std\");

pub const EntryKind = enum {
    tristate,
    string,
    value,
    unset,

    pub fn text(self: EntryKind) []const u8 {
        return switch (self) {
            .tristate => \"tristate\",
            .string => \"string\",
            .value => \"value\",
            .unset => \"unset\",
        };
    }
};

pub const Entry = struct {
    name: []const u8,
    kind: EntryKind,
    value: []const u8,
};

pub const Summary = struct {
    entries: []Entry,
    set_count: usize,
    unset_count: usize,
};

pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {
    _ = allocator;
    _ = input;
    unreachable;
}

pub fn deinitSummary(allocator: std.mem.Allocator, summary: *Summary) void {
    _ = allocator;
    _ = summary;
}

pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {
    _ = allocator;
    _ = input;
    _ = writer;
}

"""
    for anchor in REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_HELPER_ANCHORS"]:
        confdata_source += f'test "{anchor}" {{\n    try std.testing.expect(true);\n}}\n\n'
    write_text(root, CONFDATA_BRIDGE_PATH, confdata_source)

    checker_lines = [
        "REQUIRED_CONFDATA_CASES = " + repr(REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_CASES"]),
        "REQUIRED_CONFDATA_INPUT_PACKET = " + repr(REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_INPUT_PACKET"]),
        "REQUIRED_CONFDATA_EXPECTED_PACKET = " + repr(REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_EXPECTED_PACKET"]),
        "REQUIRED_CONFDATA_HELPER_ANCHORS = " + repr(REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_HELPER_ANCHORS"]),
    ]
    write_text(root, CHECKER_PATH, "\n\n".join(checker_lines) + "\n")

    confdata_cases = []
    for name, input_name, expected_name in zip(
        REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_CASES"],
        REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_INPUT_PACKET"],
        REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_EXPECTED_PACKET"],
        strict=True,
    ):
        confdata_cases.append({"name": name, "input": input_name, "expected": expected_name})
        write_text(root, FIXTURE_DIR / input_name, "CONFIG_ALPHA=y\n")
        write_text(root, FIXTURE_DIR / expected_name, '{"counts":{"set":1,"unset":0},"entries":[{"name":"CONFIG_ALPHA","kind":"tristate","value":"y"}]}\n')

    write_text(root, CASES_PATH, json.dumps({"confdata_cases": confdata_cases}, indent=2) + "\n")
    write_text(
        root,
        MANIFEST_PATH,
        json.dumps(
            {
                "cases": REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_CASES"],
                "case_count": len(REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_CASES"]),
                "input_packet": REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_INPUT_PACKET"],
                "expected_packet": REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_EXPECTED_PACKET"],
                "helper_local_anchors": REQUIRED_CONFDATA_CHECKER_LISTS["REQUIRED_CONFDATA_HELPER_ANCHORS"],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r} in {exc!s}") from exc
        return
    raise AssertionError(f"expected validation failure containing {expected_fragment!r}")


def run_self_test() -> int:
    cases = 0
    temp_dir = Path(tempfile.mkdtemp(prefix="zigux_kconfig_symbol_export_parity_"))
    try:
        good = temp_dir / "good"
        build_fixture_root(good)
        validate(good)
        cases += 1

        missing_export = temp_dir / "missing_export"
        shutil.copytree(good, missing_export)
        write_text(
            missing_export,
            CONFDATA_BRIDGE_PATH,
            read_text(missing_export, CONFDATA_BRIDGE_PATH).replace(
                "pub fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {",
                "fn runConfdataBridge(allocator: std.mem.Allocator, input: []const u8, writer: anytype) !void {",
                1,
            ),
        )
        expect_failure(missing_export, "missing required confdata export snippet")
        cases += 1

        broken_entry_kind = temp_dir / "broken_entry_kind"
        shutil.copytree(good, broken_entry_kind)
        write_text(
            broken_entry_kind,
            CONFDATA_BRIDGE_PATH,
            read_text(broken_entry_kind, CONFDATA_BRIDGE_PATH).replace("    unset,", "    flag,", 1),
        )
        expect_failure(broken_entry_kind, "EntryKind export order drifted")
        cases += 1

        broken_checker_list = temp_dir / "broken_checker_list"
        shutil.copytree(good, broken_checker_list)
        write_text(
            broken_checker_list,
            CHECKER_PATH,
            read_text(broken_checker_list, CHECKER_PATH).replace(
                "'duplicate_assignments'",
                "'duplicate_assignment_typo'",
                1,
            ),
        )
        expect_failure(broken_checker_list, "shared kconfig checker list drifted")
        cases += 1

        broken_manifest = temp_dir / "broken_manifest"
        shutil.copytree(good, broken_manifest)
        manifest = load_json(broken_manifest, MANIFEST_PATH)
        manifest["expected_packet"] = manifest["expected_packet"][:-1]
        write_text(broken_manifest, MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(broken_manifest, "confdata manifest expected_packet drifted")
        cases += 1

        broken_anchor = temp_dir / "broken_anchor"
        shutil.copytree(good, broken_anchor)
        write_text(
            broken_anchor,
            CONFDATA_BRIDGE_PATH,
            read_text(broken_anchor, CONFDATA_BRIDGE_PATH).replace(
                'test "confdata bridge preserves duplicate unset ownership on allocation failure" {',
                'test "confdata bridge preserves duplicate unset ownership after drift" {',
                1,
            ),
        )
        expect_failure(broken_anchor, "confdata bridge test anchors drifted")
        cases += 1

        missing_fixture = temp_dir / "missing_fixture"
        shutil.copytree(good, missing_fixture)
        (missing_fixture / FIXTURE_DIR / "explicit_empty_assignments_expected.json").unlink()
        expect_failure(missing_fixture, "missing required kconfig fixture artifact")
        cases += 1
    finally:
        shutil.rmtree(temp_dir)

    if cases != EXPECTED_SELF_TEST_CASE_COUNT:
        print("KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST=fail")
        print(f"KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST_CASE_COUNT_ACTUAL={cases}")
        print(f"KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST_CASE_COUNT_EXPECTED={EXPECTED_SELF_TEST_CASE_COUNT}")
        return 1

    print("KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST=pass")
    print(f"KCONFIG_SYMBOL_EXPORT_PARITY_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Kconfig confdata symbol-export parity packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root to validate (defaults to current working directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run checker fixture self-tests",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    validate(args.root)
    print("KCONFIG_SYMBOL_EXPORT_PARITY=pass")
    print(f"KCONFIG_SYMBOL_EXPORT_PARITY_CASE_COUNT={len(REQUIRED_CONFDATA_CHECKER_LISTS['REQUIRED_CONFDATA_CASES'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
