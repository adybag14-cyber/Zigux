const std = @import("std");
const abi = @import("abi_bindings");

pub const LayoutError = error{
    SizeMismatch,
    AlignMismatch,
    OffsetMismatch,
};

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

pub fn assertInteropPolicyLayout() LayoutError!void {
    try expectLayout(abi.InteropPolicy, 4, 1);
    try expectFieldLayout(abi.InteropPolicy, "panic_mode", 0);
    try expectFieldLayout(abi.InteropPolicy, "allocator_mode", 1);
    try expectFieldLayout(abi.InteropPolicy, "unsafe_scope", 2);
    try expectFieldLayout(abi.InteropPolicy, "reserved", 3);
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
    try assertNotifierBlockLayout();
    try assertNotifierChainPriorityIncreaseLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();
}

pub fn assertInteropPolicyModeValues() void {
    std.debug.assert(abi.PANIC_ABORT == @intFromEnum(abi.PanicMode.abort));
    std.debug.assert(abi.PANIC_BUG == @intFromEnum(abi.PanicMode.bug));
    std.debug.assert(abi.PANIC_WARN == @intFromEnum(abi.PanicMode.warn));
    std.debug.assert(abi.ALLOC_CALLER_PROVIDED == @intFromEnum(abi.AllocatorMode.caller_provided));
    std.debug.assert(abi.ALLOC_KERNEL_HEAP == @intFromEnum(abi.AllocatorMode.kernel_heap));
    std.debug.assert(abi.ALLOC_ARENA == @intFromEnum(abi.AllocatorMode.arena));
    std.debug.assert(abi.UNSAFE_NONE == @intFromEnum(abi.UnsafeScope.none));
    std.debug.assert(abi.UNSAFE_VOLATILE_MMIO == @intFromEnum(abi.UnsafeScope.volatile_mmio));
    std.debug.assert(abi.UNSAFE_RAW_POINTER_BRIDGE == @intFromEnum(abi.UnsafeScope.raw_pointer_bridge));
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

test "layout assert aggregates the published chrdev ABI layouts" {
    try assertPublishedAbiLayouts();
}
