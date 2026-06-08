const std = @import("std");
const testing = std.testing;

const stage_helper_source = @embedFile("stage-pinned-zig-archive.py");

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, stage_helper_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, stage_helper_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, stage_helper_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "Lane 18 stage helper keeps source input mutually exclusive with parts input" {
    try expectContains("def resolve_source_archive(");
    try expectContains("if (source is None) == (parts_dir is None):");
    try expectContains("raise ValueError(\"exactly one of source or parts_dir must be provided\")");
    try expectContains("return source, \"source\", None");
    try expectBefore("if source is not None:", "assert parts_dir is not None");
}

test "Lane 18 source check-only path validates without staging bytes" {
    try expectContains("def stage_archive(");
    try expectContains("check_only: bool");
    try expectContains("if check_only:");
    try expectContains("\"checked\"");
    try expectBefore("if check_only:", "copy_file(resolved_source, destination)");
}

test "Lane 18 CLI exposes source and check-only action path status" {
    try expectContains("parser.add_argument(\"--source\"");
    try expectContains("parser.add_argument(\"--parts-dir\"");
    try expectContains("parser.add_argument(\"--check-only\"");
    try expectContains("STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE");
    try expectContains("STAGE_PINNED_ZIG_ARCHIVE_STATUS");
}
