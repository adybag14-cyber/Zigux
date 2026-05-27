#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELP_ZIG = ROOT / "tools" / "lib" / "subcmd" / "help.zig"
FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "subcmd_help"
CASES_FIXTURE = FIXTURE_DIR / "cases.json"
WRAPPER_PATH = ROOT / ".subcmd_help_fixture_runner.zig"

REQUIRED_HELPER_ANCHORS = (
    "buildOtherCommandSearchPlan keeps PATH ordering while marking empty and exec-path entries",
    "buildOtherCommandSearchPlan preserves duplicate and relative scan targets when they are not the exec path",
    "renderCommandSections keeps stable headers for main and fallback command groups",
    "renderCommandSections emits the fallback-only packet without a blank main header",
    "renderCommandSections keeps an empty exec path unquoted while sharing longest width with fallback commands",
)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    found = shutil.which("zig")
    if found:
        return found
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def ordered_test_anchors(path: Path) -> list[str]:
    anchors: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith('test "') and line.endswith('" {'):
            anchors.append(line[len('test "') : -len('" {')])
    if not anchors:
        raise SystemExit("no Zig test anchors found in tools/lib/subcmd/help.zig")
    return anchors


def read_cases() -> list[dict[str, str]]:
    payload = json.loads(CASES_FIXTURE.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("subcmd help fixture cases must be a JSON list")

    cases: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise SystemExit("each subcmd help fixture case must be an object")
        name = item.get("name")
        expected = item.get("expected_file")
        output_kind = item.get("output_kind")
        if not isinstance(name, str) or not isinstance(expected, str) or not isinstance(output_kind, str):
            raise SystemExit("subcmd help fixture case fields must be strings")
        cases.append(
            {
                "name": name,
                "expected_file": expected,
                "output_kind": output_kind,
            }
        )
    return cases


def write_wrapper(path: Path) -> None:
    path.write_text(
        """const std = @import(\"std\");
const Io = std.Io;
const help = @import(\"tools/lib/subcmd/help.zig\");

const SearchPlanPacket = struct {
    entries: []SearchPlanEntryPacket,
    scannable_count: usize,
};

const SearchPlanEntryPacket = struct {
    path: []const u8,
    disposition: []const u8,
};

fn dispositionName(value: help.SearchPathEntryDisposition) []const u8 {
    return switch (value) {
        .scan => \"scan\",
        .skip_exec_path => \"skip_exec_path\",
        .skip_empty => \"skip_empty\",
    };
}

fn emitSearchPlan(io: Io) !void {
    const allocator = std.heap.page_allocator;
    const plan = try help.buildOtherCommandSearchPlan(
        allocator,
        \":/usr/libexec/perf-core:/bin::/usr/bin:\",
        \"/usr/libexec/perf-core\",
    );
    defer help.freeOtherCommandSearchPlan(allocator, plan);

    var entries = try allocator.alloc(SearchPlanEntryPacket, plan.len);
    defer allocator.free(entries);

    for (plan, 0..) |entry, index| {
        entries[index] = .{
            .path = entry.path,
            .disposition = dispositionName(entry.disposition),
        };
    }

    const packet = SearchPlanPacket{
        .entries = entries,
        .scannable_count = help.countScannableSearchPathEntries(plan),
    };

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;
    try std.json.Stringify.value(packet, .{ .whitespace = .indent_2 }, stdout);
    try stdout.writeByte('\\n');
    try stdout.flush();
}

fn emitMainAndOtherSections(io: Io) !void {
    const allocator = std.heap.page_allocator;

    var main_cmds = help.CommandNames.init(allocator);
    defer main_cmds.deinit();
    try main_cmds.add(\"annotate\");
    try main_cmds.add(\"bench\");

    var other_cmds = help.CommandNames.init(allocator);
    defer other_cmds.deinit();
    try other_cmds.add(\"report\");

    const rendered = try help.renderCommandSections(
        allocator,
        \"subcommands\",
        \"/usr/libexec/perf-core\",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer allocator.free(rendered);

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;
    try stdout.writeAll(rendered);
    try stdout.flush();
}

fn emitFallbackOnlySections(io: Io) !void {
    const allocator = std.heap.page_allocator;

    var main_cmds = help.CommandNames.init(allocator);
    defer main_cmds.deinit();

    var other_cmds = help.CommandNames.init(allocator);
    defer other_cmds.deinit();
    try other_cmds.add(\"report\");
    try other_cmds.add(\"script\");

    const rendered = try help.renderCommandSections(
        allocator,
        \"subcommands\",
        \"/usr/libexec/perf-core\",
        &main_cmds,
        &other_cmds,
        80,
    );
    defer allocator.free(rendered);

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;
    try stdout.writeAll(rendered);
    try stdout.flush();
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const case_name = if (args.len >= 2) args[1] else return error.MissingCaseName;
    if (args.len != 2) {
        return error.UnexpectedArguments;
    }

    if (std.mem.eql(u8, case_name, \"search_plan\")) {
        try emitSearchPlan(io);
        return;
    }
    if (std.mem.eql(u8, case_name, \"main_and_other_sections\")) {
        try emitMainAndOtherSections(io);
        return;
    }
    if (std.mem.eql(u8, case_name, \"fallback_only_sections\")) {
        try emitFallbackOnlySections(io);
        return;
    }

    return error.UnknownCaseName;
}
""",
        encoding="utf-8",
    )


def normalize_expected(kind: str, text: str):
    if kind == "json":
        return json.loads(text)
    if kind == "text":
        return text
    raise SystemExit(f"unsupported output_kind: {kind}")


def normalize_actual(kind: str, text: str):
    if kind == "json":
        return json.loads(text)
    if kind == "text":
        return text
    raise SystemExit(f"unsupported output_kind: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 8 subcmd help behavior fixtures.")
    parser.add_argument("--zig", help="Path to zig executable")
    args = parser.parse_args()

    missing_files = [path for path in (HELP_ZIG, CASES_FIXTURE) if not path.exists()]
    if missing_files:
        raise SystemExit("missing required files: " + ", ".join(str(path) for path in missing_files))

    anchors = ordered_test_anchors(HELP_ZIG)
    missing_anchors = [anchor for anchor in REQUIRED_HELPER_ANCHORS if anchor not in anchors]
    if missing_anchors:
        raise SystemExit("missing required help.zig test anchors: " + ", ".join(missing_anchors))

    zig = find_zig(args.zig)
    run([zig, "test", str(HELP_ZIG)], cwd=str(ROOT))

    cases = read_cases()
    write_wrapper(WRAPPER_PATH)
    try:
        for case in cases:
            expected_path = FIXTURE_DIR / case["expected_file"]
            if not expected_path.exists():
                raise SystemExit(f"missing expected fixture: {expected_path}")

            expected_text = expected_path.read_text(encoding="utf-8")
            expected = normalize_expected(case["output_kind"], expected_text)
            completed = subprocess.run(
                [zig, "run", str(WRAPPER_PATH), "--", case["name"]],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                raise SystemExit(
                    f"fixture runner failed for {case['name']}: "
                    + (completed.stderr.strip() or f"exit status {completed.returncode}")
                )
            actual = normalize_actual(case["output_kind"], completed.stdout)
            if actual != expected:
                raise SystemExit(
                    f"fixture mismatch for {case['name']}: expected {case['expected_file']}"
                )
    finally:
        WRAPPER_PATH.unlink(missing_ok=True)

    print(
        "subcmd help verification passed: "
        + ", ".join(case["name"] for case in cases)
        + ", plus zig test tools/lib/subcmd/help.zig"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
