const std = @import("std");
const abi = @import("abi_bindings");
const mmio = @import("mmio_helper");

const expectEqual = std.testing.expectEqual;
const expectError = std.testing.expectError;

test "mmio range constructors gate policy bytes before exposing windows" {
    const valid = try mmio.rangeInteropPolicyBytes(
        0x1000,
        16,
        4,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
    );
    try expectEqual(@as(usize, 0x1000), valid.base_addr);
    try expectEqual(@as(u32, 16), valid.length);
    try expectEqual(@as(u32, 4), valid.stride);

    try expectError(error.UnsafeScopeDenied, mmio.rangeInteropPolicyBytes(
        0x1000,
        16,
        4,
        @intFromEnum(abi.UnsafeScope.none),
        0,
    ));
    try expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(0x1000, 16, 4, 99, 0));
    try expectError(error.InvalidInteropPolicy, mmio.rangeInteropPolicyBytes(
        0x1000,
        16,
        4,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        1,
    ));

    const empty_at_max = try mmio.rangeScoped(std.math.maxInt(usize), 0, 0, .volatile_mmio);
    try expectEqual(std.math.maxInt(usize), empty_at_max.base_addr);
    try expectError(error.InvalidInteropPolicy, mmio.rangeScoped(
        std.math.maxInt(usize),
        2,
        0,
        .volatile_mmio,
    ));
}

test "mmio typed pointers obey alignment stride bounds and address overflow" {
    const range = try mmio.rangeScoped(0x2000, 16, 4, .volatile_mmio);

    const word = try mmio.pointerAt(u32, range, 4);
    try expectEqual(@as(usize, 0x2004), @intFromPtr(word));

    const half = try mmio.constPointerAt(u16, range, 8);
    try expectEqual(@as(usize, 0x2008), @intFromPtr(half));

    _ = try mmio.pointerAt(u32, range, 12);
    try expectError(error.InvalidInteropPolicy, mmio.pointerAt(u32, range, 2));
    try expectError(error.InvalidInteropPolicy, mmio.pointerAt(u16, range, 6));
    try expectError(error.InvalidInteropPolicy, mmio.pointerAt(u32, range, 16));
    try expectError(error.InvalidInteropPolicy, mmio.pointerAt(u64, range, 12));

    const overflow = mmio.MmioRange{
        .base_addr = std.math.maxInt(usize),
        .length = 8,
        .stride = 0,
    };
    try expectError(error.InvalidInteropPolicy, mmio.pointerAt(u8, overflow, 1));
}

test "mmio policy byte gates protect volatile writes from invalid scopes" {
    var cell: u32 = 0x11223344;
    const ptr: *volatile u32 = @ptrCast(&cell);

    try mmio.writeInteropPolicyBytes(
        u32,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
        ptr,
        0x55667788,
    );
    try expectEqual(@as(u32, 0x55667788), cell);

    try expectError(error.UnsafeScopeDenied, mmio.writeInteropPolicyBytes(
        u32,
        @intFromEnum(abi.UnsafeScope.none),
        0,
        ptr,
        0xAABBCCDD,
    ));
    try expectEqual(@as(u32, 0x55667788), cell);

    try expectError(error.InvalidInteropPolicy, mmio.writeInteropPolicyBytes(
        u32,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        9,
        ptr,
        0xAABBCCDD,
    ));
    try expectEqual(@as(u32, 0x55667788), cell);

    const observed = try mmio.readInteropPolicyBytes(
        u32,
        @intFromEnum(abi.UnsafeScope.volatile_mmio),
        0,
        @ptrCast(ptr),
    );
    try expectEqual(@as(u32, 0x55667788), observed);
}

test "mmio range operations mutate only covered typed slots" {
    var cells = [_]u32{ 0x11111111, 0x22222222, 0x33333333, 0x44444444 };
    const range = try mmio.rangeScoped(@intFromPtr(&cells), @sizeOf(@TypeOf(cells)), 4, .volatile_mmio);

    try mmio.writeAt(u32, range, 4, 0xA5A5A5A5);
    try expectEqual(@as(u32, 0x11111111), cells[0]);
    try expectEqual(@as(u32, 0xA5A5A5A5), cells[1]);

    const before = try mmio.exchangeAt(u32, range, 8, 0x12345678);
    try expectEqual(@as(u32, 0x33333333), before);
    try expectEqual(@as(u32, 0x12345678), cells[2]);

    const masked = try mmio.writeMaskedAt(u32, range, 12, 0x00FFFF00, 0x0000AB00);
    try expectEqual(@as(u32, 0x4400AB44), masked);
    try expectEqual(@as(u32, 0x4400AB44), cells[3]);

    try expectError(error.InvalidInteropPolicy, mmio.writeAt(u32, range, 2, 0));
    try expectError(error.InvalidInteropPolicy, mmio.exchangeAt(u32, range, 16, 0));
    try expectEqual(@as(u32, 0x11111111), cells[0]);
    try expectEqual(@as(u32, 0xA5A5A5A5), cells[1]);
    try expectEqual(@as(u32, 0x12345678), cells[2]);
    try expectEqual(@as(u32, 0x4400AB44), cells[3]);
}
