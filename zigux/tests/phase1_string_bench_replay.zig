const std = @import("std");
const string = @import("string");

const iterations_string: u64 = 40_000;

fn stringBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_string) : (idx += 1) {
        var appended = [_]u8{ 'h', 'i', 0, 'x', 'x', 'x' };
        checksum +%= @intCast(string.strlcat(appended[0..], "all"));
        checksum +%= @intCast(string.strspn("abba!", "ab"));
        checksum +%= @intCast(string.sysfsMatchString(&[_][]const u8{ "disabled", "auto\n", "manual" }, "auto").?);
    }
    return .{ .checksum = checksum };
}

test "phase1 string bench replay keeps the helper packet stable" {
    var appended = [_]u8{ 'h', 'i', 0, 'x', 'x', 'x' };
    try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], "all"));
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 'a', 'l', 'l', 0 }, &appended);
    try std.testing.expectEqual(@as(usize, 4), string.strspn("abba!", "ab"));
    try std.testing.expectEqual(
        @as(?usize, 1),
        string.sysfsMatchString(&[_][]const u8{ "disabled", "auto\n", "manual" }, "auto"),
    );
}

test "phase1 string bench replay keeps the 40000-iteration checksum stable" {
    const result = stringBench();
    try std.testing.expectEqual(@as(u64, 400_000), result.checksum);
}
