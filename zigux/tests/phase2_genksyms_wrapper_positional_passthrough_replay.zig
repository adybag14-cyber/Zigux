const std = @import("std");
const genksyms = @import("genksyms");

const testing = std.testing;
const positional_passthrough_expected_json = @embedFile("fixtures/genksyms_bridge/positional_passthrough_expected.json");

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

test "phase 2 genksyms wrapper positional passthrough keeps parsed leftovers behind later options" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
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

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(!request.warnings);
    try testing.expect(!request.dump_defs);
    try testing.expect(!request.preserve);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("foo.symref", request.reference_files[0]);
    try testing.expect(request.dump_types_file == null);

    const expected_rendered_args = [_][]const u8{
        "-d",
        "-r",
        "foo.symref",
        "leftover.c",
        "rightover.h",
    };
    try expectStringSliceEqual(&expected_rendered_args, request.rendered_args);
}

test "phase 2 genksyms wrapper positional passthrough replay matches fixture output" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();

    const args = [_][]const u8{
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
    const expected = try std.json.parseFromSlice(BridgePayload, testing.allocator, positional_passthrough_expected_json, .{});
    defer expected.deinit();

    try testing.expectEqualStrings(expected.value.tool, actual.value.tool);
    try testing.expectEqualStrings(expected.value.stdin, actual.value.stdin);
    try testing.expectEqualStrings(expected.value.stdout, actual.value.stdout);
    try expectStringSliceEqual(expected.value.argv, actual.value.argv);
    try testing.expectEqual(expected.value.options.debug_level, actual.value.options.debug_level);
    try testing.expectEqual(expected.value.options.warnings, actual.value.options.warnings);
    try testing.expectEqual(expected.value.options.dump_defs, actual.value.options.dump_defs);
    try testing.expectEqual(expected.value.options.preserve, actual.value.options.preserve);
    try expectStringSliceEqual(expected.value.options.reference_files, actual.value.options.reference_files);
    try testing.expectEqual(expected.value.options.dump_types_file, actual.value.options.dump_types_file);
}
