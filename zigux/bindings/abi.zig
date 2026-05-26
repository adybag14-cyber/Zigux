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

pub const RBTREE_ROOT_VIEW_FLAG_CACHED: u32 = 1;
pub const RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID: u32 = 2;

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

pub const RbtreeRootView = extern struct {
    root: usize,
    cached_leftmost: usize,
    flags: u32,
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
pub const NotifierChainPriorityIncrease = notifier_abi.NotifierChainPriorityIncrease;
pub const ChainPriorityIncrease = NotifierChainPriorityIncrease;
pub const NotifierBlock = notifier_abi.NotifierBlock;
pub const ListHead = notifier_abi.ListHead;
pub const HListHead = notifier_abi.HListHead;
pub const HListNode = notifier_abi.HListNode;
pub const ListBackLinkBreak = notifier_abi.ListBackLinkBreak;
pub const HListPrevLinkBreak = notifier_abi.HListPrevLinkBreak;

pub const boundary_header_size = @sizeOf(BoundaryHeader);
pub const boundary_header_align = @alignOf(BoundaryHeader);
pub const boundary_header_size_offset = @offsetOf(BoundaryHeader, "size");
pub const boundary_header_abi_version_offset = @offsetOf(BoundaryHeader, "abi_version");
pub const boundary_header_flags_offset = @offsetOf(BoundaryHeader, "flags");

pub const export_status_size = @sizeOf(ExportStatus);
pub const export_status_align = @alignOf(ExportStatus);
pub const export_status_code_offset = @offsetOf(ExportStatus, "code");
pub const export_status_facility_offset = @offsetOf(ExportStatus, "facility");
pub const export_status_flags_offset = @offsetOf(ExportStatus, "flags");

pub const interop_policy_size = @sizeOf(InteropPolicy);
pub const interop_policy_align = @alignOf(InteropPolicy);
pub const interop_policy_panic_mode_offset = @offsetOf(InteropPolicy, "panic_mode");
pub const interop_policy_allocator_mode_offset = @offsetOf(InteropPolicy, "allocator_mode");
pub const interop_policy_unsafe_scope_offset = @offsetOf(InteropPolicy, "unsafe_scope");
pub const interop_policy_reserved_offset = @offsetOf(InteropPolicy, "reserved");

pub const rbtree_root_view_size = @sizeOf(RbtreeRootView);
pub const rbtree_root_view_align = @alignOf(RbtreeRootView);
pub const rbtree_root_view_root_offset = @offsetOf(RbtreeRootView, "root");
pub const rbtree_root_view_cached_leftmost_offset = @offsetOf(RbtreeRootView, "cached_leftmost");
pub const rbtree_root_view_flags_offset = @offsetOf(RbtreeRootView, "flags");

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

pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size =
    @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align =
    @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status");

pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size =
    @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align =
    @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered");

pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size =
    @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align =
    @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags");

pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size =
    @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align =
    @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary);
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied");
pub const chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset =
    @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped");

pub const notifier_block_size = @sizeOf(NotifierBlock);
pub const notifier_block_align = @alignOf(NotifierBlock);
pub const notifier_block_notifier_call_offset = @offsetOf(NotifierBlock, "notifier_call");
pub const notifier_block_next_offset = @offsetOf(NotifierBlock, "next");
pub const notifier_block_priority_offset = @offsetOf(NotifierBlock, "priority");

pub fn notifierResultFromInt(result: u32) ?NotifierResult {
    return notifier_abi.resultFromInt(result);
}

pub fn notifierResultIsKnown(result: u32) bool {
    return notifier_abi.resultIsKnown(result);
}

pub fn notifierResultStopsChainValue(result: u32) bool {
    return notifier_abi.resultStopsChainValue(result);
}

pub fn notifierResultStopsChain(result: NotifierResult) bool {
    return notifier_abi.resultStopsChain(result);
}

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return notifier_abi.chainHasNonincreasingPriority(head);
}

pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool {
    return notifier_abi.listHasConsistentBacklinks(head);
}

pub fn hlistFirstPprevMatchesHead(head: ?*const HListHead) bool {
    return notifier_abi.firstPprevMatchesHead(head);
}

pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool {
    return notifier_abi.hlistHasConsistentPrevLinks(head);
}

pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {
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
        .size = @as(u32, @intCast(boundary_header_size)),
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
    return header.size == boundary_header_size and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return header.size >= boundary_header_size and
        headerHasCurrentAbiVersion(header.abi_version);
}

pub fn extendsBoundary(header: BoundaryHeader) bool {
    return headerIsCompatible(header) and !headerIsCanonical(header);
}

pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - @as(u32, @intCast(boundary_header_size));
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    var canonical = header;
    canonical.size = @as(u32, @intCast(boundary_header_size));
    canonical.abi_version = ABI_VERSION;
    return canonical;
}

pub fn rbtreeRootViewIsCached(view: RbtreeRootView) bool {
    return (view.flags & RBTREE_ROOT_VIEW_FLAG_CACHED) != 0;
}

pub fn rbtreeRootViewHasLeftmost(view: RbtreeRootView) bool {
    return (view.flags & RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID) != 0;
}

pub fn rbtreeRootViewIsValid(view: RbtreeRootView) bool {
    if (view.root == 0) return false;

    const cached = rbtreeRootViewIsCached(view);
    const has_leftmost_flag = rbtreeRootViewHasLeftmost(view);
    const has_leftmost_addr = view.cached_leftmost != 0;

    if (cached != has_leftmost_flag) return false;
    if (cached != has_leftmost_addr) return false;

    return true;
}

pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView {
    if (view.root == 0) {
        return .{
            .root = 0,
            .cached_leftmost = 0,
            .flags = 0,
        };
    }

    var canonical = view;
    if (canonical.cached_leftmost == 0) {
        canonical.flags = 0;
        return canonical;
    }

    canonical.flags = RBTREE_ROOT_VIEW_FLAG_CACHED | RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID;
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

pub fn panicModeFromByte(mode: u8) ?PanicMode {
    return switch (mode) {
        PANIC_ABORT => .abort,
        PANIC_BUG => .bug,
        PANIC_WARN => .warn,
        else => null,
    };
}

pub fn allocatorModeFromByte(mode: u8) ?AllocatorMode {
    return switch (mode) {
        ALLOC_CALLER_PROVIDED => .caller_provided,
        ALLOC_KERNEL_HEAP => .kernel_heap,
        ALLOC_ARENA => .arena,
        else => null,
    };
}

pub fn unsafeScopeFromByte(scope: u8) ?UnsafeScope {
    return switch (scope) {
        UNSAFE_NONE => .none,
        UNSAFE_VOLATILE_MMIO => .volatile_mmio,
        UNSAFE_RAW_POINTER_BRIDGE => .raw_pointer_bridge,
        else => null,
    };
}

pub fn panicModeIsKnown(mode: u8) bool {
    return panicModeFromByte(mode) != null;
}

pub fn allocatorModeIsKnown(mode: u8) bool {
    return allocatorModeFromByte(mode) != null;
}

pub fn unsafeScopeIsKnown(scope: u8) bool {
    return unsafeScopeFromByte(scope) != null;
}

pub fn interopPolicyReservedClear(policy: InteropPolicy) bool {
    return policy.reserved == 0;
}

pub fn panicModeFromInteropPolicy(policy: InteropPolicy) ?PanicMode {
    if (!interopPolicyReservedClear(policy)) return null;
    return panicModeFromByte(policy.panic_mode);
}

pub fn allocatorModeFromInteropPolicy(policy: InteropPolicy) ?AllocatorMode {
    if (!interopPolicyReservedClear(policy)) return null;
    return allocatorModeFromByte(policy.allocator_mode);
}

pub fn unsafeScopeFromInteropPolicy(policy: InteropPolicy) ?UnsafeScope {
    if (!interopPolicyReservedClear(policy)) return null;
    return unsafeScopeFromByte(policy.unsafe_scope);
}

pub fn interopPolicyIsRecognized(policy: InteropPolicy) bool {
    return panicModeFromInteropPolicy(policy) != null and
        allocatorModeFromInteropPolicy(policy) != null and
        unsafeScopeFromInteropPolicy(policy) != null;
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

pub fn facilityFromInt(facility: u16) ?Facility {
    return switch (facility) {
        FACILITY_KERNEL => .kernel,
        FACILITY_HELPERS => .helpers,
        FACILITY_DRIVERS => .drivers,
        else => null,
    };
}

pub fn facilityIsKnown(facility: u16) bool {
    return facilityFromInt(facility) != null;
}

pub fn statusHasKnownFacility(status: ExportStatus) bool {
    return facilityIsKnown(status.facility);
}

test "abi binding exports direct layout constants for published structs" {
    try std.testing.expectEqual(@as(usize, 8), boundary_header_size);
    try std.testing.expectEqual(@as(usize, 4), boundary_header_align);
    try std.testing.expectEqual(@as(usize, 0), boundary_header_size_offset);
    try std.testing.expectEqual(@as(usize, 4), boundary_header_abi_version_offset);
    try std.testing.expectEqual(@as(usize, 6), boundary_header_flags_offset);

    try std.testing.expectEqual(@as(usize, 8), export_status_size);
    try std.testing.expectEqual(@as(usize, 4), export_status_align);
    try std.testing.expectEqual(@as(usize, 0), export_status_code_offset);
    try std.testing.expectEqual(@as(usize, 4), export_status_facility_offset);
    try std.testing.expectEqual(@as(usize, 6), export_status_flags_offset);

    try std.testing.expectEqual(@as(usize, 4), interop_policy_size);
    try std.testing.expectEqual(@as(usize, 1), interop_policy_align);
    try std.testing.expectEqual(@as(usize, 0), interop_policy_panic_mode_offset);
    try std.testing.expectEqual(@as(usize, 1), interop_policy_allocator_mode_offset);
    try std.testing.expectEqual(@as(usize, 2), interop_policy_unsafe_scope_offset);
    try std.testing.expectEqual(@as(usize, 3), interop_policy_reserved_offset);

    const raw_notifier_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_notifier_size = std.mem.alignForward(usize, raw_notifier_size, @alignOf(usize));
    try std.testing.expectEqual(expected_notifier_size, notifier_block_size);
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), notifier_block_align);
    try std.testing.expectEqual(@as(usize, 0), notifier_block_notifier_call_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), notifier_block_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), notifier_block_priority_offset);
}

test "abi binding default header stays canonical" {
    const header = defaultHeader(0x41);

    try std.testing.expectEqual(@as(u32, @intCast(boundary_header_size)), header.size);
    try std.testing.expectEqual(@as(u16, ABI_VERSION), header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x41), header.flags);

    try std.testing.expectEqual(boundary_header_size, @sizeOf(BoundaryHeader));
    try std.testing.expectEqual(boundary_header_align, @alignOf(BoundaryHeader));
    try std.testing.expectEqual(boundary_header_size_offset, @offsetOf(BoundaryHeader, "size"));
    try std.testing.expectEqual(boundary_header_abi_version_offset, @offsetOf(BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(boundary_header_flags_offset, @offsetOf(BoundaryHeader, "flags"));
}

test "abi binding boundary header helpers keep compatibility explicit" {
    const default_header = defaultHeader(0x15);
    const expanded = compatibleHeader(@as(u32, @intCast(boundary_header_size + 8)), 0x15);
    const future = BoundaryHeader{
        .size = @as(u32, @intCast(boundary_header_size + 16)),
        .abi_version = ABI_VERSION,
        .flags = 0xA1,
    };
    const stale = BoundaryHeader{
        .size = @as(u32, @intCast(boundary_header_size)),
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

    try std.testing.expectEqual(@as(u32, @intCast(boundary_header_size)), canonicalized.size);
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
    try std.testing.expect(interopPolicyReservedClear(policy));
    try std.testing.expect(interopPolicyIsRecognized(policy));
}

test "abi binding interop-policy byte decoders stay explicit" {
    try std.testing.expectEqual(@as(?PanicMode, .abort), panicModeFromByte(PANIC_ABORT));
    try std.testing.expectEqual(@as(?PanicMode, .bug), panicModeFromByte(PANIC_BUG));
    try std.testing.expectEqual(@as(?PanicMode, .warn), panicModeFromByte(PANIC_WARN));
    try std.testing.expectEqual(@as(?PanicMode, null), panicModeFromByte(9));
    try std.testing.expect(panicModeIsKnown(PANIC_ABORT));
    try std.testing.expect(!panicModeIsKnown(9));

    try std.testing.expectEqual(@as(?AllocatorMode, .caller_provided), allocatorModeFromByte(ALLOC_CALLER_PROVIDED));
    try std.testing.expectEqual(@as(?AllocatorMode, .kernel_heap), allocatorModeFromByte(ALLOC_KERNEL_HEAP));
    try std.testing.expectEqual(@as(?AllocatorMode, .arena), allocatorModeFromByte(ALLOC_ARENA));
    try std.testing.expectEqual(@as(?AllocatorMode, null), allocatorModeFromByte(9));
    try std.testing.expect(allocatorModeIsKnown(ALLOC_CALLER_PROVIDED));
    try std.testing.expect(!allocatorModeIsKnown(9));

    try std.testing.expectEqual(@as(?UnsafeScope, .none), unsafeScopeFromByte(UNSAFE_NONE));
    try std.testing.expectEqual(@as(?UnsafeScope, .volatile_mmio), unsafeScopeFromByte(UNSAFE_VOLATILE_MMIO));
    try std.testing.expectEqual(@as(?UnsafeScope, .raw_pointer_bridge), unsafeScopeFromByte(UNSAFE_RAW_POINTER_BRIDGE));
    try std.testing.expectEqual(@as(?UnsafeScope, null), unsafeScopeFromByte(9));
    try std.testing.expect(unsafeScopeIsKnown(UNSAFE_NONE));
    try std.testing.expect(!unsafeScopeIsKnown(9));
}

test "abi binding interop-policy recognition stays explicit" {
    const valid = InteropPolicy{
        .panic_mode = PANIC_BUG,
        .allocator_mode = ALLOC_KERNEL_HEAP,
        .unsafe_scope = UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_panic = InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = ALLOC_KERNEL_HEAP,
        .unsafe_scope = UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_allocator = InteropPolicy{
        .panic_mode = PANIC_BUG,
        .allocator_mode = 9,
        .unsafe_scope = UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const unknown_scope = InteropPolicy{
        .panic_mode = PANIC_BUG,
        .allocator_mode = ALLOC_KERNEL_HEAP,
        .unsafe_scope = 9,
        .reserved = 0,
    };
    const reserved = InteropPolicy{
        .panic_mode = PANIC_WARN,
        .allocator_mode = ALLOC_ARENA,
        .unsafe_scope = UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };

    try std.testing.expect(interopPolicyReservedClear(valid));
    try std.testing.expect(!interopPolicyReservedClear(reserved));

    try std.testing.expectEqual(@as(?PanicMode, .bug), panicModeFromInteropPolicy(valid));
    try std.testing.expectEqual(@as(?AllocatorMode, .kernel_heap), allocatorModeFromInteropPolicy(valid));
    try std.testing.expectEqual(@as(?UnsafeScope, .volatile_mmio), unsafeScopeFromInteropPolicy(valid));
    try std.testing.expect(interopPolicyIsRecognized(valid));

    try std.testing.expectEqual(@as(?PanicMode, null), panicModeFromInteropPolicy(unknown_panic));
    try std.testing.expectEqual(@as(?AllocatorMode, null), allocatorModeFromInteropPolicy(unknown_allocator));
    try std.testing.expectEqual(@as(?UnsafeScope, null), unsafeScopeFromInteropPolicy(unknown_scope));
    try std.testing.expectEqual(@as(?PanicMode, null), panicModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?AllocatorMode, null), allocatorModeFromInteropPolicy(reserved));
    try std.testing.expectEqual(@as(?UnsafeScope, null), unsafeScopeFromInteropPolicy(reserved));
    try std.testing.expect(!interopPolicyIsRecognized(unknown_panic));
    try std.testing.expect(!interopPolicyIsRecognized(unknown_allocator));
    try std.testing.expect(!interopPolicyIsRecognized(unknown_scope));
    try std.testing.expect(!interopPolicyIsRecognized(reserved));
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
    const unknown_facility = ExportStatus{
        .code = 0,
        .facility = 9,
        .flags = 0,
    };

    try std.testing.expect(statusIsOk(ok));
    try std.testing.expect(statusHasKnownFacility(ok));
    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(u16, FACILITY_HELPERS), ok.facility);
    try std.testing.expectEqual(@as(u16, 0), ok.flags);

    try std.testing.expect(!statusIsOk(negative));
    try std.testing.expect(statusHasKnownFacility(negative));
    try std.testing.expectEqual(@as(i32, -22), negative.code);
    try std.testing.expectEqual(@as(u16, FACILITY_KERNEL), negative.facility);
    try std.testing.expectEqual(@as(u16, STATUS_FLAG_ERROR), negative.flags);

    try std.testing.expect(statusIsOk(positive));
    try std.testing.expect(statusHasKnownFacility(positive));
    try std.testing.expectEqual(@as(i32, 7), positive.code);
    try std.testing.expectEqual(@as(u16, FACILITY_DRIVERS), positive.facility);
    try std.testing.expectEqual(@as(u16, 0), positive.flags);
    try std.testing.expect(!statusIsOk(flagged_positive));
    try std.testing.expect(statusHasKnownFacility(flagged_positive));
    try std.testing.expect(!statusHasKnownFacility(unknown_facility));
}

test "abi binding enums stay aligned with exported constants" {
    try std.testing.expectEqual(@as(u16, FACILITY_KERNEL), @intFromEnum(Facility.kernel));
    try std.testing.expectEqual(@as(u16, FACILITY_HELPERS), @intFromEnum(Facility.helpers));
    try std.testing.expectEqual(@as(u16, FACILITY_DRIVERS), @intFromEnum(Facility.drivers));
    try std.testing.expectEqual(@as(?Facility, .kernel), facilityFromInt(FACILITY_KERNEL));
    try std.testing.expectEqual(@as(?Facility, .helpers), facilityFromInt(FACILITY_HELPERS));
    try std.testing.expectEqual(@as(?Facility, .drivers), facilityFromInt(FACILITY_DRIVERS));
    try std.testing.expectEqual(@as(?Facility, null), facilityFromInt(9));
    try std.testing.expect(facilityIsKnown(FACILITY_KERNEL));
    try std.testing.expect(facilityIsKnown(FACILITY_HELPERS));
    try std.testing.expect(facilityIsKnown(FACILITY_DRIVERS));
    try std.testing.expect(!facilityIsKnown(9));

    try std.testing.expectEqual(@as(u8, PANIC_ABORT), @intFromEnum(PanicMode.abort));
    try std.testing.expectEqual(@as(u8, PANIC_BUG), @intFromEnum(PanicMode.bug));
    try std.testing.expectEqual(@as(u8, PANIC_WARN), @intFromEnum(PanicMode.warn));

    try std.testing.expectEqual(@as(u8, ALLOC_CALLER_PROVIDED), @intFromEnum(AllocatorMode.caller_provided));
    try std.testing.expectEqual(@as(u8, ALLOC_KERNEL_HEAP), @intFromEnum(AllocatorMode.kernel_heap));
    try std.testing.expectEqual(@as(u8, ALLOC_ARENA), @intFromEnum(AllocatorMode.arena));

    try std.testing.expectEqual(@as(u8, UNSAFE_NONE), @intFromEnum(UnsafeScope.none));
    try std.testing.expectEqual(@as(u8, UNSAFE_VOLATILE_MMIO), @intFromEnum(UnsafeScope.volatile_mmio));
    try std.testing.expectEqual(@as(u8, UNSAFE_RAW_POINTER_BRIDGE), @intFromEnum(UnsafeScope.raw_pointer_bridge));

    try std.testing.expectEqual(@as(u32, RBTREE_ROOT_VIEW_FLAG_CACHED), @as(u32, 1));
    try std.testing.expectEqual(@as(u32, RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID), @as(u32, 2));

    try std.testing.expectEqual(@as(u32, NOTIFIER_DONE), @intFromEnum(NotifierResult.done));
    try std.testing.expectEqual(@as(u32, NOTIFIER_OK), @intFromEnum(NotifierResult.ok));
    try std.testing.expectEqual(@as(u32, NOTIFIER_STOP), @intFromEnum(NotifierResult.stop));
}

test "abi binding rbtree root view keeps the published layout" {
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), rbtree_root_view_align);
    try std.testing.expectEqual(@as(usize, 0), rbtree_root_view_root_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), rbtree_root_view_cached_leftmost_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), rbtree_root_view_flags_offset);
    try std.testing.expectEqual(rbtree_root_view_align, @alignOf(RbtreeRootView));
    try std.testing.expectEqual(rbtree_root_view_size, @sizeOf(RbtreeRootView));
}

test "abi binding rbtree root view keeps cached-leftmost validity explicit" {
    const uncached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = RBTREE_ROOT_VIEW_FLAG_CACHED | RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const rootless_uncached = RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached_without_leftmost_addr = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = RBTREE_ROOT_VIEW_FLAG_CACHED | RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const cached_without_leftmost_flag = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = RBTREE_ROOT_VIEW_FLAG_CACHED,
    };
    const leftmost_without_cached_flag = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    try std.testing.expect(rbtreeRootViewIsValid(uncached));
    try std.testing.expect(!rbtreeRootViewIsCached(uncached));
    try std.testing.expect(!rbtreeRootViewHasLeftmost(uncached));

    try std.testing.expect(rbtreeRootViewIsValid(cached));
    try std.testing.expect(rbtreeRootViewIsCached(cached));
    try std.testing.expect(rbtreeRootViewHasLeftmost(cached));

    try std.testing.expect(!rbtreeRootViewIsValid(rootless_uncached));
    try std.testing.expect(!rbtreeRootViewIsValid(cached_without_leftmost_addr));
    try std.testing.expect(!rbtreeRootViewIsValid(cached_without_leftmost_flag));
    try std.testing.expect(!rbtreeRootViewIsValid(leftmost_without_cached_flag));
}

test "abi binding rbtree root view canonicalization preserves valid shapes and clears malformed ones" {
    const uncached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = RBTREE_ROOT_VIEW_FLAG_CACHED,
    };
    const cached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = 0,
    };
    const rootless = RbtreeRootView{
        .root = 0,
        .cached_leftmost = 0x0800,
        .flags = RBTREE_ROOT_VIEW_FLAG_CACHED | RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    const canonical_uncached = canonicalizeRbtreeRootView(uncached);
    const canonical_cached = canonicalizeRbtreeRootView(cached);
    const canonical_rootless = canonicalizeRbtreeRootView(rootless);

    try std.testing.expectEqual(@as(u32, 0), canonical_uncached.flags);
    try std.testing.expect(rbtreeRootViewIsValid(canonical_uncached));

    try std.testing.expectEqual(
        @as(u32, RBTREE_ROOT_VIEW_FLAG_CACHED | RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID),
        canonical_cached.flags,
    );
    try std.testing.expect(rbtreeRootViewIsValid(canonical_cached));

    try std.testing.expectEqual(@as(usize, 0), canonical_rootless.root);
    try std.testing.expectEqual(@as(usize, 0), canonical_rootless.cached_leftmost);
    try std.testing.expectEqual(@as(u32, 0), canonical_rootless.flags);
}

test "abi binding notifier result and hlist-first relays stay aligned with notifier helpers" {
    try std.testing.expectEqual(@as(?NotifierResult, .done), notifierResultFromInt(NOTIFIER_DONE));
    try std.testing.expectEqual(@as(?NotifierResult, .ok), notifierResultFromInt(NOTIFIER_OK));
    try std.testing.expectEqual(@as(?NotifierResult, .stop), notifierResultFromInt(NOTIFIER_STOP));
    try std.testing.expectEqual(@as(?NotifierResult, null), notifierResultFromInt(7));

    try std.testing.expectEqual(notifier_abi.resultFromInt(NOTIFIER_DONE), notifierResultFromInt(NOTIFIER_DONE));
    try std.testing.expectEqual(notifier_abi.resultIsKnown(NOTIFIER_OK), notifierResultIsKnown(NOTIFIER_OK));
    try std.testing.expectEqual(notifier_abi.resultIsKnown(7), notifierResultIsKnown(7));
    try std.testing.expect(notifierResultIsKnown(NOTIFIER_STOP));
    try std.testing.expect(!notifierResultIsKnown(7));
    try std.testing.expectEqual(notifier_abi.resultStopsChainValue(NOTIFIER_STOP), notifierResultStopsChainValue(NOTIFIER_STOP));
    try std.testing.expect(!notifierResultStopsChainValue(NOTIFIER_DONE));

    const stop = notifierResultFromInt(NOTIFIER_STOP) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(notifier_abi.resultStopsChain(.stop), notifierResultStopsChain(stop));
    try std.testing.expect(notifierResultStopsChain(stop));

    const empty_hlist = HListHead{ .first = 0 };
    try std.testing.expectEqual(notifier_abi.firstPprevMatchesHead(&empty_hlist), hlistFirstPprevMatchesHead(&empty_hlist));

    var hlist_head = HListHead{ .first = 0 };
    var hlist_node = HListNode{ .next = 0, .pprev = 0 };
    hlist_head.first = @intFromPtr(&hlist_node);
    hlist_node.pprev = @intFromPtr(&hlist_head.first);

    try std.testing.expectEqual(notifier_abi.firstPprevMatchesHead(&hlist_head), hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(hlistFirstPprevMatchesHead(&hlist_head));

    hlist_node.pprev = 0;
    try std.testing.expectEqual(notifier_abi.firstPprevMatchesHead(&hlist_head), hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(!hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(!hlistFirstPprevMatchesHead(null));
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

test "abi binding chrdev structs keep the published layout" {
    try std.testing.expectEqual(export_status_size, @sizeOf(ExportStatus));
    try std.testing.expectEqual(export_status_align, @alignOf(ExportStatus));
    try std.testing.expectEqual(export_status_code_offset, @offsetOf(ExportStatus, "code"));
    try std.testing.expectEqual(export_status_facility_offset, @offsetOf(ExportStatus, "facility"));
    try std.testing.expectEqual(export_status_flags_offset, @offsetOf(ExportStatus, "flags"));

    try std.testing.expectEqual(interop_policy_size, @sizeOf(InteropPolicy));
    try std.testing.expectEqual(interop_policy_align, @alignOf(InteropPolicy));
    try std.testing.expectEqual(interop_policy_panic_mode_offset, @offsetOf(InteropPolicy, "panic_mode"));
    try std.testing.expectEqual(interop_policy_allocator_mode_offset, @offsetOf(InteropPolicy, "allocator_mode"));
    try std.testing.expectEqual(interop_policy_unsafe_scope_offset, @offsetOf(InteropPolicy, "unsafe_scope"));
    try std.testing.expectEqual(interop_policy_reserved_offset, @offsetOf(InteropPolicy, "reserved"));

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

test "abi binding notifier and list layouts stay aligned with the exported ABI header" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_notifier_size = std.mem.alignForward(
        usize,
        raw_size,
        @alignOf(NotifierBlock),
    );
    const raw_increase_size = (@sizeOf(usize) * 2) + (@sizeOf(i32) * 2);
    const expected_increase_size = std.mem.alignForward(
        usize,
        raw_increase_size,
        @alignOf(ChainPriorityIncrease),
    );

    try std.testing.expectEqual(@sizeOf(NotifierChainPriorityIncrease), @sizeOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@alignOf(NotifierChainPriorityIncrease), @alignOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, @alignOf(usize)), notifier_block_align);
    try std.testing.expectEqual(notifier_block_notifier_call_offset, @offsetOf(NotifierBlock, "notifier_call"));
    try std.testing.expectEqual(notifier_block_next_offset, @offsetOf(NotifierBlock, "next"));
    try std.testing.expectEqual(notifier_block_priority_offset, @offsetOf(NotifierBlock, "priority"));
    try std.testing.expectEqual(expected_notifier_size, notifier_block_size);

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ChainPriorityIncrease));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ChainPriorityIncrease, "previous_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ChainPriorityIncrease, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(ChainPriorityIncrease, "previous_priority"));
    try std.testing.expectEqual(@as(usize, (@sizeOf(usize) * 2) + @sizeOf(i32)), @offsetOf(ChainPriorityIncrease, "current_priority"));
    try std.testing.expectEqual(expected_increase_size, @sizeOf(ChainPriorityIncrease));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListHead, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListHead, "prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(ListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListHead));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListHead, "first"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @sizeOf(HListHead));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListNode));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListNode, "next"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListNode, "pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @sizeOf(HListNode));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(ListBackLinkBreak));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(ListBackLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(ListBackLinkBreak, "expected_prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(ListBackLinkBreak, "actual_prev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(ListBackLinkBreak));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), @alignOf(HListPrevLinkBreak));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(HListPrevLinkBreak, "current_index"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), @offsetOf(HListPrevLinkBreak, "expected_pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), @offsetOf(HListPrevLinkBreak, "actual_pprev"));
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 3), @sizeOf(HListPrevLinkBreak));
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
    try std.testing.expect(hlistFirstPprevMatchesHead(&hlist_head));
    try std.testing.expect(hlistHasConsistentPrevLinks(&hlist_head));
    try std.testing.expectEqual(@as(?HListPrevLinkBreak, null), firstBrokenPrevLink(&hlist_head));
}