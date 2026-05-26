#!/usr/bin/env python3
"""Guard the Phase 1 cmdline shared-replay packet against helper and smoke drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
HELPER_REL = Path("tools/lib/cmdline.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")

EXPECTED_SOURCE_SYMBOLS = [
    "pub fn parseOptionStr(optionstr: []const u8, option: []const u8) bool {",
    "pub const parse_option_str = parseOptionStr;",
    "pub fn nextArg(args: []const u8) ?NextArgResult {",
    "pub const next_arg = nextArg;",
    "pub fn memparse(text: []const u8) MemparseResult {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
    'test "memparse handles decimal hexadecimal octal and suffixes" {',
    'test "memparse reports no-conversion via unchanged rest" {',
    'test "memparse keeps original rest when sign is not followed by digits" {',
    'test "memparse saturates signed overflow instead of trapping" {',
    'test "memparse applies suffixes before signed clamping" {',
    'test "memparse keeps signed non-decimal prefixes aligned with suffix handling" {',
    'test "parseOptionStr matches only exact bare options" {',
    'test "nextArg returns null for blank input" {',
    'test "nextArg parses bare parameters and keeps the remaining text" {',
    'test "nextArg parses key value pairs and quoted values" {',
    'test "nextArg handles a quoted full token that contains a key value pair" {',
    'test "nextArg keeps empty and unterminated quoted values aligned" {',
]

EXPECTED_SMOKE_MARKERS = [
    'try std.testing.expect(@hasDecl(cmdline, "memparse"));',
    'const parsed = cmdline.memparse("64K tail");',
    'const signed = cmdline.memparse("-2K tail");',
    'const saturated = cmdline.memparse("+9223372036854775808");',
    'try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));',
    'try std.testing.expect(cmdline.parseOptionStr(",quiet", ""));',
    'try std.testing.expect(cmdline.parseOptionStr("rootwait,,quiet", ""));',
    'try std.testing.expect(!cmdline.parseOptionStr("quiet,", ""));',
    'try std.testing.expect(!cmdline.parseOptionStr("rootwait,quiet", "debug"));',
    'const keyed = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1") orelse return error.TestUnexpectedResult;',
    'const quoted_pair = cmdline.nextArg(keyed.remaining) orelse return error.TestUnexpectedResult;',
    'const quoted = cmdline.nextArg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;',
    'const unterminated = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;',
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (HELPER_REL, SMOKE_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, HELPER_REL)
    smoke_text = load_text(root, SMOKE_REL)

    for symbol in EXPECTED_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    for marker in EXPECTED_SMOKE_MARKERS:
        failures.extend(require_exact_occurrence(smoke_text, f"smoke_marker:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, HELPER_REL, "\n".join(EXPECTED_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS) + "\n")
    write_text(root, SMOKE_REL, "\n".join(EXPECTED_SMOKE_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        ("missing_helper", "missing_file:tools/lib/cmdline.zig"),
        (
            "missing_symbol",
            "helper_symbol:pub const next_arg = nextArg;:expected=1:actual=0",
        ),
        (
            "missing_anchor",
            'helper_anchor:test "memparse keeps signed non-decimal prefixes aligned with suffix handling" {:expected=1:actual=0',
        ),
        (
            "duplicate_anchor",
            'helper_anchor:test "nextArg keeps empty and unterminated quoted values aligned" {:expected=1:actual=2',
        ),
        (
            "missing_smoke",
            "missing_file:zigux/tests/phase1_host_tools_smoke.zig",
        ),
        (
            "missing_smoke_marker",
            'smoke_marker:const saturated = cmdline.memparse("+9223372036854775808");:expected=1:actual=0',
        ),
        (
            "duplicate_smoke_marker",
            'smoke_marker:try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));:expected=1:actual=2',
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_cmdline_replay_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:missing_helper")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:baseline")

        helper_path = tmp_root / HELPER_REL
        smoke_path = tmp_root / SMOKE_REL

        text = helper_path.read_text(encoding="utf-8").replace("pub const next_arg = nextArg;\n", "", 1)
        helper_path.write_text(text, encoding="utf-8")
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:missing_symbol")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "memparse keeps signed non-decimal prefixes aligned with suffix handling" {\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:missing_anchor")

        build_sample_repo(tmp_root)
        duplicated_anchor = 'test "nextArg keeps empty and unterminated quoted values aligned" {'
        text = helper_path.read_text(encoding="utf-8").replace(
            duplicated_anchor + "\n",
            duplicated_anchor + "\n" + duplicated_anchor + "\n",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:duplicate_anchor")

        build_sample_repo(tmp_root)
        smoke_path.unlink()
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:missing_smoke")

        build_sampleRepo = build_sample_repo
        build_sampleRepo(tmp_root)
        text = smoke_path.read_text(encoding="utf-8").replace(
            'const saturated = cmdline.memparse("+9223372036854775808");\n',
            "",
            1,
        )
        smoke_path.write_text(text, encoding="utf-8")
        if cases[5][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:missing_smoke_marker")

        build_sample_repo(tmp_root)
        duplicated_marker = 'try std.testing.expect(cmdline.parseOptionStr("rootwait,quiet", "quiet"));'
        text = smoke_path.read_text(encoding="utf-8").replace(
            duplicated_marker + "\n",
            duplicated_marker + "\n" + duplicated_marker + "\n",
            1,
        )
        smoke_path.write_text(text, encoding="utf-8")
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-cmdline-shared-replay:self-test:duplicate_smoke_marker")

    print("PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_CMDLINE_SHARED_REPLAY_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CMDLINE_SHARED_REPLAY_PACKET=pass")
    print(f"PHASE1_CMDLINE_SHARED_REPLAY_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_CMDLINE_SHARED_REPLAY_PACKET_SMOKE={SMOKE_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())