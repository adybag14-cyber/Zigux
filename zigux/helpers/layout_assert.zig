const std = @import("std");
const abi = @import("abi_bindings");

pub const LayoutError = error{
    SizeMismatch,
    AlignMismatch,
    OffsetMismatch,
};

pub const MmioRange = extern struct {
    base_addr: usize,
    length: u32,
    stride: u32,
};

pub const RbtreeRootView = abi.RbtreeRootView;

pub fn expectSize(comptime T: type, expected: usize) LayoutError!void {
    if (@sizeOf(T) != expected) return error.SizeMismatch;
}

pub fn expectAlign(comptime T: type, expected: usize) LayoutError!void {
    if (@alignOf(T) != expected) return error.AlignMismatch;
}

pub fn expectOffset(comptime T: type, comptime field_name: []const u8, expected: usize) LayoutError!void {
    if (@offsetOf(T, field_name) != expected) return error.OffsetMismatch;
}

pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {
    try expectSize(T, size);
    try expectAlign(T, alignment);
}

pub fn expectFieldLayout(
    comptime T: type,
    comptime field_name: []const u8,
    expected_offset: usize,
) LayoutError!void {
    try expectOffset(T, field_name, expected_offset);
}

fn expectComptimeByteValue(
    comptime actual: comptime_int,
    comptime expected: comptime_int,
    comptime label: []const u8,
) void {
    if (actual != expected) {
        @compileError(label);
    }
}

pub fn assertBoundaryHeaderLayout() LayoutError!void {
    try expectLayout(abi.BoundaryHeader, 8, 4);
    try expectFieldLayout(abi.BoundaryHeader, "size", 0);
    try expectFieldLayout(abi.BoundaryHeader, "abi_version", 4);
    try expectFieldLayout(abi.BoundaryHeader, "flags", 6);
}

pub fn assertExportStatusLayout() LayoutError!void {
    try expectLayout(abi.ExportStatus, 8, 4);
    try expectFieldLayout(abi.ExportStatus, "code", 0);
    try expectFieldLayout(abi.ExportStatus, "facility", 4);
    try expectFieldLayout(abi.ExportStatus, "flags", 6);
}

pub fn assertInteropPolicyEnumLayouts() LayoutError!void {
    try expectLayout(abi.PanicMode, 1, 1);
    try expectLayout(abi.AllocatorMode, 1, 1);
    try expectLayout(abi.UnsafeScope, 1, 1);
}

pub fn assertInteropPolicyLayout() LayoutError!void {
    try assertInteropPolicyEnumLayouts();
    assertInteropPolicyModeValues();
    try expectLayout(abi.InteropPolicy, 4, 1);
    try expectFieldLayout(abi.InteropPolicy, "panic_mode", 0);
    try expectFieldLayout(abi.InteropPolicy, "allocator_mode", 1);
    try expectFieldLayout(abi.InteropPolicy, "unsafe_scope", 2);
    try expectFieldLayout(abi.InteropPolicy, "reserved", 3);
}

pub fn assertMmioRangeLayout() LayoutError!void {
    const raw_size = @sizeOf(usize) + @sizeOf(u32) * 2;
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(MmioRange));

    try expectLayout(MmioRange, expected_size, @alignOf(usize));
    try expectFieldLayout(MmioRange, "base_addr", 0);
    try expectFieldLayout(MmioRange, "length", @sizeOf(usize));
    try expectFieldLayout(MmioRange, "stride", @sizeOf(usize) + @sizeOf(u32));
}

pub fn assertRbtreeRootViewLayout() LayoutError!void {
    try expectLayout(RbtreeRootView, abi.rbtree_root_view_size, abi.rbtree_root_view_align);
    try expectFieldLayout(RbtreeRootView, "root", abi.rbtree_root_view_root_offset);
    try expectFieldLayout(
        RbtreeRootView,
        "cached_leftmost",
        abi.rbtree_root_view_cached_leftmost_offset,
    );
    try expectFieldLayout(RbtreeRootView, "flags", abi.rbtree_root_view_flags_offset);
}

pub fn assertNotifierBlockLayout() LayoutError!void {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(abi.NotifierBlock));

    try expectLayout(abi.NotifierBlock, expected_size, @alignOf(usize));
    try expectFieldLayout(abi.NotifierBlock, "notifier_call", 0);
    try expectFieldLayout(abi.NotifierBlock, "next", @sizeOf(usize));
    try expectFieldLayout(abi.NotifierBlock, "priority", @sizeOf(usize) * 2);
}

pub fn assertNotifierChainPriorityIncreaseLayout() LayoutError!void {
    try expectLayout(
        abi.ChainPriorityIncrease,
        @sizeOf(usize) * 2 + @sizeOf(i32) * 2,
        @alignOf(usize),
    );
    try expectFieldLayout(abi.ChainPriorityIncrease, "previous_index", 0);
    try expectFieldLayout(abi.ChainPriorityIncrease, "current_index", @sizeOf(usize));
    try expectFieldLayout(abi.ChainPriorityIncrease, "previous_priority", @sizeOf(usize) * 2);
    try expectFieldLayout(
        abi.ChainPriorityIncrease,
        "current_priority",
        @sizeOf(usize) * 2 + @sizeOf(i32),
    );
}

pub fn assertListHeadLayout() LayoutError!void {
    try expectLayout(abi.ListHead, @sizeOf(usize) * 2, @alignOf(usize));
    try expectFieldLayout(abi.ListHead, "next", 0);
    try expectFieldLayout(abi.ListHead, "prev", @sizeOf(usize));
}

pub fn assertHListHeadLayout() LayoutError!void {
    try expectLayout(abi.HListHead, @sizeOf(usize), @alignOf(usize));
    try expectFieldLayout(abi.HListHead, "first", 0);
}

pub fn assertHListNodeLayout() LayoutError!void {
    try expectLayout(abi.HListNode, @sizeOf(usize) * 2, @alignOf(usize));
    try expectFieldLayout(abi.HListNode, "next", 0);
    try expectFieldLayout(abi.HListNode, "pprev", @sizeOf(usize));
}

pub fn assertListBackLinkBreakLayout() LayoutError!void {
    try expectLayout(abi.ListBackLinkBreak, @sizeOf(usize) * 3, @alignOf(usize));
    try expectFieldLayout(abi.ListBackLinkBreak, "current_index", 0);
    try expectFieldLayout(abi.ListBackLinkBreak, "expected_prev", @sizeOf(usize));
    try expectFieldLayout(abi.ListBackLinkBreak, "actual_prev", @sizeOf(usize) * 2);
}

pub fn assertHListPrevLinkBreakLayout() LayoutError!void {
    try expectLayout(abi.HListPrevLinkBreak, @sizeOf(usize) * 3, @alignOf(usize));
    try expectFieldLayout(abi.HListPrevLinkBreak, "current_index", 0);
    try expectFieldLayout(abi.HListPrevLinkBreak, "expected_pprev", @sizeOf(usize));
    try expectFieldLayout(abi.HListPrevLinkBreak, "actual_pprev", @sizeOf(usize) * 2);
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() LayoutError!void {
    try expectLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, 12, 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window", 0);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window", 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status", 8);
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() LayoutError!void {
    try expectLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, 12, 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied", 0);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped", 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered", 8);
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() LayoutError!void {
    try expectLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, 12, 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget", 0);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window", 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags", 8);
}

pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {
    try expectLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, 12, 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted", 0);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied", 4);
    try expectFieldLayout(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped", 8);
}

pub fn assertPublishedAbiLayouts() LayoutError!void {
    try assertBoundaryHeaderLayout();
    try assertExportStatusLayout();
    try assertInteropPolicyLayout();
    assertStatusAndFacilityValues();
    try assertMmioRangeLayout();
    try assertRbtreeRootViewLayout();
    assertNotifierResultValues();
    try assertNotifierBlockLayout();
    try assertNotifierChainPriorityIncreaseLayout();
    try assertListHeadLayout();
    try assertHListHeadLayout();
    try assertHListNodeLayout();
    try assertListBackLinkBreakLayout();
    try assertHListPrevLinkBreakLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();
}

pub fn assertInteropPolicyModeValues() void {
    comptime {
        expectComptimeByteValue(abi.PANIC_ABORT, @intFromEnum(abi.PanicMode.abort), "abi panic abort byte drifted");
        expectComptimeByteValue(abi.PANIC_BUG, @intFromEnum(abi.PanicMode.bug), "abi panic bug byte drifted");
        expectComptimeByteValue(abi.PANIC_WARN, @intFromEnum(abi.PanicMode.warn), "abi panic warn byte drifted");
        expectComptimeByteValue(abi.ALLOC_CALLER_PROVIDED, @intFromEnum(abi.AllocatorMode.caller_provided), "abi allocator caller byte drifted");
        expectComptimeByteValue(abi.ALLOC_KERNEL_HEAP, @intFromEnum(abi.AllocatorMode.kernel_heap), "abi allocator heap byte drifted");
        expectComptimeByteValue(abi.ALLOC_ARENA, @intFromEnum(abi.AllocatorMode.arena), "abi allocator arena byte drifted");
        expectComptimeByteValue(abi.UNSAFE_NONE, @intFromEnum(abi.UnsafeScope.none), "abi unsafe none byte drifted");
        expectComptimeByteValue(abi.UNSAFE_VOLATILE_MMIO, @intFromEnum(abi.UnsafeScope.volatile_mmio), "abi unsafe mmio byte drifted");
        expectComptimeByteValue(abi.UNSAFE_RAW_POINTER_BRIDGE, @intFromEnum(abi.UnsafeScope.raw_pointer_bridge), "abi unsafe raw-pointer byte drifted");
    }
}

pub fn assertStatusAndFacilityValues() void {
    comptime {
        expectComptimeByteValue(abi.FACILITY_KERNEL, @intFromEnum(abi.Facility.kernel), "abi kernel facility drifted");
        expectComptimeByteValue(abi.FACILITY_HELPERS, @intFromEnum(abi.Facility.helpers), "abi helpers facility drifted");
        expectComptimeByteValue(abi.FACILITY_DRIVERS, @intFromEnum(abi.Facility.drivers), "abi drivers facility drifted");
        expectComptimeByteValue(abi.STATUS_FLAG_ERROR, abi.makeStatus(-1, .kernel).flags, "abi error status flag drifted");
        expectComptimeByteValue(0, abi.makeStatus(0, .helpers).flags, "abi ok status flags drifted");
        expectComptimeByteValue(abi.FACILITY_DRIVERS, abi.makeStatus(-1, .drivers).facility, "abi status facility relay drifted");
    }
}

pub fn assertNotifierResultValues() void {
    std.debug.assert(abi.NOTIFIER_DONE == @intFromEnum(abi.NotifierResult.done));
    std.debug.assert(abi.NOTIFIER_OK == @intFromEnum(abi.NotifierResult.ok));
    std.debug.assert(abi.NOTIFIER_STOP == @intFromEnum(abi.NotifierResult.stop));
}

test "layout assert keeps starter header layouts explicit" {
    const BoundaryHeader = extern struct {
        size: u32,
        abi_version: u16,
        flags: u16,
    };

    const InteropPolicy = extern struct {
        panic_mode: u8,
        allocator_mode: u8,
        unsafe_scope: u8,
        reserved: u8,
    };

    try expectLayout(BoundaryHeader, 8, 4);
    try expectFieldLayout(BoundaryHeader, "size", 0);
    try expectFieldLayout(BoundaryHeader, "abi_version", 4);
    try expectFieldLayout(BoundaryHeader, "flags", 6);

    try expectLayout(InteropPolicy, 4, 1);
    try expectFieldLayout(InteropPolicy, "panic_mode", 0);
    try expectFieldLayout(InteropPolicy, "allocator_mode", 1);
    try expectFieldLayout(InteropPolicy, "unsafe_scope", 2);
    try expectFieldLayout(InteropPolicy, "reserved", 3);
}

test "layout assert reports helper-local range and root layouts explicitly" {
    try assertMmioRangeLayout();
    try assertRbtreeRootViewLayout();
}

test "layout assert reports mismatches without widening the call site" {
    const ExportStatus = extern struct {
        code: i32,
        facility: u16,
        flags: u16,
    };

    try expectLayout(ExportStatus, 8, 4);
    try std.testing.expectError(error.SizeMismatch, expectSize(ExportStatus, 12));
    try std.testing.expectError(error.AlignMismatch, expectAlign(ExportStatus, 2));
    try std.testing.expectError(error.OffsetMismatch, expectOffset(ExportStatus, "flags", 4));
}

test "layout assert keeps published facility and status constants explicit" {
    assertStatusAndFacilityValues();
}

test "layout assert aggregates the published ABI layouts" {
    try assertPublishedAbiLayouts();
}
