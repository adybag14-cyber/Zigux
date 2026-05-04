const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");
const export_shim = @import("export_shim");
const uapi_version = @import("uapi_version");
const panic_policy = @import("panic_policy");
const allocator_policy = @import("allocator_policy");
const mmio = @import("mmio_helpers");
const narrow = @import("narrow_unsafe");

fn rbtreeKnownFlagMask() u32 {
    return abi.RBTREE_ROOT_FLAG_EMPTY |
        abi.RBTREE_ROOT_FLAG_CACHED |
        abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID;
}

fn isRbtreeEmpty(view: abi.RbtreeRootView) bool {
    return (view.flags & abi.RBTREE_ROOT_FLAG_EMPTY) != 0;
}

fn isRbtreeCached(view: abi.RbtreeRootView) bool {
    return (view.flags & abi.RBTREE_ROOT_FLAG_CACHED) != 0;
}

fn hasRbtreeLeftmost(view: abi.RbtreeRootView) bool {
    return (view.flags & abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID) != 0;
}

fn hasOnlyKnownRbtreeFlags(view: abi.RbtreeRootView) bool {
    return (view.flags & ~rbtreeKnownFlagMask()) == 0;
}

fn hasRbtreeRoot(view: abi.RbtreeRootView) bool {
    return !isRbtreeEmpty(view) and view.root_addr != 0;
}

fn isValidRbtreeRootView(view: abi.RbtreeRootView) bool {
    if (!hasOnlyKnownRbtreeFlags(view)) return false;
    if (view.reserved != 0) return false;
    if (isRbtreeEmpty(view) and view.root_addr != 0) return false;
    if (!isRbtreeCached(view) and view.leftmost_addr != 0) return false;
    if (!hasRbtreeLeftmost(view) and view.leftmost_addr != 0) return false;
    return true;
}

fn canonicalizeRbtreeRootView(view: abi.RbtreeRootView) ?abi.RbtreeRootView {
    if (!isValidRbtreeRootView(view)) return null;
    if (isRbtreeEmpty(view)) {
        return .{
            .root_addr = 0,
            .leftmost_addr = 0,
            .flags = abi.RBTREE_ROOT_FLAG_EMPTY,
            .reserved = 0,
        };
    }
    if (isRbtreeCached(view)) {
        return .{
            .root_addr = view.root_addr,
            .leftmost_addr = view.leftmost_addr,
            .flags = abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID,
            .reserved = 0,
        };
    }
    return .{
        .root_addr = view.root_addr,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
}

fn isCanonicalRbtreeRootView(view: abi.RbtreeRootView) bool {
    const normalized = canonicalizeRbtreeRootView(view) orelse return false;
    return std.meta.eql(normalized, view);
}

test "phase3 abi slice uses stable canonical layouts" {
    comptime {
        layout_assert.assertBoundaryHeaderLayout();
        layout_assert.assertExportStatusLayout();
        layout_assert.assertInteropPolicyLayout();
        layout_assert.assertMmioRangeLayout();
        layout_assert.assertBitmapViewLayout();
        layout_assert.assertCpuMaskViewLayout();
        layout_assert.assertListHeadRefLayout();
        layout_assert.assertListViewLayout();
        layout_assert.assertListSummaryLayout();
        layout_assert.assertHListHeadRefLayout();
        layout_assert.assertHListNodeRefLayout();
        layout_assert.assertHListViewLayout();
        layout_assert.assertHListSummaryLayout();
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
        layout_assert.assertSize(abi.ListHeadRef, @sizeOf(usize) * 2);
        layout_assert.assertAlign(abi.ListHeadRef, @alignOf(usize));
        layout_assert.assertOffset(abi.ListHeadRef, "next_addr", 0);
        layout_assert.assertOffset(abi.ListHeadRef, "prev_addr", @sizeOf(usize));
        layout_assert.assertSize(abi.ListView, @sizeOf(usize) + 8);
        layout_assert.assertAlign(abi.ListView, @alignOf(usize));
        layout_assert.assertOffset(abi.ListView, "head_addr", 0);
        layout_assert.assertOffset(abi.ListView, "max_nodes", @sizeOf(usize));
        layout_assert.assertOffset(abi.ListView, "reserved", @sizeOf(usize) + 4);
        layout_assert.assertSize(abi.ListSummary, 8);
        layout_assert.assertAlign(abi.ListSummary, 4);
        layout_assert.assertOffset(abi.ListSummary, "length", 0);
        layout_assert.assertOffset(abi.ListSummary, "flags", 4);
        layout_assert.assertSize(abi.HListHeadRef, @sizeOf(usize));
        layout_assert.assertAlign(abi.HListHeadRef, @alignOf(usize));
        layout_assert.assertOffset(abi.HListHeadRef, "first_addr", 0);
        layout_assert.assertSize(abi.HListNodeRef, @sizeOf(usize) * 2);
        layout_assert.assertAlign(abi.HListNodeRef, @alignOf(usize));
        layout_assert.assertOffset(abi.HListNodeRef, "next_addr", 0);
        layout_assert.assertOffset(abi.HListNodeRef, "pprev_addr", @sizeOf(usize));
        layout_assert.assertSize(abi.HListView, @sizeOf(usize) + 8);
        layout_assert.assertAlign(abi.HListView, @alignOf(usize));
        layout_assert.assertOffset(abi.HListView, "head_addr", 0);
        layout_assert.assertOffset(abi.HListView, "max_nodes", @sizeOf(usize));
        layout_assert.assertOffset(abi.HListView, "reserved", @sizeOf(usize) + 4);
        layout_assert.assertSize(abi.HListSummary, 8);
        layout_assert.assertAlign(abi.HListSummary, 4);
        layout_assert.assertOffset(abi.HListSummary, "length", 0);
        layout_assert.assertOffset(abi.HListSummary, "flags", 4);
        layout_assert.assertSize(abi.RbtreeRootView, @sizeOf(usize) * 2 + 8);
        layout_assert.assertAlign(abi.RbtreeRootView, @alignOf(usize));
        layout_assert.assertOffset(abi.RbtreeRootView, "root_addr", 0);
        layout_assert.assertOffset(abi.RbtreeRootView, "leftmost_addr", @sizeOf(usize));
        layout_assert.assertOffset(abi.RbtreeRootView, "flags", @sizeOf(usize) * 2);
        layout_assert.assertOffset(abi.RbtreeRootView, "reserved", @sizeOf(usize) * 2 + 4);
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
    try std.testing.expectEqual(@as(u32, 1), abi.LIST_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), abi.LIST_FLAG_SINGULAR);
    try std.testing.expectEqual(@as(u32, 4), abi.LIST_FLAG_CIRCULAR);
    try std.testing.expectEqual(@as(u32, 8), abi.LIST_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), abi.HLIST_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), abi.HLIST_FLAG_SINGULAR);
    try std.testing.expectEqual(@as(u32, 4), abi.HLIST_FLAG_TERMINATED);
    try std.testing.expectEqual(@as(u32, 8), abi.HLIST_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 1), abi.MINOR_ALLOC_FLAG_TRUNCATED);
    try std.testing.expectEqual(@as(u32, 2), abi.MINOR_ALLOC_FLAG_FOUND);
    try std.testing.expectEqual(@as(u32, 4), abi.MINOR_ALLOC_FLAG_EXHAUSTED);
    try std.testing.expectEqual(@as(u32, 1), abi.RBTREE_ROOT_FLAG_EMPTY);
    try std.testing.expectEqual(@as(u32, 2), abi.RBTREE_ROOT_FLAG_CACHED);
    try std.testing.expectEqual(@as(u32, 4), abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID);

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

    // PHASE3_SHARED_RBTREE_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root
    const empty_root: abi.RbtreeRootView = .{
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = abi.RBTREE_ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0), empty_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), empty_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_EMPTY), empty_root.flags);
    try std.testing.expectEqual(@as(u32, 0), empty_root.reserved);
    try std.testing.expect(isValidRbtreeRootView(empty_root));
    try std.testing.expect(isRbtreeEmpty(empty_root));
    try std.testing.expect(!isRbtreeCached(empty_root));
    try std.testing.expect(!hasRbtreeLeftmost(empty_root));
    try std.testing.expect(!hasRbtreeRoot(empty_root));
    try std.testing.expect(isCanonicalRbtreeRootView(empty_root));

    const cached_root: abi.RbtreeRootView = .{
        .root_addr = 0x2000,
        .leftmost_addr = 0x1800,
        .flags = abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2000), cached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, abi.RBTREE_ROOT_FLAG_CACHED | abi.RBTREE_ROOT_FLAG_LEFTMOST_VALID), cached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), cached_root.reserved);
    try std.testing.expect(isValidRbtreeRootView(cached_root));
    try std.testing.expect(!isRbtreeEmpty(cached_root));
    try std.testing.expect(isRbtreeCached(cached_root));
    try std.testing.expect(hasRbtreeLeftmost(cached_root));
    try std.testing.expect(hasRbtreeRoot(cached_root));
    try std.testing.expect(isCanonicalRbtreeRootView(cached_root));

    const uncached_root: abi.RbtreeRootView = .{
        .root_addr = 0x2400,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
    try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);
    try std.testing.expectEqual(@as(usize, 0), uncached_root.leftmost_addr);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);
    try std.testing.expectEqual(@as(u32, 0), uncached_root.reserved);
    try std.testing.expect(isValidRbtreeRootView(uncached_root));
    try std.testing.expect(!isRbtreeEmpty(uncached_root));
    try std.testing.expect(!isRbtreeCached(uncached_root));
    try std.testing.expect(!hasRbtreeLeftmost(uncached_root));
    try std.testing.expect(hasRbtreeRoot(uncached_root));
    try std.testing.expect(isCanonicalRbtreeRootView(uncached_root));
}
