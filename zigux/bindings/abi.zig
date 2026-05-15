const std = @import("std");

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

pub const DecodedInteropPolicy = struct {
    panic_mode: PanicMode,
    allocator_mode: AllocatorMode,
    unsafe_scope: UnsafeScope,
};

fn decodePanicMode(mode: u8) ?PanicMode {
    return switch (mode) {
        PANIC_ABORT => .abort,
        PANIC_BUG => .bug,
        PANIC_WARN => .warn,
        else => null,
    };
}

fn decodeAllocatorMode(mode: u8) ?AllocatorMode {
    return switch (mode) {
        ALLOC_CALLER_PROVIDED => .caller_provided,
        ALLOC_KERNEL_HEAP => .kernel_heap,
        ALLOC_ARENA => .arena,
        else => null,
    };
}

fn decodeUnsafeScope(scope: u8) ?UnsafeScope {
    return switch (scope) {
        UNSAFE_NONE => .none,
        UNSAFE_VOLATILE_MMIO => .volatile_mmio,
        UNSAFE_RAW_POINTER_BRIDGE => .raw_pointer_bridge,
        else => null,
    };
}

pub fn decodeInteropPolicyBytes(
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
) ?DecodedInteropPolicy {
    if (reserved != 0) return null;
    return .{
        .panic_mode = decodePanicMode(panic_mode) orelse return null,
        .allocator_mode = decodeAllocatorMode(allocator_mode) orelse return null,
        .unsafe_scope = decodeUnsafeScope(unsafe_scope) orelse return null,
    };
}

pub fn decodeInteropPolicy(policy: InteropPolicy) ?DecodedInteropPolicy {
    return decodeInteropPolicyBytes(
        policy.panic_mode,
        policy.allocator_mode,
        policy.unsafe_scope,
        policy.reserved,
    );
}

pub const NotifierResult = enum(u32) {
    done = NOTIFIER_DONE,
    ok = NOTIFIER_OK,
    stop = NOTIFIER_STOP,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const ChainPriorityIncrease = extern struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};

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

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {
    var current = head orelse return null;
    var previous_index: usize = 0;
    var previous_priority = current.priority;

    while (current.next != 0) {
        const next: *const NotifierBlock = @ptrFromInt(current.next);
        const current_index = previous_index + 1;
        if (next.priority > previous_priority) {
            return .{
                .previous_index = previous_index,
                .current_index = current_index,
                .previous_priority = previous_priority,
                .current_priority = next.priority,
            };
        }
        previous_index = current_index;
        previous_priority = next.priority;
        current = next;
    }

    return null;
}

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return firstChainPriorityIncrease(head) == null;
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

test "abi binding interop policy decode stays canonical" {
    const decoded = decodeInteropPolicy(.{
        .panic_mode = PANIC_WARN,
        .allocator_mode = ALLOC_ARENA,
        .unsafe_scope = UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0,
    }).?;

    try std.testing.expectEqual(PanicMode.warn, decoded.panic_mode);
    try std.testing.expectEqual(AllocatorMode.arena, decoded.allocator_mode);
    try std.testing.expectEqual(UnsafeScope.raw_pointer_bridge, decoded.unsafe_scope);
    try std.testing.expect(decodeInteropPolicyBytes(PANIC_WARN, ALLOC_ARENA, UNSAFE_RAW_POINTER_BRIDGE, 1) == null);
    try std.testing.expect(decodeInteropPolicyBytes(9, ALLOC_ARENA, UNSAFE_RAW_POINTER_BRIDGE, 0) == null);
    try std.testing.expect(decodeInteropPolicyBytes(PANIC_WARN, 9, UNSAFE_RAW_POINTER_BRIDGE, 0) == null);
    try std.testing.expect(decodeInteropPolicyBytes(PANIC_WARN, ALLOC_ARENA, 9, 0) == null);
}

test "abi binding chrdev structs keep the published layout" {
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

test "abi binding keeps notifier block layout and chain helper explicit" {
    const single = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const descending_third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = -4,
    };
    const descending_second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_third),
        .priority = 8,
    };
    const descending_first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&descending_second),
        .priority = 8,
    };
    const rising_second = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 5,
    };
    const rising_first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_second),
        .priority = 3,
    };

    try std.testing.expectEqual(@as(usize, 24), @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 8), @alignOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(NotifierBlock, "priority"));

    try std.testing.expectEqual(@as(usize, 24), @sizeOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 8), @alignOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(ChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, 16), @offsetOf(ChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(@as(usize, 20), @offsetOf(ChainPriorityIncrease, "current_priority"));

    try std.testing.expect(firstChainPriorityIncrease(null) == null);
    try std.testing.expect(chainHasNonincreasingPriority(null));
    try std.testing.expect(chainHasNonincreasingPriority(&single));
    try std.testing.expect(firstChainPriorityIncrease(&single) == null);
    try std.testing.expect(chainHasNonincreasingPriority(&descending_first));
    try std.testing.expect(firstChainPriorityIncrease(&descending_first) == null);
    try std.testing.expect(!chainHasNonincreasingPriority(&rising_first));

    const increase = firstChainPriorityIncrease(&rising_first).?;
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 3), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 5), increase.current_priority);
}