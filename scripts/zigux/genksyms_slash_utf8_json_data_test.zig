const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

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

test "genksyms bridge preserves slash and utf8 JSON data" {
    const rendered_args = [_][]const u8{
        "--reference",
        "refs/linux/mod_\xC3\xA9.symvers",
        "--dump-types",
        "types/linux/symtypes_\xCE\xB2.out",
        "drivers/zigux/path_\xE2\x9C\x93.c",
    };
    const reference_files = [_][]const u8{"refs/linux/mod_\xC3\xA9.symvers"};
    const request = genksyms.Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .debug_level = 0,
        .warnings = false,
        .dump_defs = false,
        .preserve = false,
        .reference_files = &reference_files,
        .dump_types_file = "types/linux/symtypes_\xCE\xB2.out",
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const json = output.written();

    try testing.expect(std.mem.indexOf(u8, json, "\\/") == null);
    try testing.expect(std.mem.containsAtLeast(u8, json, 1, "refs/linux/mod_\xC3\xA9.symvers"));
    try testing.expect(std.mem.containsAtLeast(u8, json, 1, "types/linux/symtypes_\xCE\xB2.out"));
    try testing.expect(std.mem.containsAtLeast(u8, json, 1, "drivers/zigux/path_\xE2\x9C\x93.c"));

    const parsed = try std.json.parseFromSlice(BridgePayload, testing.allocator, json, .{});
    defer parsed.deinit();

    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.tool);
    try testing.expectEqual(@as(usize, 6), parsed.value.argv.len);
    try testing.expectEqualStrings("scripts/genksyms/genksyms", parsed.value.argv[0]);
    try testing.expectEqualStrings("refs/linux/mod_\xC3\xA9.symvers", parsed.value.argv[2]);
    try testing.expectEqualStrings("types/linux/symtypes_\xCE\xB2.out", parsed.value.argv[4]);
    try testing.expectEqualStrings("drivers/zigux/path_\xE2\x9C\x93.c", parsed.value.argv[5]);
    try testing.expectEqual(@as(usize, 1), parsed.value.options.reference_files.len);
    try testing.expectEqualStrings("refs/linux/mod_\xC3\xA9.symvers", parsed.value.options.reference_files[0]);
    try testing.expectEqualStrings("types/linux/symtypes_\xCE\xB2.out", parsed.value.options.dump_types_file.?);
}
