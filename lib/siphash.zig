// SPDX-License-Identifier: (GPL-2.0-only OR BSD-3-Clause)
const std = @import("std");

pub const SiphashKey = extern struct {
    key: [2]u64,

    pub fn fromBytes(bytes: [16]u8) SiphashKey {
        return .{ .key = .{
            std.mem.readInt(u64, bytes[0..8], .little),
            std.mem.readInt(u64, bytes[8..16], .little),
        } };
    }
};

pub const siphash_key_t = SiphashKey;
pub const HsiphashKey = extern struct { key: [2]u64 };
pub const hsiphash_key_t = HsiphashKey;

const SIPHASH_CONST_0: u64 = 0x736f6d6570736575;
const SIPHASH_CONST_1: u64 = 0x646f72616e646f6d;
const SIPHASH_CONST_2: u64 = 0x6c7967656e657261;
const SIPHASH_CONST_3: u64 = 0x7465646279746573;

pub fn siphash_key_is_zero(key: *const SiphashKey) bool {
    return (key.key[0] | key.key[1]) == 0;
}

const State = struct {
    v0: u64,
    v1: u64,
    v2: u64,
    v3: u64,

    fn init(key: [2]u64) State {
        return .{
            .v0 = SIPHASH_CONST_0 ^ key[0],
            .v1 = SIPHASH_CONST_1 ^ key[1],
            .v2 = SIPHASH_CONST_2 ^ key[0],
            .v3 = SIPHASH_CONST_3 ^ key[1],
        };
    }

    fn round(self: *State) void {
        self.v0 +%= self.v1;
        self.v1 = std.math.rotl(u64, self.v1, 13);
        self.v1 ^= self.v0;
        self.v0 = std.math.rotl(u64, self.v0, 32);

        self.v2 +%= self.v3;
        self.v3 = std.math.rotl(u64, self.v3, 16);
        self.v3 ^= self.v2;

        self.v0 +%= self.v3;
        self.v3 = std.math.rotl(u64, self.v3, 21);
        self.v3 ^= self.v0;

        self.v2 +%= self.v1;
        self.v1 = std.math.rotl(u64, self.v1, 17);
        self.v1 ^= self.v2;
        self.v2 = std.math.rotl(u64, self.v2, 32);
    }

    fn compress(self: *State, word: u64, comptime rounds: usize) void {
        self.v3 ^= word;
        inline for (0..rounds) |_| self.round();
        self.v0 ^= word;
    }

    fn finish(self: *State, b: u64, comptime c_rounds: usize, comptime d_rounds: usize) u64 {
        self.compress(b, c_rounds);
        self.v2 ^= 0xff;
        inline for (0..d_rounds) |_| self.round();
        return (self.v0 ^ self.v1) ^ (self.v2 ^ self.v3);
    }
};

pub fn siphash(data: []const u8, key: *const SiphashKey) u64 {
    return siphashRounds(data, key.key, 2, 4);
}

pub fn __siphash_unaligned(data: []const u8, key: *const SiphashKey) u64 {
    return siphash(data, key);
}

pub fn __siphash_aligned(data: []const u8, key: *const SiphashKey) u64 {
    return siphash(data, key);
}

pub fn siphash13(data: []const u8, key: *const SiphashKey) u64 {
    return siphashRounds(data, key.key, 1, 3);
}

pub fn siphash_1u64(first: u64, key: *const SiphashKey) u64 {
    var state = preamble(8, key.key);
    state.compress(first, 2);
    return state.finish(@as(u64, 8) << 56, 2, 4);
}

pub fn siphash_2u64(first: u64, second: u64, key: *const SiphashKey) u64 {
    var state = preamble(16, key.key);
    state.compress(first, 2);
    state.compress(second, 2);
    return state.finish(@as(u64, 16) << 56, 2, 4);
}

pub fn siphash_3u64(first: u64, second: u64, third: u64, key: *const SiphashKey) u64 {
    var state = preamble(24, key.key);
    state.compress(first, 2);
    state.compress(second, 2);
    state.compress(third, 2);
    return state.finish(@as(u64, 24) << 56, 2, 4);
}

pub fn siphash_4u64(first: u64, second: u64, third: u64, fourth: u64, key: *const SiphashKey) u64 {
    var state = preamble(32, key.key);
    state.compress(first, 2);
    state.compress(second, 2);
    state.compress(third, 2);
    state.compress(fourth, 2);
    return state.finish(@as(u64, 32) << 56, 2, 4);
}

pub fn siphash_1u32(first: u32, key: *const SiphashKey) u64 {
    var state = preamble(4, key.key);
    return state.finish((@as(u64, 4) << 56) | first, 2, 4);
}

pub fn siphash_2u32(first: u32, second: u32, key: *const SiphashKey) u64 {
    return siphash_1u64((@as(u64, second) << 32) | first, key);
}

pub fn siphash_3u32(first: u32, second: u32, third: u32, key: *const SiphashKey) u64 {
    var state = preamble(12, key.key);
    const combined = (@as(u64, second) << 32) | first;
    state.compress(combined, 2);
    return state.finish((@as(u64, 12) << 56) | third, 2, 4);
}

pub fn siphash_4u32(first: u32, second: u32, third: u32, fourth: u32, key: *const SiphashKey) u64 {
    return siphash_2u64((@as(u64, second) << 32) | first, (@as(u64, fourth) << 32) | third, key);
}

pub fn hsiphash(data: []const u8, key: *const HsiphashKey) u32 {
    return @truncate(siphashRounds(data, key.key, 1, 3));
}

pub fn __hsiphash_unaligned(data: []const u8, key: *const HsiphashKey) u32 {
    return hsiphash(data, key);
}

pub fn __hsiphash_aligned(data: []const u8, key: *const HsiphashKey) u32 {
    return hsiphash(data, key);
}

pub fn hsiphash_1u32(first: u32, key: *const HsiphashKey) u32 {
    var state = preamble(4, key.key);
    return @truncate(state.finish((@as(u64, 4) << 56) | first, 1, 3));
}

pub fn hsiphash_2u32(first: u32, second: u32, key: *const HsiphashKey) u32 {
    var state = preamble(8, key.key);
    state.compress((@as(u64, second) << 32) | first, 1);
    return @truncate(state.finish(@as(u64, 8) << 56, 1, 3));
}

pub fn hsiphash_3u32(first: u32, second: u32, third: u32, key: *const HsiphashKey) u32 {
    var state = preamble(12, key.key);
    state.compress((@as(u64, second) << 32) | first, 1);
    return @truncate(state.finish((@as(u64, 12) << 56) | third, 1, 3));
}

pub fn hsiphash_4u32(first: u32, second: u32, third: u32, fourth: u32, key: *const HsiphashKey) u32 {
    var state = preamble(16, key.key);
    state.compress((@as(u64, second) << 32) | first, 1);
    state.compress((@as(u64, fourth) << 32) | third, 1);
    return @truncate(state.finish(@as(u64, 16) << 56, 1, 3));
}

fn preamble(len: usize, key: [2]u64) State {
    _ = len;
    return State.init(key);
}

fn siphashRounds(data: []const u8, key: [2]u64, comptime c_rounds: usize, comptime d_rounds: usize) u64 {
    var state = State.init(key);
    var offset: usize = 0;

    while (offset + 8 <= data.len) : (offset += 8) {
        state.compress(std.mem.readInt(u64, data[offset..][0..8], .little), c_rounds);
    }

    var b: u64 = @as(u64, data.len) << 56;
    var shift: u6 = 0;
    while (offset < data.len) : (offset += 1) {
        b |= @as(u64, data[offset]) << shift;
        shift += 8;
    }

    return state.finish(b, c_rounds, d_rounds);
}

test "siphash key zero detection" {
    const zero = SiphashKey{ .key = .{ 0, 0 } };
    const nonzero = SiphashKey{ .key = .{ 0, 1 } };

    try std.testing.expect(siphash_key_is_zero(&zero));
    try std.testing.expect(!siphash_key_is_zero(&nonzero));
}

test "siphash 2-4 official short input vectors" {
    var key_bytes: [16]u8 = undefined;
    for (&key_bytes, 0..) |*byte, i| byte.* = @intCast(i);
    const key = SiphashKey.fromBytes(key_bytes);

    var input: [16]u8 = undefined;
    for (&input, 0..) |*byte, i| byte.* = @intCast(i);

    const vectors = [_]u64{
        0x726fdb47dd0e0e31,
        0x74f839c593dc67fd,
        0x0d6c8009d9a94f5a,
        0x85676696d7fb7e2d,
        0xcf2794e0277187b7,
        0x18765564cd99a68d,
        0xcbc9466e58fee3ce,
        0xab0200f58b01d137,
        0x93f5f5799a932462,
        0x9e0082df0ba9e4b0,
        0x7a5dbbc594ddb9f3,
        0xf4b32f46226bada7,
        0x751e8fbc860ee5fb,
        0x14ea5627c0843d90,
        0xf723ca908e7af2ee,
        0xa129ca6149be45e5,
    };

    for (vectors, 0..) |expected, len| {
        try std.testing.expectEqual(expected, siphash(input[0..len], &key));
        try std.testing.expectEqual(expected, __siphash_unaligned(input[0..len], &key));
    }
}

test "siphash integer wrappers match little-endian byte input" {
    const key = SiphashKey{ .key = .{ 0x1111111111111111, 0x2222222222222222 } };
    var bytes: [32]u8 = undefined;

    std.mem.writeInt(u64, bytes[0..8], 0x0102030405060708, .little);
    try std.testing.expectEqual(siphash(bytes[0..8], &key), siphash_1u64(0x0102030405060708, &key));

    std.mem.writeInt(u64, bytes[8..16], 0x8877665544332211, .little);
    try std.testing.expectEqual(siphash(bytes[0..16], &key), siphash_2u64(0x0102030405060708, 0x8877665544332211, &key));

    std.mem.writeInt(u32, bytes[0..4], 1, .little);
    std.mem.writeInt(u32, bytes[4..8], 2, .little);
    std.mem.writeInt(u32, bytes[8..12], 3, .little);
    std.mem.writeInt(u32, bytes[12..16], 4, .little);
    try std.testing.expectEqual(siphash(bytes[0..4], &key), siphash_1u32(1, &key));
    try std.testing.expectEqual(siphash(bytes[0..8], &key), siphash_2u32(1, 2, &key));
    try std.testing.expectEqual(siphash(bytes[0..12], &key), siphash_3u32(1, 2, 3, &key));
    try std.testing.expectEqual(siphash(bytes[0..16], &key), siphash_4u32(1, 2, 3, 4, &key));
}

test "hsiphash models Linux 64-bit SipHash1-3 truncation" {
    const hkey = HsiphashKey{ .key = .{ 0x0706050403020100, 0x0f0e0d0c0b0a0908 } };
    const skey = SiphashKey{ .key = hkey.key };
    const message = "zigux siphash";

    try std.testing.expectEqual(@as(u32, @truncate(siphash13(message, &skey))), hsiphash(message, &hkey));
}

test "hsiphash u32 wrappers match byte input" {
    const key = HsiphashKey{ .key = .{ 0x1111111111111111, 0x2222222222222222 } };
    var bytes: [16]u8 = undefined;
    std.mem.writeInt(u32, bytes[0..4], 1, .little);
    std.mem.writeInt(u32, bytes[4..8], 2, .little);
    std.mem.writeInt(u32, bytes[8..12], 3, .little);
    std.mem.writeInt(u32, bytes[12..16], 4, .little);

    try std.testing.expectEqual(hsiphash(bytes[0..4], &key), hsiphash_1u32(1, &key));
    try std.testing.expectEqual(hsiphash(bytes[0..8], &key), hsiphash_2u32(1, 2, &key));
    try std.testing.expectEqual(hsiphash(bytes[0..12], &key), hsiphash_3u32(1, 2, 3, &key));
    try std.testing.expectEqual(hsiphash(bytes[0..16], &key), hsiphash_4u32(1, 2, 3, 4, &key));
}
