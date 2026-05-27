const std = @import("std");
const mmio = @import("mmio");

pub fn exchange8InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    value: u8,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u8 {
    const before = try mmio.read8InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    try mmio.write8InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, reserved);
    return before;
}

pub fn exchange8InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    value: u8,
    unsafe_scope: u8,
) mmio.PolicyError!u8 {
    return exchange8InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn exchange16InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    value: u16,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u16 {
    const before = try mmio.read16InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    try mmio.write16InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, reserved);
    return before;
}

pub fn exchange16InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    value: u16,
    unsafe_scope: u8,
) mmio.PolicyError!u16 {
    return exchange16InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn exchange32InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    value: u32,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u32 {
    const before = try mmio.read32InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    try mmio.write32InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, reserved);
    return before;
}

pub fn exchange32InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    value: u32,
    unsafe_scope: u8,
) mmio.PolicyError!u32 {
    return exchange32InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn exchange64InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    value: u64,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u64 {
    const before = try mmio.read64InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    try mmio.write64InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, reserved);
    return before;
}

pub fn exchange64InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    value: u64,
    unsafe_scope: u8,
) mmio.PolicyError!u64 {
    return exchange64InteropPolicyBytes(base_addr, byte_offset, value, unsafe_scope, 0);
}

pub fn writeMasked8InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u8,
    set_mask: u8,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u8 {
    const before = try mmio.read8InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    const after = (before & ~clear_mask) | set_mask;
    try mmio.write8InteropPolicyBytes(base_addr, byte_offset, after, unsafe_scope, reserved);
    return after;
}

pub fn writeMasked8InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u8,
    set_mask: u8,
    unsafe_scope: u8,
) mmio.PolicyError!u8 {
    return writeMasked8InteropPolicyBytes(base_addr, byte_offset, clear_mask, set_mask, unsafe_scope, 0);
}

pub fn writeMasked16InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u16,
    set_mask: u16,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u16 {
    const before = try mmio.read16InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    const after = (before & ~clear_mask) | set_mask;
    try mmio.write16InteropPolicyBytes(base_addr, byte_offset, after, unsafe_scope, reserved);
    return after;
}

pub fn writeMasked16InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u16,
    set_mask: u16,
    unsafe_scope: u8,
) mmio.PolicyError!u16 {
    return writeMasked16InteropPolicyBytes(base_addr, byte_offset, clear_mask, set_mask, unsafe_scope, 0);
}

pub fn writeMasked32InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u32,
    set_mask: u32,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u32 {
    const before = try mmio.read32InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    const after = (before & ~clear_mask) | set_mask;
    try mmio.write32InteropPolicyBytes(base_addr, byte_offset, after, unsafe_scope, reserved);
    return after;
}

pub fn writeMasked32InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u32,
    set_mask: u32,
    unsafe_scope: u8,
) mmio.PolicyError!u32 {
    return writeMasked32InteropPolicyBytes(base_addr, byte_offset, clear_mask, set_mask, unsafe_scope, 0);
}

pub fn writeMasked64InteropPolicyBytes(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u64,
    set_mask: u64,
    unsafe_scope: u8,
    reserved: u8,
) mmio.PolicyError!u64 {
    const before = try mmio.read64InteropPolicyBytes(base_addr, byte_offset, unsafe_scope, reserved);
    const after = (before & ~clear_mask) | set_mask;
    try mmio.write64InteropPolicyBytes(base_addr, byte_offset, after, unsafe_scope, reserved);
    return after;
}

pub fn writeMasked64InteropPolicyByte(
    base_addr: usize,
    byte_offset: usize,
    clear_mask: u64,
    set_mask: u64,
    unsafe_scope: u8,
) mmio.PolicyError!u64 {
    return writeMasked64InteropPolicyBytes(base_addr, byte_offset, clear_mask, set_mask, unsafe_scope, 0);
}

test "mmio width helper keeps exchange aliases explicit across register widths" {
    var words = [_]u64{0} ** 3;
    const bytes: [*]u8 = @ptrCast(&words[0]);
    const base_addr = @intFromPtr(&bytes[0]);

    try mmio.write8InteropPolicyByte(base_addr, 0, 0x31, 1);
    try std.testing.expectEqual(@as(u8, 0x31), try exchange8InteropPolicyByte(base_addr, 0, 0x44, 1));
    try std.testing.expectEqual(@as(u8, 0x44), try mmio.read8InteropPolicyBytes(base_addr, 0, 1, 0));

    try mmio.write16InteropPolicyBytes(base_addr, 2, 0xABCD, 1, 0);
    try std.testing.expectEqual(@as(u16, 0xABCD), try exchange16InteropPolicyBytes(base_addr, 2, 0x1357, 1, 0));
    try std.testing.expectEqual(@as(u16, 0x1357), try mmio.read16InteropPolicyBytes(base_addr, 2, 1, 0));

    try mmio.write32InteropPolicyBytes(base_addr, 4, 0xCAFE_BABE, 1, 0);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), try exchange32InteropPolicyByte(base_addr, 4, 0x0BAD_F00D, 1));
    try std.testing.expectEqual(@as(u32, 0x0BAD_F00D), try mmio.read32InteropPolicyBytes(base_addr, 4, 1, 0));

    try mmio.write64InteropPolicyBytes(base_addr, 8, 0x0123_4567_89AB_CDEF, 1, 0);
    try std.testing.expectEqual(
        @as(u64, 0x0123_4567_89AB_CDEF),
        try exchange64InteropPolicyBytes(base_addr, 8, 0x0FED_CBA9_8765_4321, 1, 0),
    );
    try std.testing.expectEqual(
        @as(u64, 0x0FED_CBA9_8765_4321),
        try mmio.read64InteropPolicyBytes(base_addr, 8, 1, 0),
    );
}

test "mmio width helper keeps masked aliases explicit across register widths" {
    var words = [_]u64{0} ** 3;
    const bytes: [*]u8 = @ptrCast(&words[0]);
    const base_addr = @intFromPtr(&bytes[0]);

    try mmio.write8InteropPolicyBytes(base_addr, 0, 0b1011_0101, 1, 0);
    try std.testing.expectEqual(
        @as(u8, 0b1001_0110),
        try writeMasked8InteropPolicyByte(base_addr, 0, 0b0011_0001, 0b0001_0010, 1),
    );

    try mmio.write16InteropPolicyBytes(base_addr, 2, 0x0FF0, 1, 0);
    try std.testing.expectEqual(
        @as(u16, 0x0F05),
        try writeMasked16InteropPolicyBytes(base_addr, 2, 0x00F0, 0x0005, 1, 0),
    );

    try mmio.write32InteropPolicyBytes(base_addr, 4, 0xCAFE_BABE, 1, 0);
    try std.testing.expectEqual(
        @as(u32, 0xCA0E_B00E),
        try writeMasked32InteropPolicyByte(base_addr, 4, 0x00F0_0FF0, 0x000E_000E, 1),
    );

    try mmio.write64InteropPolicyBytes(base_addr, 8, 0x1234_5678_9ABC_DEF0, 1, 0);
    try std.testing.expectEqual(
        @as(u64, 0x1255_5678_9A11_DEA0),
        try writeMasked64InteropPolicyBytes(
            base_addr,
            8,
            0x00FF_0000_00FF_00F0,
            0x0055_0000_0011_00A0,
            1,
            0,
        ),
    );
}

test "mmio width helper preserves policy denials and reserved-byte failures" {
    var words = [_]u64{0} ** 2;
    const bytes: [*]u8 = @ptrCast(&words[0]);
    const base_addr = @intFromPtr(&bytes[0]);

    try std.testing.expectError(error.UnsafeScopeDenied, exchange8InteropPolicyByte(base_addr, 0, 0x11, 0));
    try std.testing.expectError(error.UnsafeScopeDenied, exchange16InteropPolicyBytes(base_addr, 2, 0x2222, 2, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, exchange32InteropPolicyBytes(base_addr, 4, 0x3333_3333, 1, 1));
    try std.testing.expectError(error.UnsafeScopeDenied, writeMasked64InteropPolicyByte(base_addr, 8, 0xFFFF_0000_0000_0000, 0, 0));
    try std.testing.expectError(error.InvalidInteropPolicy, writeMasked16InteropPolicyBytes(base_addr, 2, 0x00F0, 0x0005, 1, 1));
}
