#!/usr/bin/env python3
"""Guard the Phase 1 cmdline review packet against helper, fixture, and shared-smoke drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/cmdline.zig")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_SOURCE_SYMBOLS = [
    "pub const MemparseResult = struct {",
    "pub const NextArgResult = struct {",
    "pub fn parseOptionStr(optionstr: []const u8, option: []const u8) bool {",
    "pub const parse_option_str = parseOptionStr;",
    "pub fn nextArg(args: []const u8) ?NextArgResult {",
    "pub const next_arg = nextArg;",
    "pub fn memparse(text: []const u8) MemparseResult {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse reports no-conversion via unchanged rest"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse applies suffixes before signed clamping"',
    'test "memparse keeps signed non-decimal prefixes aligned with suffix handling"',
    'test "parseOptionStr matches only exact bare options"',
    'test "nextArg returns null for blank input"',
    'test "nextArg parses bare parameters and keeps the remaining text"',
    'test "nextArg parses key value pairs and quoted values"',
    'test "nextArg handles a quoted full token that contains a key value pair"',
    'test "nextArg keeps empty and unterminated quoted values aligned"',
]

EXPECTED_FIXTURE_VALUES = {
    "decimal_k": {"value": 65536, "rest": " rest"},
    "hex_m": {"value": 33554432, "rest": ""},
    "octal_k": {"value": 8192, "rest": ""},
    "invalid": {"value": 0, "rest": "xyz"},
}

EXPECTED_SMOKE_MARKERS = [
    'const parsed = cmdline.memparse("64K tail");',
    'const signed = cmdline.memparse("-2K tail");',
    'const saturated = cmdline.memparse("+9223372036854775808");',
    'try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));',
    'try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));',
    'const keyed = cmdline.nextArg("console=ttyS0,115200 root=\\"/dev/sda1 quiet\\" panic=-1") orelse return error.TestUnexpectedResult;',
    'const quoted = cmdline.nextArg("\\"mode=fast path\\" tail") orelse return error.TestUnexpectedResult;',
    'const unterminated = cmdline.nextArg("mode=\\"fast boot") orelse return error.TestUnexpectedResult;',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> Any:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> Any:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: Any, expected: Any) -> list[str]:
    return [] if actual == expected else [f"{label}:expected_current_packet"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (HELPER_REL, FIXTURE_REL, SMOKE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    smoke_text = load_text(root, SMOKE_REL)
    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("fixture", exc)]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)
    if duplicate_fixture_paths:
        return [f"fixture:duplicate_json_key:{path}" for path in duplicate_fixture_paths]

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"cmdline_symbol:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"cmdline_anchor:{anchor}", anchor))

    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"cmdline_smoke:{marker}", marker))

    cmdline_fixture = fixture.get("cmdline")
    if not isinstance(cmdline_fixture, dict):
        return ["fixture:cmdline"]

    for key, expected in EXPECTED_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"fixture:{key}", cmdline_fixture.get(key), expected))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPER_REL, "\n".join(EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS) + "\n")
    write_text(root, FIXTURE_REL, json.dumps({"cmdline": EXPECTED_FIXTURE_VALUES}, indent=2) + "\n")
    write_text(root, SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        ("missing_helper", "missing_file:tools/lib/cmdline.zig"),
        ("missing_symbol", "cmdline_symbol:pub fn memparse(text: []const u8) MemparseResult {:expected=1:actual=0"),
        ("missing_anchor", 'cmdline_anchor:test "nextArg parses key value pairs and quoted values":expected=1:actual=0'),
        ("missing_smoke", 'cmdline_smoke:const keyed = cmdline.nextArg("console=ttyS0,115200 root=\\"/dev/sda1 quiet\\" panic=-1") orelse return error.TestUnexpectedResult;:expected=1:actual=0'),
        ("fixture_drift", "fixture:decimal_k:expected_current_packet"),
        ("fixture_invalid_json", "fixture:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1"),
        ("fixture_duplicate_key", "fixture:duplicate_json_key:cmdline.decimal_k"),
        ("duplicate_smoke", 'cmdline_smoke:try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));:expected=1:actual=2'),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_cmdline_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:missing_helper")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:baseline")

        helper_text = load_text(tmp_root, HELPER_REL).replace("pub fn memparse(text: []const u8) MemparseResult {\n", "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:missing_symbol")

        build_sample_repo(tmp_root)
        helper_text = load_text(tmp_root, HELPER_REL).replace('test "nextArg parses key value pairs and quoted values"\n', "", 1)
        write_text(tmp_root, HELPER_REL, helper_text)
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:missing_anchor")

        build_sample_repo(tmp_root)
        smoke_text = load_text(tmp_root, SMOKE_REL).replace(EXPECTED_SMOKE_MARKERS[5] + "\n", "", 1)
        write_text(tmp_root, SMOKE_REL, smoke_text)
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:missing_smoke")

        build_sample_repo(tmp_root)
        fixture = load_json(tmp_root, FIXTURE_REL)
        fixture["cmdline"]["decimal_k"] = {"value": 1, "rest": " rest"}
        write_text(tmp_root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        write_text(tmp_root, FIXTURE_REL, "{\n")
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:fixture_invalid_json")

        build_sample_repo(tmp_root)
        fixture_text = load_text(tmp_root, FIXTURE_REL).replace(
            '    "decimal_k": {\n',
            '    "decimal_k": {"value": 1, "rest": " rest"},\n    "decimal_k": {\n',
            1,
        )
        write_text(tmp_root, FIXTURE_REL, fixture_text)
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:fixture_duplicate_key")

        build_sample_repo(tmp_root)
        smoke_text = load_text(tmp_root, SMOKE_REL)
        duplicated = EXPECTED_SMOKE_MARKERS[3]
        smoke_text = smoke_text.replace(duplicated + "\n", duplicated + "\n" + duplicated + "\n", 1)
        write_text(tmp_root, SMOKE_REL, smoke_text)
        if cases[7][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-review:self-test:duplicate_smoke")

    print("PHASE1_CMDLINE_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CMDLINE_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CMDLINE_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("phase1-cmdline-review-packet:ok")
    print(f"PHASE1_CMDLINE_REVIEW_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_CMDLINE_REVIEW_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_CMDLINE_REVIEW_PACKET_SMOKE={SMOKE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
