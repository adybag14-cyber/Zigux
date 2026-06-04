const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

const BridgePacket = struct {
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

test "genksyms bridge accepts and renders exactly sixteen reference files" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "-r", "01.symref",
        "-r", "02.symref",
        "-r", "03.symref",
        "-r", "04.symref",
        "-r", "05.symref",
        "-r", "06.symref",
        "-r", "07.symref",
        "-r", "08.symref",
        "-r", "09.symref",
        "-r", "10.symref",
        "-r", "11.symref",
        "-r", "12.symref",
        "-r", "13.symref",
        "-r", "14.symref",
        "-r", "15.symref",
        "-r", "16.symref",
        "-d",
    };

    const outcome = try genksyms.parseArgs(arena, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 16), request.reference_files.len);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqualSlices([]const u8, &args, request.rendered_args);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const parsed = try std.json.parseFromSlice(BridgePacket, testing.allocator, output.written(), .{});
    defer parsed.deinit();

    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.tool);
    try testing.expectEqualStrings("cpp-stream", parsed.value.stdin);
    try testing.expectEqualStrings("symversions", parsed.value.stdout);
    try testing.expectEqual(@as(usize, args.len + 1), parsed.value.argv.len);
    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.argv[0]);
    for (args, parsed.value.argv[1..]) |expected, actual| {
        try testing.expectEqualStrings(expected, actual);
    }
    try testing.expectEqual(@as(usize, 16), parsed.value.options.reference_files.len);
    try testing.expectEqualStrings("01.symref", parsed.value.options.reference_files[0]);
    try testing.expectEqualStrings("16.symref", parsed.value.options.reference_files[15]);
    try testing.expectEqual(@as(usize, 1), parsed.value.options.debug_level);
    try testing.expect(!parsed.value.options.warnings);
    try testing.expect(!parsed.value.options.dump_defs);
    try testing.expect(!parsed.value.options.preserve);
    try testing.expect(parsed.value.options.dump_types_file == null);
}
