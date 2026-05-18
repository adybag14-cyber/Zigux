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

pub const NotifierBlock = notifier_abi.NotifierBlock;
pub const ListHead = notifier_abi.ListHead;
pub const HListHead = notifier_abi.HListHead;
pub const HListNode = notifier_abi.HListNode;

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return notifier_abi.chainHasNonincreasingPriority(head);
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    return notifier_abi.listHasConsistentBacklinks(head);
}

pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    return notifier_abi.hlistHasConsistentPrevLinks(head);
}

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {
    var current = head orelse return null;
    if (current.next == 0) return null;

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

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = ABI_VERSION,
        .flags = flags,
    };
}

pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {
    var header = defaultHeader(flags);
    header.size = size;
    return header;
}

pub fn headerHasCurrentAbiVersion(abi_version: u16) bool {
    return abi_version == ABI_VERSION;
}

pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return header.size == @sizeOf(BoundaryHeader) and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return header.size >= @sizeOf(BoundaryHeader) and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn extendsBoundary(header: BoundaryHeader) bool {
    return headerIsCompatible(header) and !headerIsCanonical(header);
}

pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - @as(u32, @sizeOf(BoundaryHeader));
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    var canonical = header;
    canonical.size = @sizeOf(BoundaryHeader);
    canonical.abi_version = ABI_VERSION;
    return canonical;
}

pub fn defaultInteropPolicy() InteropPolicy {
    return .{
        .panic_mode = @intFromEnum(PanicMode.abort),
        .allocator_mode = @intFromEnum(AllocatorMode.caller_provided),
        .unsafe_scope = @intFromEnum(UnsafeScope.none),
        .reserved = 0,
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

test "abi binding boundary header helpers keep compatibility explicit" {
    const default_header = defaultHeader(0x15);
    const expanded = compatibleHeader(@sizeOf(BoundaryHeader) + 8, 0x15);
    const future = BoundaryHeader{
        .size = @sizeOf(BoundaryHeader) + 16,
        .abi_version = ABI_VERSION,
        .flags = 0xA1,
    };
    const stale = BoundaryHeader{
        .size = @sizeOf(BoundaryHeader),
        .abi_version = ABI_VERSION + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeHeader(future);

    try std.testing.expect(headerHasCurrentAbiVersion(default_header.abi_version));
    try std.testing.expect(headerIsCanonical(default_header));
    try std.testing.expect(headerIsCompatible(default_header));
    try std.testing.expect(!extendsBoundary(default_header));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(default_header));

    try std.testing.expect(!headerIsCanonical(expanded));
    try std.testing.expect(headerIsCompatible(expanded));
    try std.testing.expect(extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 8), requestedExtraBytes(expanded));
    try std.testing.expect(!headerIsCanonical(future));
    try std.testing.expect(headerIsCompatible(future));
    try std.testing.expect(extendsBoundary(future));
    try std.testing.expectEqual(@as(u32, 16), requestedExtraBytes(future));

    try std.testing.expect(!headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!headerIsCanonical(stale));
    try std.testing.expect(!headerIsCompatible(stale));
    try std.testing.expect(!extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(stale));

    try std.testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), canonicalized.size);
    try std.testing.expectEqual(@as(u16, ABI_VERSION), canonicalized.abi_version);
    try std.testing.expectEqual(future.flags, canonicalized.flags);
    try std.testing.expect(headerIsCanonical(canonicalized));
    try std.testing.expect(!extendsBoundary(canonicalized));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(canonicalized));
}

test "abi binding default interop policy stays safe by default" {
    const policy = defaultInteropPolicy();

    try std.testing.expectEqual(@as(u8, @intFromEnum(PanicMode.abort)), policy.panic_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(AllocatorMode.caller_provided)), policy.allocator_mode);
    try std.testing.expectEqual(@as(u8, @intFromEnum(UnsafeScope.none)), policy.unsafe_scope);
    try std.testing.expectEqual(@as(u8, 0), policy.reserved);
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

test "abi binding notifier and list layouts stay aligned with the dedicated notifier bindings" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_notifier_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(NotifierBlock));
    try std.testing.expectEqual(expected_notifier_size, @sizeOf(NotifierBlock));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(NotifierBlock, "priority"));
    try std.testing.expectEqual(@sizeOf(notifier_abi.NotifierBlock), @sizeOf(NotifierBlock));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListHead, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListHead, "prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHead));
    try std.testing.expectEqual(@sizeOf(notifier_abi.ListHead), @sizeOf(ListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListHead, "first"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHead));
    try std.testing.expectEqual(@sizeOf(notifier_abi.HListHead), @sizeOf(HListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListNode));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListNode, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListNode, "pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNode));
    try std.testing.expectEqual(@sizeOf(notifier_abi.HListNode), @sizeOf(HListNode));
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

test "abi binding list helper matches the dedicated notifier binding" {
    var sentinel = ListHead{ .next = 0, .prev = 0 };
    var first = ListHead{ .next = 0, .prev = 0 };
    var second = ListHead{ .next = 0, .prev = 0 };

    sentinel.next = @intFromPtr(&first);
    sentinel.prev = @intFromPtr(&second);
    first.next = @intFromPtr(&second);
    first.prev = @intFromPtr(&sentinel);
    second.next = @intFromPtr(&sentinel);
    second.prev = @intFromPtr(&first);

    try std.testing.expect(listHasConsistentBacklinks(&sentinel));
    try std.testing.expectEqual(
        notifier_abi.listHasConsistentBacklinks(&sentinel),
        listHasConsistentBacklinks(&sentinel),
    );

    second.prev = @intFromPtr(&sentinel);
    try std.testing.expect(!listHasConsistentBacklinks(&sentinel));
    try std.testing.expectEqual(
        notifier_abi.listHasConsistentBacklinks(&sentinel),
        listHasConsistentBacklinks(&sentinel),
    );
}

test "abi binding hlist helper matches the dedicated notifier binding" {
    var head = HListHead{ .first = 0 };
    var first = HListNode{ .next = 0, .pprev = 0 };
    var second = HListNode{ .next = 0, .pprev = 0 };

    head.first = @intFromPtr(&first);
    first.next = @intFromPtr(&second);
    first.pprev = @intFromPtr(&head.first);
    second.next = 0;
    second.pprev = @intFromPtr(&first.next);

    try std.testing.expect(hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(
        notifier_abi.hlistHasConsistentPrevLinks(&head),
        hlistHasConsistentPrevLinks(&head),
    );

    second.pprev = @intFromPtr(&head.first);
    try std.testing.expect(!hlistHasConsistentPrevLinks(&head));
    try std.testing.expectEqual(
        notifier_abi.hlistHasConsistentPrevLinks(&head),
        hlistHasConsistentPrevLinks(&head),
    );
}

test "abi binding notifier chain priority increase layout stays stable" {
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + @sizeOf(i32) * 2), @sizeOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(ChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2 + @sizeOf(i32)), @offsetOf(ChainPriorityIncrease, "current_priority"));
}

test "abi binding reports the first notifier priority increase" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 6,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 2,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    const increase = firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 2), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 6), increase.current_priority);
}

test "abi binding omits notifier increase when the chain is nonincreasing" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 1,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 3,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 5,
    };

    try std.testing.expectEqual(@as(?ChainPriorityIncrease, null), firstChainPriorityIncrease(null));
    try std.testing.expectEqual(@as(?ChainPriorityIncrease, null), firstChainPriorityIncrease(&first));
}

test "abi binding keeps the earliest notifier priority increase explicit" {
    const third = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const second = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&third),
        .priority = 6,
    };
    const first = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&second),
        .priority = 4,
    };

    const increase = firstChainPriorityIncrease(&first) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 0), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 1), increase.current_index);
    try std.testing.expectEqual(@as(i32, 4), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 6), increase.current_priority);
}
