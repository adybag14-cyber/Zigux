const std = @import("std");
const testing = std.testing;
const genksyms = @import("genksyms.zig");

test "genksyms bridge preserves DEL byte JSON data" {
    const del_payload = [_]u8{ 'l', 'i', 'v', 'e', 0x7f, 's', 'y', 'm' };
    const rendered_args = [_][]const u8{del_payload[0..]};
    const reference_files = [_][]const u8{del_payload[0..]};
    const request = genksyms.Request{
        .raw_args = &rendered_args,
        .rendered_args = &rendered_args,
        .debug_level = 0,
        .warnings = false,
        .dump_defs = false,
        .preserve = false,
        .reference_files = &reference_files,
        .dump_types_file = del_payload[0..],
    };

    var output: std.Io.Writer.Allocating = .init(testing.allocator);
    defer output.deinit();

    try genksyms.renderGenksymsBridge(&output.writer, request);
    const written = output.written();
    try testing.expect(std.mem.containsAtLeast(u8, written, 3, del_payload[0..]));
    try testing.expect(std.mem.indexOf(u8, written, "\\u007f") == null);
    try testing.expect(std.mem.indexOf(u8, written, "\\u00") == null);

    const parsed = try std.json.parseFromSlice(std.json.Value, testing.allocator, written, .{});
    defer parsed.deinit();
}
