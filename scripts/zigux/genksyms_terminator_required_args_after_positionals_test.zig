const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRenderedArgs(expected: []const []const u8, actual: []const []const u8) !void {
    try testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_arg, actual_arg| {
        try testing.expectEqualStrings(expected_arg, actual_arg);
    }
}

test "required option lookalikes after terminator remain argv data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "delayed.c",
        "-d",
        "--",
        "-r",
        "after.symref",
        "--reference",
        "also-after.symref",
        "-T",
        "after.symtypes",
        "--dump-types=inline-after.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "-d",
        "--",
        "delayed.c",
        "-r",
        "after.symref",
        "--reference",
        "also-after.symref",
        "-T",
        "after.symtypes",
        "--dump-types=inline-after.symtypes",
    };

    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| {
                try testing.expectEqual(@as(usize, 1), request.version_count);
                try testing.expectEqual(@as(usize, 1), request.debug_level);
                try testing.expectEqual(@as(usize, 0), request.reference_files.len);
                try testing.expect(request.dump_types_file == null);
                try expectRenderedArgs(&expected_rendered, request.rendered_args);
            },
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    }
}

test "bridge renders post terminator required options as argv only" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "source.c",
        "--debug",
        "--",
        "--ref=after.symref",
        "--reference=after-two.symref",
        "-rinline-after.symref",
        "--dump-t=after.symtypes",
        "-Tinline-after.symtypes",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--debug\",\"--\",\"source.c\",\"--ref=after.symref\",\"--reference=after-two.symref\",\"-rinline-after.symref\",\"--dump-t=after.symtypes\",\"-Tinline-after.symtypes\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
