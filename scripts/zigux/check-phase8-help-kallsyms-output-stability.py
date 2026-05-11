#!/usr/bin/env python3
"""Check bounded Phase 8 help and kallsyms output-stability markers.

This checker stays narrowly focused on the parked Phase 8 tooling packet:

- help section rendering should suppress empty sections while keeping the
  stable main and PATH headings explicit when content exists.
- kallsyms parse wrappers should preserve the callback stop-code contract
  instead of swallowing it inside the Zig wrapper layer.
"""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import sys
import tempfile


@dataclasses.dataclass(frozen=True)
class CheckResult:
    path: pathlib.Path
    missing: tuple[str, ...]


HELP_MARKERS = (
    "pub fn writeCommandSectionsForTerminal(",
    'if (main_cmds.count() != 0) {',
    """try writer.print(\"available {s} in '{s}'\\n\", .{ title, exec_path });""",
    'if (other_cmds.count() != 0) {',
    """try writer.print(\"{s} available from elsewhere on your $PATH\\n\", .{title});""",
)

KALLSYMS_MARKERS = (
    "pub fn kallsymsParseFile(",
    "error.StopParsing => return callback_state.result,",
    "pub fn kallsymsParse(",
    "return kallsymsParseFile(allocator, io, file, &scratch_buffer, context, process_symbol);",
)


def read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def check_markers(path: pathlib.Path, markers: tuple[str, ...]) -> CheckResult | None:
    text = read_text(path)
    missing = tuple(marker for marker in markers if marker not in text)
    if not missing:
        return None
    return CheckResult(path=path, missing=missing)


def run_checks(repo_root: pathlib.Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    help_path = repo_root / "tools/lib/subcmd/help.zig"
    help_result = check_markers(help_path, HELP_MARKERS)
    if help_result is not None:
        results.append(help_result)

    kallsyms_path = repo_root / "tools/lib/symbol/kallsyms.zig"
    kallsyms_result = check_markers(kallsyms_path, KALLSYMS_MARKERS)
    if kallsyms_result is not None:
        results.append(kallsyms_result)

    return results


def write_fixture_tree(repo_root: pathlib.Path, *, break_help: bool = False) -> None:
    help_path = repo_root / "tools/lib/subcmd"
    help_path.mkdir(parents=True, exist_ok=True)
    help_text = """
pub fn writeCommandSectionsForTerminal(
    writer: anytype,
    title: []const u8,
    exec_path: []const u8,
    main_cmds: CmdNames,
    other_cmds: CmdNames,
    env_lines: ?[]const u8,
    env_columns: ?[]const u8,
    fallback: ?TerminalDimensions,
) !void {
    _ = env_lines;
    _ = env_columns;
    _ = fallback;
    if (main_cmds.count() != 0) {
        try writer.print("available {s} in '{s}'\\n", .{ title, exec_path });
    }
    if (other_cmds.count() != 0) {
        try writer.print("{s} available from elsewhere on your $PATH\\n", .{title});
    }
}
""".strip()
    if break_help:
        help_text = help_text.replace("if (other_cmds.count() != 0) {", "if (other_cmds.count() == 0) {")
    (help_path / "help.zig").write_text(help_text + "\n", encoding="utf-8")

    kallsyms_path = repo_root / "tools/lib/symbol"
    kallsyms_path.mkdir(parents=True, exist_ok=True)
    (kallsyms_path / "kallsyms.zig").write_text(
        """
pub fn kallsymsParseFile(
    allocator: std.mem.Allocator,
    io: std.Io,
    file: std.fs.File,
    scratch_buffer: []u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    _ = allocator;
    _ = io;
    _ = file;
    _ = scratch_buffer;
    _ = context;
    _ = process_symbol;
    return error.StopParsing => return callback_state.result,;
}

pub fn kallsymsParse(
    allocator: std.mem.Allocator,
    io: std.Io,
    dir: std.Io.Dir,
    sub_path: []const u8,
    context: ?*anyopaque,
    process_symbol: ProcessSymbolFn,
) !i32 {
    _ = dir;
    _ = sub_path;
    return kallsymsParseFile(allocator, io, file, &scratch_buffer, context, process_symbol);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        write_fixture_tree(root)
        assert not run_checks(root)

        broken_root = root / "broken"
        write_fixture_tree(broken_root, break_help=True)
        broken_results = run_checks(broken_root)
        assert len(broken_results) == 1
        assert broken_results[0].path.as_posix().endswith("tools/lib/subcmd/help.zig")
        assert "if (other_cmds.count() != 0) {" in broken_results[0].missing
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check Phase 8 help and kallsyms output-stability markers."
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
        help="repository root to inspect (default: parent of scripts/zigux)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run a fixture-backed self-test instead of inspecting a repo checkout",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    results = run_checks(args.repo_root)
    if not results:
        print("phase8 help and kallsyms output-stability markers: ok")
        return 0

    for result in results:
        print(f"{result.path}: missing expected markers:", file=sys.stderr)
        for marker in result.missing:
            print(f"  - {marker}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
