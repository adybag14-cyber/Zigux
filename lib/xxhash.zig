// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

const PRIME32_1: u32 = 2654435761;
const PRIME32_2: u32 = 2246822519;
const PRIME32_3: u32 = 3266489917;
const PRIME32_4: u32 = 668265263;
const PRIME32_5: u32 = 374761393;

const PRIME64_1: u64 = 11400714785074694791;
const PRIME64_2: u64 = 14029467366897019727;
const PRIME64_3: u64 = 1609587929392839161;
const PRIME64_4: u64 = 9650029242287828579;
const PRIME64_5: u64 = 2870177450012600261;

fn rotl32(value: u32, comptime amount: u5) u32 {
    return std.math.rotl(u32, value, amount);
}

fn rotl64(value: u64, comptime amount: u6) u64 {
    return std.math.rotl(u64, value, amount);
}

fn read32(input: []const u8, offset: usize) u32 {
    return std.mem.readInt(u32, input[offset..][0..4], .little);
}

fn read64(input: []const u8, offset: usize) u64 {
    return std.mem.readInt(u64, input[offset..][0..8], .little);
}

fn xxh32Round(seed: u32, input: u32) u32 {
    var acc = seed +% input *% PRIME32_2;
    acc = rotl32(acc, 13);
    acc *%= PRIME32_1;
    return acc;
}

pub fn xxh32(input: []const u8, seed: u32) u32 {
    var p: usize = 0;
    var h32: u32 = undefined;

    if (input.len >= 16) {
        const limit = input.len - 16;
        var v1 = seed +% PRIME32_1 +% PRIME32_2;
        var v2 = seed +% PRIME32_2;
        var v3 = seed;
        var v4 = seed -% PRIME32_1;

        while (p <= limit) {
            v1 = xxh32Round(v1, read32(input, p));
            p += 4;
            v2 = xxh32Round(v2, read32(input, p));
            p += 4;
            v3 = xxh32Round(v3, read32(input, p));
            p += 4;
            v4 = xxh32Round(v4, read32(input, p));
            p += 4;
        }

        h32 = rotl32(v1, 1) +% rotl32(v2, 7) +% rotl32(v3, 12) +% rotl32(v4, 18);
    } else {
        h32 = seed +% PRIME32_5;
    }

    h32 +%= @intCast(input.len);

    while (p + 4 <= input.len) {
        h32 +%= read32(input, p) *% PRIME32_3;
        h32 = rotl32(h32, 17) *% PRIME32_4;
        p += 4;
    }

    while (p < input.len) : (p += 1) {
        h32 +%= @as(u32, input[p]) *% PRIME32_5;
        h32 = rotl32(h32, 11) *% PRIME32_1;
    }

    h32 ^= h32 >> 15;
    h32 *%= PRIME32_2;
    h32 ^= h32 >> 13;
    h32 *%= PRIME32_3;
    h32 ^= h32 >> 16;
    return h32;
}

fn xxh64Round(acc_in: u64, input: u64) u64 {
    var acc = acc_in +% input *% PRIME64_2;
    acc = rotl64(acc, 31);
    acc *%= PRIME64_1;
    return acc;
}

fn xxh64MergeRound(acc_in: u64, value_in: u64) u64 {
    var acc = acc_in;
    const value = xxh64Round(0, value_in);
    acc ^= value;
    acc = acc *% PRIME64_1 +% PRIME64_4;
    return acc;
}

pub fn xxh64(input: []const u8, seed: u64) u64 {
    var p: usize = 0;
    var h64: u64 = undefined;

    if (input.len >= 32) {
        const limit = input.len - 32;
        var v1 = seed +% PRIME64_1 +% PRIME64_2;
        var v2 = seed +% PRIME64_2;
        var v3 = seed;
        var v4 = seed -% PRIME64_1;

        while (p <= limit) {
            v1 = xxh64Round(v1, read64(input, p));
            p += 8;
            v2 = xxh64Round(v2, read64(input, p));
            p += 8;
            v3 = xxh64Round(v3, read64(input, p));
            p += 8;
            v4 = xxh64Round(v4, read64(input, p));
            p += 8;
        }

        h64 = rotl64(v1, 1) +% rotl64(v2, 7) +% rotl64(v3, 12) +% rotl64(v4, 18);
        h64 = xxh64MergeRound(h64, v1);
        h64 = xxh64MergeRound(h64, v2);
        h64 = xxh64MergeRound(h64, v3);
        h64 = xxh64MergeRound(h64, v4);
    } else {
        h64 = seed +% PRIME64_5;
    }

    h64 +%= @intCast(input.len);
    return xxh64FinalizeTail(h64, input[p..]);
}

fn xxh64FinalizeTail(h64_in: u64, tail: []const u8) u64 {
    var h64 = h64_in;
    var p: usize = 0;

    while (p + 8 <= tail.len) {
        const k1 = xxh64Round(0, read64(tail, p));
        h64 ^= k1;
        h64 = rotl64(h64, 27) *% PRIME64_1 +% PRIME64_4;
        p += 8;
    }

    if (p + 4 <= tail.len) {
        h64 ^= @as(u64, read32(tail, p)) *% PRIME64_1;
        h64 = rotl64(h64, 23) *% PRIME64_2 +% PRIME64_3;
        p += 4;
    }

    while (p < tail.len) : (p += 1) {
        h64 ^= @as(u64, tail[p]) *% PRIME64_5;
        h64 = rotl64(h64, 11) *% PRIME64_1;
    }

    h64 ^= h64 >> 33;
    h64 *%= PRIME64_2;
    h64 ^= h64 >> 29;
    h64 *%= PRIME64_3;
    h64 ^= h64 >> 32;
    return h64;
}

pub fn xxhash(input: []const u8, seed: u64) usize {
    return if (@sizeOf(usize) == 8)
        @intCast(xxh64(input, seed))
    else
        @intCast(xxh32(input, @truncate(seed)));
}

pub const Xxh64State = struct {
    total_len: u64,
    v1: u64,
    v2: u64,
    v3: u64,
    v4: u64,
    mem: [32]u8,
    memsize: usize,

    pub fn init(seed: u64) Xxh64State {
        var state: Xxh64State = undefined;
        state.reset(seed);
        return state;
    }

    pub fn reset(self: *Xxh64State, seed: u64) void {
        self.total_len = 0;
        self.v1 = seed +% PRIME64_1 +% PRIME64_2;
        self.v2 = seed +% PRIME64_2;
        self.v3 = seed;
        self.v4 = seed -% PRIME64_1;
        self.memsize = 0;
    }

    pub fn update(self: *Xxh64State, input: []const u8) void {
        var p: usize = 0;
        self.total_len +%= @intCast(input.len);

        if (self.memsize + input.len < 32) {
            @memcpy(self.mem[self.memsize .. self.memsize + input.len], input);
            self.memsize += input.len;
            return;
        }

        if (self.memsize != 0) {
            const fill = 32 - self.memsize;
            @memcpy(self.mem[self.memsize..32], input[0..fill]);
            self.v1 = xxh64Round(self.v1, read64(self.mem[0..], 0));
            self.v2 = xxh64Round(self.v2, read64(self.mem[0..], 8));
            self.v3 = xxh64Round(self.v3, read64(self.mem[0..], 16));
            self.v4 = xxh64Round(self.v4, read64(self.mem[0..], 24));
            p += fill;
            self.memsize = 0;
        }

        if (p + 32 <= input.len) {
            const limit = input.len - 32;
            var v1 = self.v1;
            var v2 = self.v2;
            var v3 = self.v3;
            var v4 = self.v4;

            while (p <= limit) {
                v1 = xxh64Round(v1, read64(input, p));
                p += 8;
                v2 = xxh64Round(v2, read64(input, p));
                p += 8;
                v3 = xxh64Round(v3, read64(input, p));
                p += 8;
                v4 = xxh64Round(v4, read64(input, p));
                p += 8;
            }

            self.v1 = v1;
            self.v2 = v2;
            self.v3 = v3;
            self.v4 = v4;
        }

        if (p < input.len) {
            const remaining = input.len - p;
            @memcpy(self.mem[0..remaining], input[p..]);
            self.memsize = remaining;
        }
    }

    pub fn digest(self: *const Xxh64State) u64 {
        var h64: u64 = undefined;
        if (self.total_len >= 32) {
            h64 = rotl64(self.v1, 1) +% rotl64(self.v2, 7) +% rotl64(self.v3, 12) +% rotl64(self.v4, 18);
            h64 = xxh64MergeRound(h64, self.v1);
            h64 = xxh64MergeRound(h64, self.v2);
            h64 = xxh64MergeRound(h64, self.v3);
            h64 = xxh64MergeRound(h64, self.v4);
        } else {
            h64 = self.v3 +% PRIME64_5;
        }

        h64 +%= self.total_len;
        return xxh64FinalizeTail(h64, self.mem[0..self.memsize]);
    }
};

pub fn xxh64_reset(state: *Xxh64State, seed: u64) void {
    state.reset(seed);
}

pub fn xxh64_update(state: *Xxh64State, input: []const u8) i32 {
    state.update(input);
    return 0;
}

pub fn xxh64_digest(state: *const Xxh64State) u64 {
    return state.digest();
}

test "xxhash empty seed zero vectors" {
    try std.testing.expectEqual(@as(u32, 0x02cc5d05), xxh32("", 0));
    try std.testing.expectEqual(@as(u64, 0xef46db3751d8e999), xxh64("", 0));
}

test "xxhash one shot is stable across thresholds" {
    var data: [65]u8 = undefined;
    for (&data, 0..) |*byte, i| {
        byte.* = @intCast((i * 37 + 11) & 0xff);
    }

    try std.testing.expectEqual(xxh32(data[0..15], 0x12345678), xxh32(data[0..15], 0x12345678));
    try std.testing.expectEqual(xxh32(data[0..16], 0x12345678), xxh32(data[0..16], 0x12345678));
    try std.testing.expectEqual(xxh64(data[0..31], 0x123456789abcdef0), xxh64(data[0..31], 0x123456789abcdef0));
    try std.testing.expectEqual(xxh64(data[0..32], 0x123456789abcdef0), xxh64(data[0..32], 0x123456789abcdef0));
}

test "xxh64 streaming split updates equal one shot" {
    var data: [97]u8 = undefined;
    for (&data, 0..) |*byte, i| {
        byte.* = @intCast((i * 37 + 11) & 0xff);
    }

    const seed: u64 = 0x123456789abcdef0;
    const expected = xxh64(&data, seed);

    for (0..data.len + 1) |split| {
        var state = Xxh64State.init(seed);
        state.update(data[0..split]);
        state.update(data[split..]);
        try std.testing.expectEqual(expected, state.digest());
    }

    var state = Xxh64State.init(seed);
    state.update(data[0..0]);
    state.update(data[0..1]);
    state.update(data[1..17]);
    state.update(data[17..32]);
    state.update(data[32..65]);
    state.update(data[65..]);
    try std.testing.expectEqual(expected, state.digest());
}

test "xxh64 byte by byte streaming covers short thresholds" {
    var data: [65]u8 = undefined;
    for (&data, 0..) |*byte, i| {
        byte.* = @intCast((i * 19 + 5) & 0xff);
    }

    const seed: u64 = 0xfeedfacedeadbeef;
    for (0..data.len + 1) |len| {
        var state = Xxh64State.init(seed);
        for (data[0..len]) |byte| {
            const one = [_]u8{byte};
            state.update(&one);
        }
        try std.testing.expectEqual(xxh64(data[0..len], seed), state.digest());
    }
}
