// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub fn add(sum: u32, addend: u32) u32 {
    const result = sum +% addend;
    return result +% @as(u32, @intFromBool(result < addend));
}

pub fn sub(sum: u32, addend: u32) u32 {
    return add(sum, ~addend);
}

pub fn shift(sum: u32, offset: usize) u32 {
    return if ((offset & 1) != 0) (sum >> 8) | (sum << 24) else sum;
}

pub fn blockAdd(sum: u32, other: u32, offset: usize) u32 {
    return add(sum, shift(other, offset));
}

pub fn from32To16(sum: u32) u16 {
    const folded = sum +% ((sum >> 16) | (sum << 16));
    return @truncate(folded >> 16);
}

pub fn fold(sum: u32) u16 {
    return ~from32To16(sum);
}

pub fn unfold(sum: u16) u32 {
    return sum;
}

pub fn add16(sum: u16, addend: u16) u16 {
    const result = sum +% addend;
    return result +% @as(u16, @intFromBool(result < addend));
}

pub fn sub16(sum: u16, addend: u16) u16 {
    return add16(sum, ~addend);
}

pub fn replaceByDiff(sum: u16, diff: u32) u16 {
    return fold(add(diff, ~unfold(sum)));
}

pub fn replace4(sum: u16, from: u32, to: u32) u16 {
    const tmp = sub(~unfold(sum), from);
    return fold(add(tmp, to));
}

pub fn replace2(sum: u16, old: u16, new_value: u16) u16 {
    return ~add16(sub16(~sum, old), new_value);
}

pub fn replace(sum: u32, old: u32, new_value: u32) u32 {
    return add(sub(sum, old), new_value);
}

pub fn partial(bytes: []const u8, seed: u32) u32 {
    var acc: u64 = seed;
    var index: usize = 0;

    while (index + 1 < bytes.len) : (index += 2) {
        acc += (@as(u64, bytes[index]) << 8) | @as(u64, bytes[index + 1]);
    }

    if (index < bytes.len) {
        acc += @as(u64, bytes[index]) << 8;
    }

    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }

    return @intCast(acc);
}

pub fn compute(bytes: []const u8) u16 {
    return ~@as(u16, @truncate(partial(bytes, 0)));
}

pub fn tcpUdpNofold(sum: u32, saddr: u32, daddr: u32, len: u32, proto: u8) u32 {
    var acc = partial("", sum);
    acc = add(acc, saddr >> 16);
    acc = add(acc, saddr & 0xffff);
    acc = add(acc, daddr >> 16);
    acc = add(acc, daddr & 0xffff);
    acc = add(acc, proto);
    acc = add(acc, len);
    return partial("", acc);
}

pub fn tcpUdpV6Nofold(sum: u32, saddr: [16]u8, daddr: [16]u8, len: u32, proto: u8) u32 {
    var trailer = [_]u8{0} ** 8;
    writeBe32(trailer[0..4], len);
    trailer[7] = proto;

    var acc = partial(saddr[0..], sum);
    acc = partial(daddr[0..], acc);
    return partial(trailer[0..], acc);
}

fn writeBe32(out: []u8, value: u32) void {
    std.debug.assert(out.len == 4);
    out[0] = @as(u8, @truncate(value >> 24));
    out[1] = @as(u8, @truncate(value >> 16));
    out[2] = @as(u8, @truncate(value >> 8));
    out[3] = @as(u8, @truncate(value));
}
