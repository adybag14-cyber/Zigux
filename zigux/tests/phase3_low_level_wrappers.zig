const std = @import("std");
const abi = @import("abi_bindings");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const export_shim = @import("export_shim");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");
const uapi_version = @import("uapi_version");

test "phase3 low-level wrappers stay inside the documented ABI surface" {
    var value: u32 = 5;
    try std.testing.expectEqual(@as(u32, 5), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 8, .seq_cst);
    try std.testing.expectEqual(@as(u32, 8), value);
    try std.testing.expectEqual(@as(u32, 8), atomic.exchange(u32, &value, 13, .seq_cst));
    try std.testing.expectEqual(@as(u32, 13), value);
    try std.testing.expectEqual(@as(u32, 13), atomic.fetchAdd(u32, &value, 2, .seq_cst));
    try std.testing.expectEqual(@as(u32, 15), value);
    try std.testing.expectEqual(@as(?u32, null), atomic.compareExchange(u32, &value, 15, 21, .seq_cst, .seq_cst));
    try std.testing.expectEqual(@as(u32, 21), value);

    barrier.acquire();
    barrier.release();
    barrier.full();

    var regs = [_]u32{ 0, 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    const desc = mmio.range(base, 12, 4);
    try std.testing.expectEqual(base, desc.base_addr);
    try std.testing.expectEqual(@as(u32, 12), desc.length);
    try std.testing.expectEqual(@as(u32, 4), desc.stride);
    mmio.write32(base, 8, 0x12345678);
    try std.testing.expectEqual(@as(u32, 0x12345678), mmio.read32(base, 8));
    try std.testing.expectEqual(@as(u32, 0x12345678), regs[2]);
}

test "phase3 low-level wrapper ABI range shape stays stable" {
    comptime {
        if (@sizeOf(abi.MmioRange) != @sizeOf(usize) + 8) {
            @compileError("MmioRange size drifted");
        }
        if (@offsetOf(abi.MmioRange, "length") != @sizeOf(usize)) {
            @compileError("MmioRange.length offset drifted");
        }
        if (@offsetOf(abi.MmioRange, "stride") != @sizeOf(usize) + 4) {
            @compileError("MmioRange.stride offset drifted");
        }
    }
}

test "phase3 low-level wrappers keep the narrow unsafe scope contract explicit" {
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.none), @intFromEnum(narrow.UnsafeScopeTag.none));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.volatile_mmio), @intFromEnum(narrow.UnsafeScopeTag.volatile_mmio));
    try std.testing.expectEqual(@intFromEnum(abi.UnsafeScope.raw_pointer_bridge), @intFromEnum(narrow.UnsafeScopeTag.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsVolatileMmio(.none));
    try std.testing.expect(narrow.permitsVolatileMmio(.volatile_mmio));
    try std.testing.expect(!narrow.permitsVolatileMmio(.raw_pointer_bridge));

    try std.testing.expect(!narrow.permitsRawPointerBridge(.none));
    try std.testing.expect(!narrow.permitsRawPointerBridge(.volatile_mmio));
    try std.testing.expect(narrow.permitsRawPointerBridge(.raw_pointer_bridge));
}

test "phase3 focused boundary gate keeps export shim status encoding explicit" {
    const success = export_shim.ok(.kernel);
    try std.testing.expect(export_shim.isOk(success));
    try std.testing.expectEqual(@as(i32, 0), success.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), success.facility);
    try std.testing.expectEqual(@as(u16, 0), success.flags);

    const failure = export_shim.errno(-22, .helpers);
    try std.testing.expect(!export_shim.isOk(failure));
    try std.testing.expectEqual(@as(i32, -22), failure.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), failure.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), failure.flags);
}

test "phase3 focused boundary gate keeps UAPI version pinned to the ABI version" {
    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
}
