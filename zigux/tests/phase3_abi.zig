const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const atomic = @import("atomic_helpers");
const barrier = @import("barrier_helpers");
const mmio = @import("mmio_helpers");
const bitmap_view = @import("bitmap_view");
const cpumask_view = @import("cpumask_view");
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
        layout_assert.assertSize(abi.BitmapSummary, 16);
        layout_assert.assertSize(abi.CpuMaskSummary, 16);
        layout_assert.assertOffset(abi.BitmapSummary, "first_zero", 4);
        layout_assert.assertOffset(abi.CpuMaskSummary, "next_cpu", 4);
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

test "phase3 bitmap/cpumask interop helpers stay aligned with the ABI substrate" {
    var bitmap_words = [_]usize{
        (@as(usize, 1) << 1) | (@as(usize, 1) << 5) | (@as(usize, 1) << 63),
        (@as(usize, 1) << 4) | (@as(usize, 1) << 9),
    };
    const bitmap = bitmap_view.viewFromWords(bitmap_words[0..], bitmap_view.bits_per_long + 10);
    const bitmap_summary = bitmap_view.summarize(bitmap);

    try std.testing.expect(bitmap_view.isValid(bitmap));
    try std.testing.expectEqual(@as(u32, 1), bitmap_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), bitmap_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 5), bitmap_summary.weight);

    var cpumask_bits = [_]usize{(@as(usize, 1) << 0) | (@as(usize, 1) << 2) | (@as(usize, 1) << 6) | (@as(usize, 1) << 9)};
    const cpumask = cpumask_view.viewFromBits(cpumask_bits[0..], 12);
    const cpumask_summary = cpumask_view.summarize(cpumask);

    try std.testing.expect(cpumask_view.isValid(cpumask));
    try std.testing.expectEqual(@as(u32, 0), cpumask_summary.first_cpu);
    try std.testing.expectEqual(@as(u32, 2), cpumask_summary.next_cpu);
    try std.testing.expectEqual(@as(u32, 4), cpumask_summary.weight);
}
