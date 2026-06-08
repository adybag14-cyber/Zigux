// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn check_signature(io_addr: []const u8, signature: []const u8, length: isize) i32 {
    if (length < 0) return 0;

    const len: usize = @intCast(length);
    if (len > io_addr.len or len > signature.len) return 0;

    var idx: usize = 0;
    while (idx < len) : (idx += 1) {
        if (io_addr[idx] != signature[idx]) return 0;
    }
    return 1;
}

pub fn checkSignature(io_addr: []const u8, signature: []const u8) bool {
    return check_signature(io_addr, signature, @intCast(signature.len)) != 0;
}

test "check signature returns one for matching bytes" {
    const mmio = [_]u8{ 0x55, 0xaa, 0x12, 0x34 };
    const sig = [_]u8{ 0x55, 0xaa, 0x12, 0x34 };

    try std.testing.expectEqual(@as(i32, 1), check_signature(&mmio, &sig, sig.len));
    try std.testing.expect(checkSignature(&mmio, &sig));
}

test "check signature returns zero at first mismatch" {
    const mmio = [_]u8{ 0x55, 0xaa, 0x12, 0x34 };
    const sig = [_]u8{ 0x55, 0xaa, 0xff, 0x34 };

    try std.testing.expectEqual(@as(i32, 0), check_signature(&mmio, &sig, sig.len));
}

test "check signature handles zero invalid and shortened lengths" {
    const mmio = [_]u8{ 1, 2, 3 };
    const sig = [_]u8{ 1, 2, 4 };

    try std.testing.expectEqual(@as(i32, 1), check_signature(&mmio, &sig, 0));
    try std.testing.expectEqual(@as(i32, 1), check_signature(&mmio, &sig, 2));
    try std.testing.expectEqual(@as(i32, 0), check_signature(&mmio, &sig, -1));
    try std.testing.expectEqual(@as(i32, 0), check_signature(mmio[0..2], &sig, 3));
}
