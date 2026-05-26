const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;

const BridgePayload = struct {
    tool: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    argv: []const []const u8,
    options: struct {
        debug_level: usize,
        warnings: bool,
        dump_defs: bool,
        preserve: bool,
        reference_files: []const []const u8,
        dump_types_file: ?[]const u8,
    },
};

fn expectStringSliceEqual(expected: []const []const u8, actual: []const []const u8) !void {
    try testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_item, actual_item| {
        try testing.expectEqualStrings(expected_item, actual_item);
    }
}

test "phase 2 genksyms wrapper repeated abbreviated positional passthrough keeps version side effects" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "leftover.c",
        "-d",
        "rightover.h",
        "-r",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 2), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered_args = [_][]const u8{
        "--ver",
        "--ver",
        "-d",
        "-r",
        "foo.symref",
        "leftover.c",
        "rightover.h",
    };
    try expectStringSliceEqual(&expected_rendered_args, request.rendered_args);
}

test "phase 2 genksyms wrapper repeated abbreviated positional passthrough renders normalized plan" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
        "--ver",
        "--ver",
        "leftover.c",
        "-d",
        "rightover.h",
        "-r",
        "foo.symref",
    };
    const outcome = try genksyms.parseArgs(arena_state.allocator(), &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    var rendered: std.Io.Writer.Allocating = .init(testing.allocator);
    defer rendered.deinit();
    try genksyms.renderGenksymsBridge(&rendered.writer, request);

    const actual = try std.json.parseFromSlice(BridgePayload, testing.allocator, rendered.written(), .{});
    defer actual.deinit();

    try testing.expectEqualStrings("scripts/genksyms/genksyms", actual.value.tool);
    try testing.expectEqualStrings("cpp-stream", actual.value.stdin);
    try testing.expectEqualStrings("symversions", actual.value.stdout);

    const expected_argv = [_][]const u8{
        "scripts/genksyms/genksyms",
        "--ver",
        "--ver",
        "-d",
        "-r",
        "foo.symref",
        "leftover.c",
        "rightover.h",
    };
    try expectStringSliceEqual(&expected_argv, actual.value.argv);
    try testing.expectEqual(@as(usize, 1), actual.value.options.debug_level);
    try testing.expectEqual(false, actual.value.options.warnings);
    try testing.expectEqual(false, actual.value.options.dump_defs);
    try testing.expectEqual(false, actual.value.options.preserve);
    try testing.expectEqual(@as(usize, 1), actual.value.options.reference_files.len);
    try testing.expectEqualStrings("foo.symref", actual.value.options.reference_files[0]);
    try testing.expect(actual.value.options.dump_types_file == null);
}
