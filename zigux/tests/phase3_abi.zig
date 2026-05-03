const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");
const rbtree = @import("rbtree_bindings");

test "phase3 abi slice uses stable canonical layouts" {
    comptime {
        layout_assert.assertBoundaryHeaderLayout();
        layout_assert.assertExportStatusLayout();
        layout_assert.assertInteropPolicyLayout();
        layout_assert.assertMmioRangeLayout();
        layout_assert.assertBitmapViewLayout();
        layout_assert.assertCpuMaskViewLayout();
        layout_assert.assertRbtreeRootViewLayout();
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
        layout_assert.assertSize(rbtree.RootView, @sizeOf(usize) * 2 + 8);
        layout_assert.assertAlign(rbtree.RootView, @alignOf(usize));
        layout_assert.assertOffset(rbtree.RootView, "root_addr", 0);
        layout_assert.assertOffset(rbtree.RootView, "leftmost_addr", @sizeOf(usize));
        layout_assert.assertOffset(rbtree.RootView, "flags", @sizeOf(usize) * 2);
        layout_assert.assertOffset(rbtree.RootView, "reserved", @sizeOf(usize) * 2 + 4);
    }
}

test "phase3 abi slice keeps explicit constants and statuses reviewable" {
    try std.testing.expectEqual(@as(u16, 1), abi.ABI_VERSION);
    try std.testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
    try std.testing.expectEqual(@as(u16, 1), @intFromEnum(abi.Facility.kernel));
    try std.testing.expectEqual(@as(u16, 2), @intFromEnum(abi.Facility.helpers));
    try std.testing.expectEqual(@as(u16, 3), @intFromEnum(abi.Facility.drivers));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(abi.PanicMode.abort));
    try std.testing.expectEqual(@as(u8, 1), @intFromEnum(abi.PanicMode.bug));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.PanicMode.warn));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(abi.AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, 1), @intFromEnum(abi.AllocatorMode.kernel_heap));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.AllocatorMode.arena));
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(abi.UnsafeScope.none));
    try std.testing.expectEqual(@as(u8, 1), @intFromEnum(abi.UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));
    try std.testing.expectEqual(@as(u32, 1), rbtree.ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), rbtree.ROOT_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 4), rbtree.ROOT_FLAG_LEFTMOST_VALID);

    const ok = export_shim.ok(.kernel);
    try std.testing.expect(export_shim.isOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.kernel)), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);

    const failure = export_shim.errno(-22, .helpers);
    try std.testing.expect(!export_shim.isOk(failure));
    try std.testing.expectEqual(@as(i32, -22), failure.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(abi.Facility.helpers)), failure.facility);
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

    // PHASE3_SHARED_RBTREE_SAMPLE_RECORD=cached-leftmost-root
    const cached_root: rbtree.RootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2000), cached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID), cached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), cached_root.reserved);
    try std.testing.expect(rbtree.isValid(cached_root));
    try std.testing.expect(!rbtree.isEmpty(cached_root));
    try std.testing.expect(rbtree.isCached(cached_root));
    try std.testing.expect(rbtree.hasLeftmost(cached_root));
}
