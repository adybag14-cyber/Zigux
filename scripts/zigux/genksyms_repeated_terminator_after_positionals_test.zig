const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

fn expectRequest(allocator: std.mem.Allocator, args: []const []const u8) !genksyms.Request {
    const outcome = try genksyms.parseArgs(allocator, args);
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.UnexpectedParseFailure,
    };
}

test "repeated terminator after positionals freezes the remaining argv" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "-Vd",
        "leftover.c",
        "--",
        "--",
        "--reference",
        "late.symref",
        "-Tlate.types",
        "--version",
        "rightover.h",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);
    try testing.expectEqual(@as(usize, args.len), request.raw_args.len);
    try testing.expectEqualSlices([]const u8, &args, request.raw_args);

    const expected_rendered = [_][]const u8{
        "-Vd",
        "leftover.c",
        "--",
        "--",
        "--reference",
        "late.symref",
        "-Tlate.types",
        "--version",
        "rightover.h",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "repeated terminator tail does not become request state" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "first.c",
        "--",
        "--",
        "-d",
        "--dump",
        "-p",
        "-w",
        "-r",
        "tail.symref",
        "--dump-types",
        "tail.types",
    };
    const request = try expectRequest(arena_state.allocator(), &args);

    try testing.expectEqual(@as(usize, 0), request.version_count);
    try testing.expectEqual(@as(usize, 0), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 0), request.reference_files.len);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered = [_][]const u8{
        "first.c",
        "--",
        "--",
        "-d",
        "--dump",
        "-p",
        "-w",
        "-r",
        "tail.symref",
        "--dump-types",
        "tail.types",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}

test "bridge output preserves repeated terminator data order" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--version",
        "unit.c",
        "--",
        "--",
        "--debug",
        "-VV",
    };
    const request = try genksyms.parseArgs(arena_state.allocator(), &args);
    const parsed_request = switch (request) {
        .command => |command| switch (command) {
            .request => |value| value,
            else => return error.ExpectedRequestCommand,
        },
        .failure => return error.UnexpectedParseFailure,
    };

    try testing.expectEqual(@as(usize, 1), parsed_request.version_count);
    try testing.expectEqual(@as(usize, 0), parsed_request.debug_level);
    try testing.expectEqual(@as(usize, 0), parsed_request.reference_files.len);
    try testing.expect(parsed_request.dump_types_file == null);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, parsed_request);
    try testing.expectEqualStrings(
        "{\"tool\":\"scripts/genksyms/genksyms\",\"stdin\":\"cpp-stream\",\"stdout\":\"symversions\",\"argv\":[\"scripts/genksyms/genksyms\",\"--version\",\"unit.c\",\"--\",\"--\",\"--debug\",\"-VV\"],\"options\":{\"debug_level\":0,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n",
        output.written(),
    );
}
