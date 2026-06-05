const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

fn expectRepeatedDumpTypesRequest(
    allocator: std.mem.Allocator,
    args: []const []const u8,
    expected_dump_types_file: []const u8,
    expected_rendered_args: []const []const u8,
    expected_version_count: usize,
) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(expected_version_count, request.version_count);
    try testing.expectEqualStrings(expected_dump_types_file, request.dump_types_file.?);
    try testing.expectEqualSlices([]const u8, expected_rendered_args, request.rendered_args);
    try testing.expectEqualSlices([]const u8, args, request.raw_args);

    return request;
}

test "long dump-types after delayed positionals keeps the last value" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "leftover.c",
        "--dump-types=first.symtypes",
        "rightover.h",
        "--dump-types",
        "last.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--dump-types=first.symtypes",
        "--dump-types",
        "last.symtypes",
        "leftover.c",
        "rightover.h",
    };

    const request = try expectRepeatedDumpTypesRequest(
        arena_state.allocator(),
        &args,
        "last.symtypes",
        &expected_rendered,
        0,
    );

    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
}

test "mixed short and abbreviated dump-types after positionals preserves normalized order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "before.sym",
        "-Tfirst.symtypes",
        "--dump-t",
        "middle.symtypes",
        "after.sym",
        "-T",
        "final.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "-Tfirst.symtypes",
        "--dump-t",
        "middle.symtypes",
        "-T",
        "final.symtypes",
        "before.sym",
        "after.sym",
    };

    const request = try expectRepeatedDumpTypesRequest(
        arena_state.allocator(),
        &args,
        "final.symtypes",
        &expected_rendered,
        0,
    );

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"-Tfirst.symtypes\",\"--dump-t\",\"middle.symtypes\",\"-T\",\"final.symtypes\",\"before.sym\",\"after.sym\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":\"final.symtypes\"}}\n",
        output.written(),
    );
}

test "dump-types overrides after positionals coexist with version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "input.c",
        "--version",
        "--dump-types",
        "first.symtypes",
        "-VV",
        "-Tsecond.symtypes",
    };
    const expected_rendered = [_][]const u8{
        "--version",
        "--dump-types",
        "first.symtypes",
        "-VV",
        "-Tsecond.symtypes",
        "input.c",
    };

    const request = try expectRepeatedDumpTypesRequest(
        arena_state.allocator(),
        &args,
        "second.symtypes",
        &expected_rendered,
        3,
    );

    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
}
