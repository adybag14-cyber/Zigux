const std = @import("std");
const genksyms = @import("genksyms.zig");

const testing = std.testing;

const BridgePacket = struct {
    tool: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    argv: []const []const u8,
    options: Options,

    const Options = struct {
        debug_level: usize,
        warnings: bool,
        dump_defs: bool,
        preserve: bool,
        reference_files: []const []const u8,
        dump_types_file: ?[]const u8,
    };
};

fn expectRequest(outcome: genksyms.ParseOutcome) !genksyms.Request {
    return switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => error.ExpectedRequestCommand,
        },
        .failure => error.ExpectedRequestCommand,
    };
}

test "genksyms bridge renders explicit empty terminator request" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const arena = arena_state.allocator();

    const args = [_][]const u8{
        "--version",
        "orphan.c",
        "-d",
        "--",
    };
    const request = try expectRequest(try genksyms.parseArgs(arena, &args));

    try testing.expectEqual(@as(usize, 1), request.version_count);
    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expectEqual(@as(usize, 4), request.rendered_args.len);
    try testing.expectEqualStrings("--version", request.rendered_args[0]);
    try testing.expectEqualStrings("-d", request.rendered_args[1]);
    try testing.expectEqualStrings("orphan.c", request.rendered_args[2]);
    try testing.expectEqualStrings("--", request.rendered_args[3]);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    try testing.expect(std.mem.endsWith(u8, output.written(), "\"orphan.c\",\"--\"],\"options\":{\"debug_level\":1,\"warnings\":false,\"dump_defs\":false,\"preserve\":false,\"reference_files\":[],\"dump_types_file\":null}}\n"));
    try testing.expect(std.mem.indexOf(u8, output.written(), "\"--\",null") == null);

    const parsed = try std.json.parseFromSlice(BridgePacket, testing.allocator, output.written(), .{});
    defer parsed.deinit();

    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.tool);
    try testing.expectEqualStrings("cpp-stream", parsed.value.stdin);
    try testing.expectEqualStrings("symversions", parsed.value.stdout);
    try testing.expectEqual(@as(usize, 5), parsed.value.argv.len);
    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.argv[0]);
    try testing.expectEqualStrings("--version", parsed.value.argv[1]);
    try testing.expectEqualStrings("-d", parsed.value.argv[2]);
    try testing.expectEqualStrings("orphan.c", parsed.value.argv[3]);
    try testing.expectEqualStrings("--", parsed.value.argv[4]);
    try testing.expectEqual(@as(usize, 1), parsed.value.options.debug_level);
    try testing.expectEqual(@as(usize, 0), parsed.value.options.reference_files.len);
    try testing.expect(parsed.value.options.dump_types_file == null);
}
