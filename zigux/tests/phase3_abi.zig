const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const export_shim = @import("export_shim");
const narrow = @import("narrow_unsafe");
const uapi_version = @import("uapi_version");

test "phase3 abi slice uses stable canonical layouts" {
    comptime {
        layout_assert.assertSize(abi.BoundaryHeader, 8);
        layout_assert.assertSize(abi.ExportStatus, 8);
        layout_assert.assertSize(abi.InteropPolicy, 4);
        layout_assert.assertOffset(abi.BitmapView, "nbits", @sizeOf(usize));
        layout_assert.assertOffset(abi.BitmapView, "word_count", @sizeOf(usize) + 4);
        layout_assert.assertOffset(abi.CpuMaskView, "nr_cpu_ids", @sizeOf(usize));
        layout_assert.assertOffset(abi.MmioRange, "length", @sizeOf(usize));
    }
}

test "phase3 abi slice wires policies and exports" {
    try std.testing.expectEqual(abi.ABI_VERSION, uapi_version.abi_version);
    try std.testing.expect(panic_policy.canReturn(.warn));
    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));

    const status = export_shim.errno(-12, .kernel);
    try std.testing.expectEqual(@as(i32, -12), status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), status.flags);
}

test "phase3 abi slice wires atomic and mmio helpers" {
    var value: u32 = 3;
    try std.testing.expectEqual(@as(u32, 3), atomic.load(u32, &value, .seq_cst));
    atomic.store(u32, &value, 5, .seq_cst);
    try std.testing.expectEqual(@as(u32, 5), value);
    _ = atomic.exchange(u32, &value, 7, .seq_cst);
    try std.testing.expectEqual(@as(u32, 7), value);

    var regs = [_]u32{ 0, 0 };
    const base = narrow.addressOf(&regs[0]);
    mmio.write32(base, @sizeOf(u32), 0x12345678);
    try std.testing.expectEqual(@as(u32, 0x12345678), mmio.read32(base, @sizeOf(u32)));

    barrier.acquire();
    barrier.release();
    barrier.full();
}
