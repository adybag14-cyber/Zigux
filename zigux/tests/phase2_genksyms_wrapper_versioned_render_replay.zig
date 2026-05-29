const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

fn expectVersionedRender(
    args: []const []const u8,
    expected_version_count: usize,
    expected_json: []const u8,
) !void {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const outcome = try genksyms.parseArgs(arena_state.allocator(), args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(expected_version_count, request.version_count);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(expected_json, output.written());
}

test "phase2 genksyms wrapper keeps version side effect out of bridge options" {
    try expectVersionedRender(
        &.{
            "--version",
            "--reference",
            "base.symref",
            "-T",
            "types.symtypes",
        },
        1,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"--reference\",\"base.symref\",\"-T\",\"types.symtypes\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"base.symref\"],\"dump_types_file\":\"types.symtypes\"}}\n",
    );
}

test "phase2 genksyms wrapper renders normalized argv after versioned positional request" {
    try expectVersionedRender(
        &.{
            "leftover.c",
            "-VVd",
            "--reference=base.symref",
            "rightover.h",
        },
        2,
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-VVd\",\"--reference=base.symref\",\"leftover.c\",\"rightover.h\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[\"base.symref\"],\"dump_types_file\":null}}\n",
    );
}
