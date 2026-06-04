const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

const BridgeOptions = struct {
    debug_level: usize,
    warnings: bool,
    dump_defs: bool,
    preserve: bool,
    reference_files: []const []const u8,
    dump_types_file: ?[]const u8,
};

const BridgePlan = struct {
    tool: []const u8,
    stdin: []const u8,
    stdout: []const u8,
    argv: []const []const u8,
    options: BridgeOptions,
};

fn expectArg(argv: []const []const u8, expected: []const u8) !void {
    for (argv) |arg| {
        if (std.mem.eql(u8, arg, expected)) return;
    }
    return error.ExpectedRenderedArg;
}

test "genksyms bridge round-trips mixed JSON escaped arguments" {
    var arena_state = std.heap.ArenaAllocator.init(testing.allocator);
    defer arena_state.deinit();
    const allocator = arena_state.allocator();

    const reference = "ref\"quote\\slash\nline.sym";
    const dump_types = "types\twith\rcontrols.symtypes";
    const positional = "pos\"quote\nline";
    const tail = "--tail\\path\tvalue";
    const args = [_][]const u8{
        "-d",
        "--warnings",
        "--reference",
        reference,
        "--dump-types",
        dump_types,
        positional,
        "--",
        tail,
    };
    const outcome = try genksyms.parseArgs(allocator, &args);
    const request = switch (outcome) {
        .command => |command| switch (command) {
            .request => |request| request,
            else => return error.ExpectedRequestCommand,
        },
        else => return error.ExpectedRequestCommand,
    };

    try testing.expectEqual(@as(usize, 1), request.debug_level);
    try testing.expect(request.warnings);
    try testing.expectEqualStrings(reference, request.reference_files[0]);
    try testing.expectEqualStrings(dump_types, request.dump_types_file.?);

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();
    try genksyms.renderGenksymsBridge(&output.writer, request);

    const rendered = output.written();
    try testing.expect(std.mem.indexOf(u8, rendered, "ref\\\"quote\\\\slash\\nline.sym") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "types\\twith\\rcontrols.symtypes") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "pos\\\"quote\\nline") != null);
    try testing.expect(std.mem.indexOf(u8, rendered, "--tail\\\\path\\tvalue") != null);

    const parsed = try std.json.parseFromSlice(BridgePlan, allocator, rendered, .{});
    defer parsed.deinit();
    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.tool);
    try testing.expectEqualStrings(reference, parsed.value.options.reference_files[0]);
    try testing.expectEqualStrings(dump_types, parsed.value.options.dump_types_file.?);
    try expectArg(parsed.value.argv, positional);
    try expectArg(parsed.value.argv, tail);
}
