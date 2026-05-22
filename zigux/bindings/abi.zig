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

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED: u32 = 1;
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
pub const ChainPriorityIncrease = notifier_abi.NotifierChainPriorityIncrease;
pub const NotifierBlock = notifier_abi.NotifierBlock;
pub const ListHead = notifier_abi.ListHead;
pub const HListHead = notifier_abi.HListHead;
pub const HListNode = notifier_abi.HListNode;
pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;
pub const HListPrevLinkBreak = notifier_abi.HListPrevLinkBreak;

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

pub const BOUNDARY_HEADER_SIZE: u32 = @sizeOf(BoundaryHeader);
pub const BOUNDARY_HEADER_ALIGN: usize = @alignOf(BoundaryHeader);
pub const BOUNDARY_HEADER_OFFSET_SIZE: usize = @offsetOf(BoundaryHeader, "size");
pub const BOUNDARY_HEADER_OFFSET_ABI_VERSION: usize = @offsetOf(BoundaryHeader, "abi_version");
pub const BOUNDARY_HEADER_OFFSET_FLAGS: usize = @offsetOf(BoundaryHeader, "flags");

pub const EXPORT_STATUS_SIZE: u32 = @sizeOf(ExportStatus);
pub const EXPORT_STATUS_ALIGN: usize = @alignOf(ExportStatus);
pub const EXPORT_STATUS_OFFSET_CODE: usize = @offsetOf(ExportStatus, "code");
pub const EXPORT_STATUS_OFFSET_FACILITY: usize = @offsetOf(ExportStatus, "facility");
pub const EXPORT_STATUS_OFFSET_FLAGS: usize = @offsetOf(ExportStatus, "flags");

pub const INTEROP_POLICY_SIZE: u32 = @sizeOf(InteropPolicy);
pub const INTEROP_POLICY_ALIGN: usize = @alignOf(InteropPolicy);
pub const INTEROP_POLICY_OFFSET_PANIC_MODE: usize = @offsetOf(InteropPolicy, "panic_mode");
pub const INTEROP_POLICY_OFFSET_ALLOCATOR_MODE: usize = @offsetOf(InteropPolicy, "allocator_mode");
pub const INTEROP_POLICY_OFFSET_UNSAFE_SCOPE: usize = @offsetOf(InteropPolicy, "unsafe_scope");
pub const INTEROP_POLICY_OFFSET_RESERVED: usize = @offsetOf(InteropPolicy, "reserved");

pub const NOTIFIER_BLOCK_SIZE: usize = @sizeOf(NotifierBlock);
pub const NOTIFIER_BLOCK_ALIGN: usize = @alignOf(NotifierBlock);
pub const NOTIFIER_BLOCK_OFFSET_NOTIFIER_CALL: usize = @offsetOf(NotifierBlock, "notifier_call");
pub const NOTIFIER_BLOCK_OFFSET_NEXT: usize = @offsetOf(NotifierBlock, "next");
pub const NOTIFIER_BLOCK_OFFSET_PRIORITY: usize = @offsetOf(NotifierBlock, "priority");

pub const CHAIN_PRIORITY_INCREASE_SIZE: usize = @sizeOf(ChainPriorityIncrease);
pub const CHAIN_PRIORITY_INCREASE_ALIGN: usize = @alignOf(ChainPriorityIncrease);
pub const CHAIN_PRIORITY_INCREASE_OFFSET_PREVIOUS_INDEX: usize = @offsetOf(ChainPriorityIncrease, "previous_index");
pub const CHAIN_PRIORITY_INCREASE_OFFSET_CURRENT_INDEX: usize = @offsetOf(ChainPriorityIncrease, "current_index");
pub const CHAIN_PRIORITY_INCREASE_OFFSET_PREVIOUS_PRIORITY: usize = @offsetOf(ChainPriorityIncrease, "previous_priority");
pub const CHAIN_PRIORITY_INCREASE_OFFSET_CURRENT_PRIORITY: usize = @offsetOf(ChainPriorityIncrease, "current_priority");

pub const LIST_HEAD_SIZE: usize = @sizeOf(ListHead);
pub const LIST_HEAD_ALIGN: usize = @alignOf(ListHead);
pub const LIST_HEAD_OFFSET_NEXT: usize = @offsetOf(ListHead, "next");
pub const LIST_HEAD_OFFSET_PREV: usize = @offsetOf(ListHead, "prev");

pub const HLIST_HEAD_SIZE: usize = @sizeOf(HListHead);
pub const HLIST_HEAD_ALIGN: usize = @alignOf(HListHead);
pub const HLIST_HEAD_OFFSET_FIRST: usize = @offsetOf(HListHead, "first");

pub const HLIST_NODE_SIZE: usize = @sizeOf(HListNode);
pub const HLIST_NODE_ALIGN: usize = @alignOf(HListNode);
pub const HLIST_NODE_OFFSET_NEXT: usize = @offsetOf(HListNode, "next");
pub const HLIST_NODE_OFFSET_PPREV: usize = @offsetOf(HListNode, "pprev");

pub const LIST_BACKLINK_BREAK_SIZE: usize = @sizeOf(ListBackLinkBreak);
pub const LIST_BACKLINK_BREAK_ALIGN: usize = @alignOf(ListBackLinkBreak);
pub const LIST_BACKLINK_BREAK_OFFSET_CURRENT_INDEX: usize = @offsetOf(ListBackLinkBreak, "current_index");
pub const LIST_BACKLINK_BREAK_OFFSET_EXPECTED_PREV: usize = @offsetOf(ListBackLinkBreak, "expected_prev");
pub const LIST_BACKLINK_BREAK_OFFSET_ACTUAL_PREV: usize = @offsetOf(ListBackLinkBreak, "actual_prev");

pub const HLIST_PREV_LINK_BREAK_SIZE: usize = @sizeOf(HListPrevLinkBreak);
pub const HLIST_PREV_LINK_BREAK_ALIGN: usize = @alignOf(HListPrevLinkBreak);
pub const HLIST_PREV_LINK_BREAK_OFFSET_CURRENT_INDEX: usize = @offsetOf(HListPrevLinkBreak, "current_index");
pub const HLIST_PREV_LINK_BREAK_OFFSET_EXPECTED_PPREV: usize = @offsetOf(HListPrevLinkBreak, "expected_pprev");
pub const HLIST_PREV_LINK_BREAK_OFFSET_ACTUAL_PPREV: usize = @offsetOf(HListPrevLinkBreak, "actual_pprev");

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_SIZE: u32 = @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_ALIGN: usize = @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_ACK_WINDOW: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_DELIVERY_WINDOW: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_STATUS: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status");

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_SIZE: u32 = @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_ALIGN: usize = @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_APPLIED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_SKIPPED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_DELIVERED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered");

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_SIZE: u32 = @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_ALIGN: usize = @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_BUDGET: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_WINDOW: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_FLAGS: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags");

pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_SIZE: u32 = @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_ALIGN: usize = @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary);
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_ATTEMPTED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_APPLIED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied");
pub const CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_SKIPPED: usize = @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped");

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
    return notifier_abi.firstChainPriorityIncrease(head);
}

pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {
    return notifier_abi.firstBrokenBacklink(head);
}

pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {
    return notifier_abi.firstBrokenPrevLink(head);
}

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = BOUNDARY_HEADER_SIZE,
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

pub fn headerIsCompatibleSize(size: u32) bool {
    return size >= BOUNDARY_HEADER_SIZE;
}

pub fn headerIsCanonicalSize(size: u32) bool {
    return size == BOUNDARY_HEADER_SIZE;
}

pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return headerIsCanonicalSize(header.size) and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return headerIsCompatibleSize(header.size) and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn extendsBoundary(header: BoundaryHeader) bool {
    return headerIsCompatible(header) and !headerIsCanonical(header);
}

pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - BOUNDARY_HEADER_SIZE;
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    var canonical = header;
    canonical.size = BOUNDARY_HEADER_SIZE;
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

pub fn makeStatus(code: i32, facility: Facility) ExportStatus {
    return .{
        .code = code,
        .facility = @intFromEnum(facility),
        .flags = if (code < 0) STATUS_FLAG_ERROR else 0,
    };
}

pub fn okStatus(facility: Facility) ExportStatus {
    return makeStatus(0, facility);
}

pub fn statusIsOk(status: ExportStatus) bool {
    return (status.flags & STATUS_FLAG_ERROR) == 0;
}

test "abi binding default header stays canonical" {
    const header = defaultHeader(0x41);

    try std.testing.expectEqual(BOUNDARY_HEADER_SIZE, header.size);
    try std.testing.expectEqual(@as(u16, ABI_VERSION), header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x41), header.flags);

    try std.testing.expectEqual(@as(u32, 8), BOUNDARY_HEADER_SIZE);
    try std.testing.expectEqual(@as(usize, 4), BOUNDARY_HEADER_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), BOUNDARY_HEADER_OFFSET_SIZE);
    try std.testing.expectEqual(@as(usize, 4), BOUNDARY_HEADER_OFFSET_ABI_VERSION);
    try std.testing.expectEqual(@as(usize, 6), BOUNDARY_HEADER_OFFSET_FLAGS);
}

test "abi binding boundary header helpers keep compatibility explicit" {
    const default_header = defaultHeader(0x15);
    const expanded = compatibleHeader(BOUNDARY_HEADER_SIZE + 8, 0x15);
    const future = BoundaryHeader{
        .size = BOUNDARY_HEADER_SIZE + 16,
        .abi_version = ABI_VERSION,
        .flags = 0xA1,
    };
    const stale = BoundaryHeader{
        .size = BOUNDARY_HEADER_SIZE,
        .abi_version = ABI_VERSION + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeHeader(future);

    try std.testing.expect(headerHasCurrentAbiVersion(default_header.abi_version));
    try std.testing.expect(headerIsCanonicalSize(default_header.size));
    try std.testing.expect(headerIsCompatibleSize(default_header.size));
    try std.testing.expect(headerIsCanonical(default_header));
    try std.testing.expect(headerIsCompatible(default_header));
    try std.testing.expect(!extendsBoundary(default_header));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(default_header));

    try std.testing.expect(headerIsCompatibleSize(expanded.size));
    try std.testing.expect(!headerIsCanonicalSize(expanded.size));
    try std.testing.expect(!headerIsCanonical(expanded));
    try std.testing.expect(headerIsCompatible(expanded));
    try std.testing.expect(extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 8), requestedExtraBytes(expanded));
    try std.testing.expect(!headerIsCanonical(future));
    try std.testing.expect(headerIsCompatible(future));
    try std.testing.expect(extendsBoundary(future));
    try std.testing.expectEqual(@as(u32, 16), requestedExtraBytes(future));

    try std.testing.expect(headerIsCanonicalSize(stale.size));
    try std.testing.expect(headerIsCompatibleSize(stale.size));
    try std.testing.expect(!headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!headerIsCanonical(stale));
    try std.testing.expect(!headerIsCompatible(stale));
    try std.testing.expect(!extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(stale));

    try std.testing.expectEqual(BOUNDARY_HEADER_SIZE, canonicalized.size);
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

test "abi binding status helper mirrors the exported status flag contract" {
    const ok = okStatus(.helpers);
    const negative = makeStatus(-22, .kernel);
    const positive = makeStatus(7, .drivers);
    const flagged_positive = ExportStatus{
        .code = 7,
        .facility = FACILITY_DRIVERS,
        .flags = STATUS_FLAG_ERROR,
    };

    try std.testing.expect(statusIsOk(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, FACILITY_HELPERS), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);

    try std.testing.expect(!statusIsOk(negative));
    try std.testing.expectEqual(@as(i32, -22), negative.code);
    try std.testing.expectEqual(@as(u16, FACILITY_KERNEL), negative.facility);
    try std.testing.expectEqual(@as(u16, STATUS_FLAG_ERROR), negative.flags);

    try std.testing.expect(statusIsOk(positive));
    try std.testing.expectEqual(@as(i32, 7), positive.code);
    try std.testing.expectEqual(@as(u16, FACILITY_DRIVERS), positive.facility);
    try std.testing.expectEqual(@as(u16, 0), positive.flags);
    try std.testing.expect(!statusIsOk(flagged_positive));
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

test "abi binding chrdev notify window constants stay explicit" {
    try std.testing.expectEqual(
        @as(u32, 1),
        CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );

    const delivery_view = ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView{
        .ack_window = 7,
        .delivery_window = 11,
        .status = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };
    const delivery_summary = ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        .skipped = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        .delivered = 3,
    };
    const budget_view = ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView{
        .budget = 5,
        .window = 9,
        .flags = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED |
            CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    };
    const budget_summary = ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary{
        .attempted = 4,
        .applied = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        .skipped = CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expectEqual(@as(u32, 1), delivery_view.status);
    try std.testing.expectEqual(@as(u32, 1), delivery_summary.applied);
    try std.testing.expectEqual(@as(u32, 1), delivery_summary.skipped);
    try std.testing.expectEqual(@as(u32, 1), budget_view.flags);
    try std.testing.expectEqual(@as(u32, 1), budget_summary.applied);
    try std.testing.expectEqual(@as(u32, 1), budget_summary.skipped);
}

test "abi binding exported layout constants stay aligned with the published boundary surface" {
    try std.testing.expectEqual(@as(u32, 8), BOUNDARY_HEADER_SIZE);
    try std.testing.expectEqual(@as(usize, 4), BOUNDARY_HEADER_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), BOUNDARY_HEADER_OFFSET_SIZE);
    try std.testing.expectEqual(@as(usize, 4), BOUNDARY_HEADER_OFFSET_ABI_VERSION);
    try std.testing.expectEqual(@as(usize, 6), BOUNDARY_HEADER_OFFSET_FLAGS);

    try std.testing.expectEqual(@as(u32, 8), EXPORT_STATUS_SIZE);
    try std.testing.expectEqual(@as(usize, 4), EXPORT_STATUS_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), EXPORT_STATUS_OFFSET_CODE);
    try std.testing.expectEqual(@as(usize, 4), EXPORT_STATUS_OFFSET_FACILITY);
    try std.testing.expectEqual(@as(usize, 6), EXPORT_STATUS_OFFSET_FLAGS);

    try std.testing.expectEqual(@as(u32, 4), INTEROP_POLICY_SIZE);
    try std.testing.expectEqual(@as(usize, 1), INTEROP_POLICY_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), INTEROP_POLICY_OFFSET_PANIC_MODE);
    try std.testing.expectEqual(@as(usize, 1), INTEROP_POLICY_OFFSET_ALLOCATOR_MODE);
    try std.testing.expectEqual(@as(usize, 2), INTEROP_POLICY_OFFSET_UNSAFE_SCOPE);
    try std.testing.expectEqual(@as(usize, 3), INTEROP_POLICY_OFFSET_RESERVED);

    try std.testing.expectEqual(@as(u32, 12), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_SIZE);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_ACK_WINDOW);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_DELIVERY_WINDOW);
    try std.testing.expectEqual(@as(usize, 8), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_VIEW_OFFSET_STATUS);

    try std.testing.expectEqual(@as(u32, 12), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_SIZE);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_APPLIED);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_SKIPPED);
    try std.testing.expectEqual(@as(usize, 8), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_SUMMARY_OFFSET_DELIVERED);

    try std.testing.expectEqual(@as(u32, 12), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_SIZE);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_BUDGET);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_WINDOW);
    try std.testing.expectEqual(@as(usize, 8), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_VIEW_OFFSET_FLAGS);

    try std.testing.expectEqual(@as(u32, 12), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_SIZE);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_ATTEMPTED);
    try std.testing.expectEqual(@as(usize, 4), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_APPLIED);
    try std.testing.expectEqual(@as(usize, 8), CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY_OFFSET_SKIPPED);
}

test "abi binding notifier and list layout constants stay aligned with the exported ABI header" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_notifier_size = std.mem.alignForward(
        usize,
        raw_size,
        NOTIFIER_BLOCK_ALIGN,
    );
    const raw_increase_size = (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2);
    const expected_increase_size = std.mem.alignForward(
        usize,
        raw_increase_size,
        CHAIN_PRIORITY_INCREASE_ALIGN,
    );

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), NOTIFIER_BLOCK_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), NOTIFIER_BLOCK_OFFSET_NOTIFIER_CALL);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), NOTIFIER_BLOCK_OFFSET_NEXT);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), NOTIFIER_BLOCK_OFFSET_PRIORITY);
    try std.testing.expectEqual(expected_notifier_size, NOTIFIER_BLOCK_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), CHAIN_PRIORITY_INCREASE_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), CHAIN_PRIORITY_INCREASE_OFFSET_PREVIOUS_INDEX);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), CHAIN_PRIORITY_INCREASE_OFFSET_CURRENT_INDEX);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), CHAIN_PRIORITY_INCREASE_OFFSET_PREVIOUS_PRIORITY);
    try std.testing.expectEqual(@as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)), CHAIN_PRIORITY_INCREASE_OFFSET_CURRENT_PRIORITY);
    try std.testing.expectEqual(expected_increase_size, CHAIN_PRIORITY_INCREASE_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), LIST_HEAD_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), LIST_HEAD_OFFSET_NEXT);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), LIST_HEAD_OFFSET_PREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), LIST_HEAD_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), HLIST_HEAD_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), HLIST_HEAD_OFFSET_FIRST);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), HLIST_HEAD_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), HLIST_NODE_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), HLIST_NODE_OFFSET_NEXT);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), HLIST_NODE_OFFSET_PPREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), HLIST_NODE_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), LIST_BACKLINK_BREAK_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), LIST_BACKLINK_BREAK_OFFSET_CURRENT_INDEX);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), LIST_BACKLINK_BREAK_OFFSET_EXPECTED_PREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), LIST_BACKLINK_BREAK_OFFSET_ACTUAL_PREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), LIST_BACKLINK_BREAK_SIZE);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), HLIST_PREV_LINK_BREAK_ALIGN);
    try std.testing.expectEqual(@as(usize, 0), HLIST_PREV_LINK_BREAK_OFFSET_CURRENT_INDEX);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), HLIST_PREV_LINK_BREAK_OFFSET_EXPECTED_PPREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), HLIST_PREV_LINK_BREAK_OFFSET_ACTUAL_PPREV);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), HLIST_PREV_LINK_BREAK_SIZE);
}

test "abi binding notifier helper relays stay aligned with notifier_abi" {
    const tail = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 8,
    };
    const head = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&tail),
        .priority = 2,
    };

    try std.testing.expectEqual(notifier_abi.chainHasNonincreasingPriority(&head), chainHasNonincreasingPriority(&head));
    try std.testing.expectEqual(notifier_abi.firstChainPriorityIncrease(&head), firstChainPriorityIncrease(&head));
}

test "abi binding first priority increase and list helpers stay explicit" {
    const rising_tail = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 7,
    };
    const middle = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&rising_tail),
        .priority = 4,
    };
    const head = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&middle),
        .priority = 5,
    };
    const flat_tail = NotifierBlock{
        .notifier_call = 0,
        .next = 0,
        .priority = 2,
    };
    const flat_head = NotifierBlock{
        .notifier_call = 0,
        .next = @intFromPtr(&flat_tail),
        .priority = 2,
    };

    const increase = firstChainPriorityIncrease(&head) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 1), increase.previous_index);
    try std.testing.expectEqual(@as(usize, 2), increase.current_index);
    try std.testing.expectEqual(@as(i32, 4), increase.previous_priority);
    try std.testing.expectEqual(@as(i32, 7), increase.current_priority);
    try std.testing.expectEqual(@as(?ChainPriorityIncrease, null), firstChainPriorityIncrease(&flat_head));
    try std.testing.expectEqual(@as(?ChainPriorityIncrease, null), firstChainPriorityIncrease(null));

    var list_head = ListHead{ .next = 0, .prev = 0 };
    list_head.next = @intFromPtr(&list_head);
    list_head.prev = @intFromPtr(&list_head);
    try std.testing.expect(listHasConsistentBacklinks(&list_head));
    try std.testing.expectEqual(@as(?ListBackLinkBreak, null), firstBrokenBacklink(&list_head));

    const hlist_head = HListHead{ .first = 0 };
    try std.testing.expect(hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(?HListPrevLinkBreak, null), firstBrokenPrevLink(&hlist_head));
}
