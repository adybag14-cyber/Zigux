const std = @import("std");
const notifier_abi = @import("notifier_abi.zig");

pub const ABI_VERSION: u16 = 1;

pub const FACILITY_KERNEL: u16 = 1;
pub const FACILITY_HELPERS: u16 = 2;
pub const FACILITY_DRIVERS: u16 = 3;

pub const STATUS_FLAG_ERROR: u16 = 1;

pub const PANIC_ABORT: u8 = 0;
pub const PANIC_BUG: u8 = 1;
pub const PANIC_WARN: u8 = 2;

pub const ALLOC_CALLER_PROVIDED: u8 = 0;
pub const ALLOC_KERNEL_HEAP: u8 = 1;
pub const ALLOC_ARENA: u8 = 2;

pub const UNSAFE_NONE: u8 = 0;
pub const UNSAFE_VOLATILE_MMIO: u8 = 1;
pub const UNSAFE_RAW_POINTER_BRIDGE: u8 = 2;

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED: u32 = 1;
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED: u32 = 1;

pub const NOTIFIER_DONE: u32 = 0;
pub const NOTIFIER_OK: u32 = 1;
pub const NOTIFIER_STOP: u32 = 2;

pub const BoundaryHeader = extern struct {
    size: u32,
    abi_version: u16,
    flags: u16,
};

pub const ExportStatus = extern struct {
    code: i32,
    facility: u16,
    flags: u16,
};

pub const InteropPolicy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};

pub const Facility = enum(u16) {
    kernel = FACILITY_KERNEL,
    helpers = FACILITY_HELPERS,
    drivers = FACILITY_DRIVERS,
};

pub const PanicMode = enum(u8) {
    abort = PANIC_ABORT,
    bug = PANIC_BUG,
    warn = PANIC_WARN,
};

pub const AllocatorMode = enum(u8) {
    caller_provided = ALLOC_CALLER_PROVIDED,
    kernel_heap = ALLOC_KERNEL_HEAP,
    arena = ALLOC_ARENA,
};

pub const UnsafeScope = enum(u8) {
    none = UNSAFE_NONE,
    volatile_mmio = UNSAFE_VOLATILE_MMIO,
    raw_pointer_bridge = UNSAFE_RAW_POINTER_BRIDGE,
};

pub const NotifierResult = notifier_abi.NotifierResult;

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {
    ack_window: u32,
    delivery_window: u32,
    status: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {
    applied: u32,
    skipped: u32,
    delivered: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView = extern struct {
    budget: u32,
    window: u32,
    flags: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary = extern struct {
    attempted: u32,
    applied: u32,
    skipped: u32,
};

pub const NotifierBlock = notifier_abi.NotifierBlock;

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return notifier_abi.chainHasNonincreasingPriority(head);
}

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = ABI_VERSION,
        .flags = flags,
    };
}

test "abi binding default header stays canonical" {
    const header = defaultHeader(0x41);

    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), header.size);
    try std.testing.expectEqual(@as(u16, ABI_VERSION), header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x41), header.flags);

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(BoundaryHeader, "flags"));
}

test "abi binding enums stay aligned with exported constants" {
    try std.testing.expectEqual(@as(u16, FACILITY_KERNEL), @intFromEnum(Facility.kernel));
    try std.testing.expectEqual(@as(u16, FACILITY_HELPERS), @intFromEnum(Facility.helpers));
    try std.testing.expectEqual(@as(u16, FACILITY_DRIVERS), @intFromEnum(Facility.drivers));

    try std.testing.expectEqual(@as(u8, PANIC_ABORT), @intFromEnum(PanicMode.abort));
    try std.testing.expectEqual(@as(u8, PANIC_BUG), @intFromEnum(PanicMode.bug));
    try std.testing.expectEqual(@as(u8, PANIC_WARN), @intFromEnum(PanicMode.warn));

    try std.testing.expectEqual(@as(u8, ALLOC_CALLER_PROVIDED), @intFromEnum(AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, ALLOC_KERNEL_HEAP), @intFromEnum(AllocatorMode.kernel_heap));
    try std.testing.expectEqual(@as(u8, ALLOC_ARENA), @intFromEnum(AllocatorMode.arena));

    try std.testing.expectEqual(@as(u8, UNSAFE_NONE), @intFromEnum(UnsafeScope.none));
    try std.testing.expectEqual(@as(u8, UNSAFE_VOLATILE_MMIO), @intFromEnum(UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u8, UNSAFE_RAW_POINTER_BRIDGE), @intFromEnum(UnsafeScope.raw_pointer_bridge));

    try std.testing.expectEqual(@as(u32, NOTIFIER_DONE), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, NOTIFIER_OK), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, NOTIFIER_STOP), @intFromEnum(NotifierResult.stop));
}

test "abi binding chrdev structs keep the published layout" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(ExportStatus));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(ExportStatus, "flags"));

    try std.testing.expectEqual(@as(usize, 4), @sizeOf(InteropPolicy));
    try std.testing.expectEqual(@as(usize, 1), @alignOf(InteropPolicy));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(InteropPolicy, "panic_mode"));
    try std.testing.expectEqual(@as(usize, 1), @offsetOf(InteropPolicy, "allocator_mode"));
    try std.testing.expectEqual(@as(usize, 2), @offsetOf(InteropPolicy, "unsafe_scope"));
    try std.testing.expectEqual(@as(usize, 3), @offsetOf(InteropPolicy, "reserved"));

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"));

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"));

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"));

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"));
}

test "abi binding notifier block keeps the published layout" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierBlock));
    try std.testing.expectEqual(expected_size, @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierBlock, "priority"));
}

test "abi binding notifier helper matches the dedicated notifier binding" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 3,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 5,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try std.testing.expect(chainHasNonincreasingPriority(&first));
    try std.testing.expectEqual(
        notifier_abi.chainHasNonincreasingPriority(&first),
        chainHasNonincreasingPriority(&first),
    );

    const increasing_tail = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const increasing_head = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&increasing_tail),
        .priority = 2,
    };

    try std.testing.expect(!chainHasNonincreasingPriority(&increasing_head));
    try std.testing.expectEqual(
        notifier_abi.chainHasNonincreasingPriority(&increasing_head),
        chainHasNonincreasingPriority(&increasing_head),
    );
}

test "abi binding notifier block preserves pointer-width chain links" {
    const tail = NotifierBlock{
        .notifier_call = 0x33,
        .next = 0,
        .priority = -2,
    };
    const middle = NotifierBlock{
        .notifier_call = 0x22,
        .next = @intFromPtr(&tail),
        .priority = 7,
    };
    const head = NotifierBlock{
        .notifier_call = 0x11,
        .next = @intFromPtr(&middle),
        .priority = 12,
    };

    const middle_ptr: *const NotifierBlock = @ptrFromInt(head.next);
    const tail_ptr: *const NotifierBlock = @ptrFromInt(middle_ptr.next);

    try std.testing.expectEqual(@as(usize, @intFromPtr(&middle)), head.next);
    try std.testing.expectEqual(@as(usize, @intFromPtr(&tail)), middle_ptr.next);
    try std.testing.expectEqual(@as(usize, 0), tail_ptr.next);

    try std.testing.expectEqual(@as(usize, 0x11), head.notifier_call);
    try std.testing.expectEqual(@as(usize, 0x22), middle_ptr.notifier_call);
    try std.testing.expectEqual(@as(usize, 0x33), tail_ptr.notifier_call);

    try std.testing.expectEqual(@as(i32, 12), head.priority);
    try std.testing.expectEqual(@as(i32, 7), middle_ptr.priority);
    try std.testing.expectEqual(@as(i32, -2), tail_ptr.priority);
}
