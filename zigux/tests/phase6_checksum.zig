const std = @import("std");
const checksum = @import("checksum");

fn foldCarry(sum: u32) u32 {
    var acc = sum;
    while ((acc >> 16) != 0) {
        acc = (acc & 0xffff) + (acc >> 16);
    }
    return acc;
}

fn referenceInternetChecksum(bytes: []const u8) u16 {
    var acc: u32 = 0;
    var index: usize = 0;
    while (index + 1 < bytes.len) : (index += 2) {
        const pair: *const [2]u8 = @ptrCast(bytes[index .. index + 2]);
        acc += std.mem.readInt(u16, pair, .big);
    }
    if (index < bytes.len) {
        acc += @as(u16, bytes[index]) << 8;
    }
    return ~@as(u16, @truncate(foldCarry(acc)));
}

fn appendBigEndianU16(buffer: []u8, value: u16) void {
    const pair: *[2]u8 = @ptrCast(buffer[0..2]);
    std.mem.writeInt(u16, pair, value, .big);
}

fn appendBigEndianU32(buffer: []u8, value: u32) void {
    const pair: *[4]u8 = @ptrCast(buffer[0..4]);
    std.mem.writeInt(u32, pair, value, .big);
}

test "phase 6 checksum module imports cleanly" {
    _ = checksum;
}

test "compute matches the reference checksum on an IPv4 header" {
    const header = [_]u8{
        0x45, 0x00, 0x00, 0x3c,
        0x1c, 0x46, 0x40, 0x00,
        0x40, 0x06, 0x00, 0x00,
        0xc0, 0xa8, 0x00, 0x01,
        0xc0, 0xa8, 0x00, 0xc7,
    };

    const expected = referenceInternetChecksum(&header);
    try std.testing.expectEqual(expected, checksum.compute(&header));
}

test "partial sums compose across even and odd fragment boundaries" {
    const payload = "checksum fragments keep their carry";
    const whole = checksum.partial(payload, 0);

    const even_prefix = checksum.partial(payload[0..20], 0);
    const even_suffix = checksum.partial(payload[20..], 0);
    const even_combined = checksum.blockAdd(even_prefix, even_suffix, 20);
    try std.testing.expectEqual(whole, checksum.partial("", even_combined));

    const odd_prefix = checksum.partial(payload[0..21], 0);
    const odd_suffix = checksum.partial(payload[21..], 0);
    const odd_combined = checksum.blockAdd(odd_prefix, odd_suffix, 21);
    try std.testing.expectEqual(whole, checksum.partial("", odd_combined));
}

test "pseudo header accumulation matches the reference checksum" {
    const payload = "zigux checksum";
    const payload_partial = checksum.partial(payload, 0);
    const saddr = 0xc0a80001;
    const daddr = 0xc0a800c7;
    const proto: u8 = 17;

    var pseudo_header: [12]u8 = undefined;
    appendBigEndianU32(pseudo_header[0..4], saddr);
    appendBigEndianU32(pseudo_header[4..8], daddr);
    pseudo_header[8] = 0;
    pseudo_header[9] = proto;
    appendBigEndianU16(pseudo_header[10..12], payload.len);

    const pseudo_partial = checksum.partial(&pseudo_header, 0);
    const actual = checksum.fold(checksum.blockAdd(pseudo_partial, payload_partial, pseudo_header.len));

    var pseudo_and_payload: [12 + payload.len]u8 = undefined;
    @memcpy(pseudo_and_payload[0..12], &pseudo_header);
    @memcpy(pseudo_and_payload[12..], payload);

    const expected = referenceInternetChecksum(&pseudo_and_payload);
    try std.testing.expectEqual(expected, actual);
}
