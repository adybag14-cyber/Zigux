// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const RndState = struct {
    s1: u32,
    s2: u32,
    s3: u32,
    s4: u32,
};

fn tausworthe(s: u32, comptime a: u5, comptime b: u5, comptime c: u32, comptime d: u5) u32 {
    return ((s & c) << d) ^ (((s << a) ^ s) >> b);
}

pub fn prandom_u32_state(state: *RndState) u32 {
    state.s1 = tausworthe(state.s1, 6, 13, 4294967294, 18);
    state.s2 = tausworthe(state.s2, 2, 27, 4294967288, 2);
    state.s3 = tausworthe(state.s3, 13, 21, 4294967280, 7);
    state.s4 = tausworthe(state.s4, 3, 12, 4294967168, 13);
    return state.s1 ^ state.s2 ^ state.s3 ^ state.s4;
}

pub fn prandom_bytes_state(state: *RndState, buf: []u8) void {
    var offset: usize = 0;
    while (offset + 4 <= buf.len) : (offset += 4) {
        std.mem.writeInt(u32, buf[offset..][0..4], prandom_u32_state(state), .little);
    }

    if (offset < buf.len) {
        var value = prandom_u32_state(state);
        while (offset < buf.len) : (offset += 1) {
            buf[offset] = @truncate(value);
            value >>= 8;
        }
    }
}

pub fn prandom_warmup(state: *RndState) void {
    for (0..10) |_| _ = prandom_u32_state(state);
}

fn lcg(x: u32) u32 {
    return x *% 69069;
}

fn seedValue(x: u32, comptime min: u32) u32 {
    return if (x < min) x +% min else x;
}

pub fn selftestSeed(seed: u32) RndState {
    var state: RndState = undefined;
    state.s1 = seedValue(lcg(seed), 2);
    state.s2 = seedValue(lcg(state.s1), 8);
    state.s3 = seedValue(lcg(state.s2), 16);
    state.s4 = seedValue(lcg(state.s3), 128);
    prandom_warmup(&state);
    return state;
}

test "random32 warmup seed vectors match Linux selftest" {
    const expected = [_]u32{ 3484351685, 2623130059, 3125133893, 984847254 };
    for (expected, 1..) |want, seed_index| {
        var state = selftestSeed(@intCast(seed_index));
        try std.testing.expectEqual(want, prandom_u32_state(&state));
    }
}

test "random32 iteration vector matches Linux selftest" {
    var state = selftestSeed(931557656);
    var got: u32 = 0;
    for (0..959) |_| {
        got = prandom_u32_state(&state);
    }
    try std.testing.expectEqual(@as(u32, 2975593782), got);
}

test "random32 bytes are emitted little-endian" {
    var state = selftestSeed(1);
    const first = prandom_u32_state(&state);
    const second = prandom_u32_state(&state);

    state = selftestSeed(1);
    var bytes = [_]u8{ 0, 0, 0, 0, 0, 0 };
    prandom_bytes_state(&state, bytes[0..]);

    try std.testing.expectEqual(@as(u8, @truncate(first)), bytes[0]);
    try std.testing.expectEqual(@as(u8, @truncate(first >> 8)), bytes[1]);
    try std.testing.expectEqual(@as(u8, @truncate(first >> 16)), bytes[2]);
    try std.testing.expectEqual(@as(u8, @truncate(first >> 24)), bytes[3]);
    try std.testing.expectEqual(@as(u8, @truncate(second)), bytes[4]);
    try std.testing.expectEqual(@as(u8, @truncate(second >> 8)), bytes[5]);
}
