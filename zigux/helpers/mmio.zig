const std = @import("std");

pub fn read(comptime T: type, ptr: *volatile const T) T {
    return ptr.*;
}

pub fn write(comptime T: type, ptr: *volatile T, value: T) void {
    ptr.* = value;
}

pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {
    const before = read(T, @ptrCast(ptr));
    write(T, ptr, value);
    return before;
}

pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {
    const before = read(T, @ptrCast(ptr));
    const after = (before & ~clear_mask) | set_mask;
    write(T, ptr, after);
    return after;
}

test "phase3 mmio helper keeps volatile register reads and writes reviewable" {
    var register: u32 = 0x1234_5678;
    const register_ptr: *volatile u32 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u32, 0x1234_5678), read(u32, register_ptr));
    write(u32, register_ptr, 0xCAFE_BABE);
    try std.testing.expectEqual(@as(u32, 0xCAFE_BABE), register);
}

test "phase3 mmio helper keeps exchange-style register updates explicit" {
    var register: u16 = 0x1002;
    const register_ptr: *volatile u16 = @ptrCast(&register);

    try std.testing.expectEqual(@as(u16, 0x1002), exchange(u16, register_ptr, 0xBEEF));
    try std.testing.expectEqual(@as(u16, 0xBEEF), register);
}

test "phase3 mmio helper keeps masked register updates reviewable" {
    var register: u8 = 0b1011_0101;
    const register_ptr: *volatile u8 = @ptrCast(&register);

    try std.testing.expectEqual(
        @as(u8, 0b1001_0110),
        writeMasked(u8, register_ptr, 0b0011_0001, 0b0001_0010),
    );
    try std.testing.expectEqual(@as(u8, 0b1001_0110), register);
}
