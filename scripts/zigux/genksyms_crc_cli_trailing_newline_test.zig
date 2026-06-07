const std = @import("std");
const gen = @import("genksyms_crc.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "genksyms_crc CLI trims trailing newlines without emitting blank records" {
    const input_path = ".zig-cache-genksyms-crc-trailing-newline-input.txt";
    const cwd = std.Io.Dir.cwd();
    try cwd.writeFile(std.testing.io, .{
        .sub_path = input_path,
        .data = "int\nstruct device\n\n",
    });
    defer cwd.deleteFile(std.testing.io, input_path) catch {};

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ "zig", "run", "scripts/zigux/genksyms_crc.zig", "--", input_path },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = 0 }, result.term);
    try std.testing.expectEqualStrings("", result.stderr);

    const int_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("int")});
    defer std.testing.allocator.free(int_crc);
    const struct_crc = try std.fmt.allocPrint(std.testing.allocator, "0x{x:0>8}", .{gen.crc32("struct device")});
    defer std.testing.allocator.free(struct_crc);

    try expectContains(result.stdout, "\"input\":\"int\"");
    try expectContains(result.stdout, int_crc);
    try expectContains(result.stdout, "\"input\":\"struct device\"");
    try expectContains(result.stdout, struct_crc);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"\\n\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, result.stdout, "\"input\":\"\"") == null);
    try std.testing.expectEqual(@as(usize, 2), std.mem.count(u8, result.stdout, "crc_hex"));
}
