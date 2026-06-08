// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn memcatP(comptime T: type, allocator: std.mem.Allocator, a: []const ?*T, b: []const ?*T) ![]?*T {
    const a_count = countUntilNull(T, a);
    const b_count = countUntilNull(T, b);
    var out = try allocator.alloc(?*T, a_count + b_count + 1);
    @memcpy(out[0..a_count], a[0..a_count]);
    @memcpy(out[a_count .. a_count + b_count], b[0..b_count]);
    out[a_count + b_count] = null;
    return out;
}

pub fn countUntilNull(comptime T: type, values: []const ?*T) usize {
    for (values, 0..) |value, idx| {
        if (value == null) return idx;
    }
    return values.len;
}

test "memcatP merges null terminated pointer arrays" {
    var one: i32 = 1;
    var two: i32 = 2;
    var three: i32 = 3;
    const lhs = [_]?*i32{ &one, &two, null };
    const rhs = [_]?*i32{ &three, null };

    const out = try memcatP(i32, std.testing.allocator, &lhs, &rhs);
    defer std.testing.allocator.free(out);

    try std.testing.expectEqual(@as(usize, 3), countUntilNull(i32, out));
    try std.testing.expectEqual(@as(i32, 1), out[0].?.*);
    try std.testing.expectEqual(@as(i32, 2), out[1].?.*);
    try std.testing.expectEqual(@as(i32, 3), out[2].?.*);
    try std.testing.expect(out[3] == null);
}
