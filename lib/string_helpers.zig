// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const EINVAL: i32 = -22;

pub fn sysfsStreq(s1: []const u8, s2: []const u8) bool {
    return std.mem.eql(u8, sysfsComparablePrefix(s1), sysfsComparablePrefix(s2));
}

pub fn matchString(array: []const ?[]const u8, n: usize, needle: []const u8) i32 {
    const limit = @min(n, array.len);
    for (array[0..limit], 0..) |item, index| {
        const value = item orelse break;
        if (std.mem.eql(u8, cStringPrefix(value), cStringPrefix(needle))) {
            return @intCast(index);
        }
    }
    return EINVAL;
}

pub fn sysfsMatchString(array: []const ?[]const u8, n: usize, needle: []const u8) i32 {
    const limit = @min(n, array.len);
    for (array[0..limit], 0..) |item, index| {
        const value = item orelse break;
        if (sysfsStreq(value, needle)) {
            return @intCast(index);
        }
    }
    return EINVAL;
}

pub fn strreplace(buf: []u8, old: u8, new: u8) []u8 {
    for (cStringPrefixMutable(buf)) |*ch| {
        if (ch.* == old) {
            ch.* = new;
        }
    }
    return buf;
}

pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {
    std.debug.assert(src.len >= count);

    if (dest.len > count) {
        @memcpy(dest[0..count], src[0..count]);
        @memset(dest[count..], pad);
    } else {
        @memcpy(dest, src[0..dest.len]);
    }
}

pub fn stringIsTerminated(s: []const u8, len: usize) bool {
    return std.mem.indexOfScalar(u8, s[0..@min(len, s.len)], 0) != null;
}

pub fn stringUpper(dest: []u8, src: []const u8) void {
    copyCStringMapped(dest, src, std.ascii.toUpper);
}

pub fn stringLower(dest: []u8, src: []const u8) void {
    copyCStringMapped(dest, src, std.ascii.toLower);
}

fn cStringPrefix(s: []const u8) []const u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn cStringPrefixMutable(s: []u8) []u8 {
    return s[0 .. std.mem.indexOfScalar(u8, s, 0) orelse s.len];
}

fn sysfsComparablePrefix(s: []const u8) []const u8 {
    const prefix = cStringPrefix(s);
    if (prefix.len != 0 and prefix[prefix.len - 1] == '\n') {
        return prefix[0 .. prefix.len - 1];
    }
    return prefix;
}

fn copyCStringMapped(dest: []u8, src: []const u8, comptime mapper: fn (u8) u8) void {
    const limit = @min(dest.len, src.len);
    var index: usize = 0;

    while (index < limit) : (index += 1) {
        const ch = src[index];
        dest[index] = mapper(ch);
        if (ch == 0) {
            break;
        }
    }
}

test "sysfsStreq accepts optional trailing newline" {
    try std.testing.expect(sysfsStreq("enabled", "enabled\n"));
    try std.testing.expect(sysfsStreq("enabled\n", "enabled"));
    try std.testing.expect(sysfsStreq("enabled\x00ignored", "enabled\n"));
    try std.testing.expect(!sysfsStreq("enabled", "disabled"));
    try std.testing.expect(!sysfsStreq("enabled\nlater", "enabled"));
}

test "matchString stops at null sentinels and returns -EINVAL on miss" {
    const choices = [_]?[]const u8{ "alpha", "beta", null, "gamma" };

    try std.testing.expectEqual(@as(i32, 0), matchString(&choices, choices.len, "alpha"));
    try std.testing.expectEqual(@as(i32, 1), matchString(&choices, choices.len, "beta\x00ignored"));
    try std.testing.expectEqual(EINVAL, matchString(&choices, choices.len, "gamma"));
    try std.testing.expectEqual(EINVAL, matchString(&choices, 2, "gamma"));
}

test "sysfsMatchString reuses sysfs newline semantics" {
    const choices = [_]?[]const u8{ "offline", "online", "standby", null };

    try std.testing.expectEqual(@as(i32, 1), sysfsMatchString(&choices, choices.len, "online\n"));
    try std.testing.expectEqual(@as(i32, 2), sysfsMatchString(&choices, choices.len, "standby"));
    try std.testing.expectEqual(EINVAL, sysfsMatchString(&choices, choices.len, "missing\n"));
}

test "strreplace mutates in place without touching bytes after NUL" {
    var buffer = [_]u8{ 'a', '-', 'b', 0, '-', 'x' };
    const returned = strreplace(&buffer, '-', '_');

    try std.testing.expectEqualStrings("a_b", cStringPrefix(returned));
    try std.testing.expectEqual(@as(u8, '-'), buffer[4]);
}

test "memcpyAndPad matches the bounded copy-and-pad contract" {
    var padded = [_]u8{ 0, 0, 0, 0, 0, 0 };
    memcpyAndPad(&padded, "zig", 3, '.');
    try std.testing.expectEqualSlices(u8, "zig...", &padded);

    var truncated = [_]u8{ 0, 0, 0, 0 };
    memcpyAndPad(&truncated, "zigux", 5, '.');
    try std.testing.expectEqualSlices(u8, "zigu", &truncated);
}

test "stringIsTerminated reports whether a bounded window contains NUL" {
    try std.testing.expect(stringIsTerminated("ok\x00tail", 3));
    try std.testing.expect(stringIsTerminated("ok\x00tail", 32));
    try std.testing.expect(!stringIsTerminated("ok\x00tail", 2));
    try std.testing.expect(!stringIsTerminated("plain", 5));
}

test "stringUpper and stringLower perform bounded ASCII case conversion" {
    var upper = [_]u8{ '?', '?', '?', '?', '?', '?', '?', '?' };
    stringUpper(&upper, "abC9!\x00tail");
    try std.testing.expectEqualSlices(u8, "ABC9!\x00", upper[0..6]);
    try std.testing.expectEqual(@as(u8, '?'), upper[6]);

    var lower = [_]u8{ '?', '?', '?', '?', '?' };
    stringLower(&lower, "AbCDe");
    try std.testing.expectEqualSlices(u8, "abcde", &lower);
}
