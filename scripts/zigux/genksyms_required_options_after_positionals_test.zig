const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

const BridgeOptions = struct {
    debug_level: usize,
    warnings: bool,
    dump_defs: bool,
    preserve: bool,
    reference_files: []const []const u8,
    dump_types_file: ?[]const u8,
};

const BridgePacket = struct {
    tool: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    argv: []const []const u8,
    options: BridgeOptions,
};

test "genksyms required options after positionals render before delayed data" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "prelude.c",
        "--reference",
        "first.symref",
        "middle.c",
        "-Tinline.symtypes",
        "--debug",
        "tail.c",
    };

    const outcome = try genksyms.parseArgs(arena, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("first.symref", request.reference_files[0]);
    try testing.expectEqualStrings("inline.symtypes", request.dump_types_file.?);

    const expected_rendered = [_][]const u8{
        "--reference",
        "first.symref",
        "-Tinline.symtypes",
        "--debug",
        "prelude.c",
        "middle.c",
        "tail.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    const parsed = try std.json.parseFromSlice(BridgePacket, testing.allocator, output.written(), .{});
    defer parsed.deinit();

    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.tool);
    try testing.expectEqualStrings("cpp-stream", parsed.value.stdin);
    try testing.expectEqualStrings("symversions", parsed.value.stdout);
    try testing.expectEqual(@as(usize, expected_rendered.len + 1), parsed.value.argv.len);
    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.argv[0]);
    for (expected_rendered, 0..) |arg, index| {
        try testing.expectEqualStrings(arg, parsed.value.argv[index + 1]);
    }
    try testing.expectEqual(@as(usize, 1), parsed.value.options.debug_level);
    try testing.expect(!parsed.value.options.warnings);
    try testing.expect(!parsed.value.options.dump_defs);
    try testing.expect(!parsed.value.options.preserve);
    try testing.expectEqual(@as(usize, 1), parsed.value.options.reference_files.len);
    try testing.expectEqualStrings("first.symref", parsed.value.options.reference_files[0]);
    try testing.expectEqualStrings("inline.symtypes", parsed.value.options.dump_types_file.?);
}

test "genksyms separated dump-types after positionals keeps next option as value" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "front.c",
        "--dump-types",
        "--not-an-option.symtypes",
        "back.c",
        "-r",
        "-also-data.symref",
    };

    const outcome = try genksyms.parseArgs(arena, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqualStrings("--not-an-option.symtypes", request.dump_types_file.?);
    try testing.expectEqual(@as(usize, 1), request.reference_files.len);
    try testing.expectEqualStrings("-also-data.symref", request.reference_files[0]);

    const expected_rendered = [_][]const u8{
        "--dump-types",
        "--not-an-option.symtypes",
        "-r",
        "-also-data.symref",
        "front.c",
        "back.c",
    };
    try testing.expectEqualSlices([]const u8, &expected_rendered, request.rendered_args);
}
