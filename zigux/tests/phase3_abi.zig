const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

test "phase3 abi slice uses stable canonical layouts" {
    comptime {
        layout_assert.assertBoundaryHeaderLayout();
        layout_assert.assertExportStatusLayout();
        layout_assert.assertInteropPolicyLayout();
        layout_assert.assertMmioRangeLayout();
        layout_assert.assertBitmapViewLayout();
        layout_assert.assertCpuMaskViewLayout();
        layout_assert.assertSize(abi.MmioRange, @sizeOf(usize) + 8);
        layout_assert.assertAlign(abi.MmioRange, @alignOf(usize));
        layout_assert.assertOffset(abi.MmioRange, "base_addr", 0);
        layout_assert.assertOffset(abi.MmioRange, "length", @sizeOf(usize));
        layout_assert.assertOffset(abi.MmioRange, "stride", @sizeOf(usize) + 4);
        layout_assert.assertSize(abi.BitmapView, @sizeOf(usize) + 8);
        layout_assert.assertAlign(abi.BitmapView, @alignOf(usize));
        layout_assert.assertOffset(abi.BitmapView, "words_addr", 0);
        layout_assert.assertOffset(abi.BitmapView, "nbits", @sizeOf(usize));
        layout_assert.assertOffset(abi.BitmapView, "word_count", @sizeOf(usize) + 4);
        layout_assert.assertSize(abi.CpuMaskView, @sizeOf(usize) + 8);
        layout_assert.assertAlign(abi.CpuMaskView, @alignOf(usize));
        layout_assert.assertOffset(abi.CpuMaskView, "bits_addr", 0);
        layout_assert.assertOffset(abi.CpuMaskView, "nr_cpu_ids", @sizeOf(usize));
        layout_assert.assertOffset(abi.CpuMaskView, "reserved", @sizeOf(usize) + 4);
    }
}

test "phase3 abi slice keeps explicit constants and statuses reviewable" {
    try std.testing.expectEqual(@as(u16, 1), abi.ABI_VERSION);
    try std.testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
    try std.testing.expectEqual(@as(u16, 1), @intFromEnum(abi.Facility.kernel));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(abi.PanicMode.abort));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(abi.AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));
    try std.testing.expectEqual(@as(u32, 6), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED);
    try std.testing.expectEqual(@as(u32, 5), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED);
    try std.testing.expectEqual(@as(u32, 1), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED);
    try std.testing.expectEqual(@as(u32, 6), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED);
    try std.testing.expectEqual(@as(u32, 5), abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED);

    const ok = export_shim.ok(.kernel);
    try std.testing.expect(export_shim.isOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);

    const failure = export_shim.errno(-22, .kernel);
    try std.testing.expect(!export_shim.isOk(failure));
    try std.testing.expectEqual(@as(i32, -22), failure.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), failure.flags);
}

test "phase3 abi slice keeps the boundary helpers constructible" {
    const header = export_shim.header(0x44);
    try std.testing.expectEqual(header, uapi_version.boundaryHeader(0x44));
    try std.testing.expect(export_shim.isCanonicalHeader(header));
    try std.testing.expect(uapi_version.isCanonical(header));

    const compatible: abi.BoundaryHeader = .{
        .size = @sizeOf(abi.BoundaryHeader) + 8,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x44,
    };
    try std.testing.expect(export_shim.isCompatibleHeader(compatible));
    try std.testing.expect(uapi_version.isCompatible(compatible));

    try std.testing.expectEqual(panic_policy.Action.abort_now, panic_policy.actionFor(.abort));
    try std.testing.expect(allocator_policy.requiresExplicitCaller(.caller_provided));

    try std.testing.expectEqual(abi.PanicMode.warn, panic_policy.modeFromInteropPolicyByte(@intFromEnum(abi.PanicMode.warn)).?);
    try std.testing.expectEqual(abi.AllocatorMode.kernel_heap, allocator_policy.modeFromInteropPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)).?);
    try std.testing.expect(panic_policy.canReturnPolicyByte(@intFromEnum(abi.PanicMode.warn)));
    try std.testing.expect(allocator_policy.permitsGlobalFallbackPolicyByte(@intFromEnum(abi.AllocatorMode.kernel_heap)));

    const range = mmio.range(0x1000, 0x40, 4);
    try std.testing.expectEqual(@as(usize, 0x1000), range.base_addr);
    try std.testing.expectEqual(@as(u32, 0x40), range.length);
    try std.testing.expectEqual(@as(u32, 4), range.stride);

    try std.testing.expectEqual(narrow.UnsafeScopeTag.raw_pointer_bridge, narrow.scopeFromInteropPolicyBytes(2, 0).?);
    try std.testing.expect(narrow.permitsRawPointerBridgePolicyBytes(2, 0));
    try std.testing.expect(!narrow.permitsVolatileMmioPolicyBytes(2, 0));
}
