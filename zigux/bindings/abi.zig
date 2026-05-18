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

pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {
    return notifier_abi.chainHasNonincreasingPriority(head);
}

pub fn defaultHeader(flags: u16) BoundaryHeader {
    return .{
        .size = @as(u32, boundary_header_size),
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

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    var canonical = header;
    canonical.size = @as(u32, boundary_header_size);
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

    try std.testing.expectEqual(
        @as(usize, 12),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align,
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset,
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align,
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset,
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align,
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset,
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align,
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset,
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset,
    );

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

    try std.testing.expect(!headerIsCanonical(expanded));
    try std.testing.expect(headerIsCompatible(expanded));
    try std.testing.expect(!headerIsCanonical(future));
    try std.testing.expect(headerIsCompatible(future));

    try std.testing.expect(!headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!headerIsCanonical(stale));
    try std.testing.expect(!headerIsCompatible(stale));

    try std.testing.expectEqual(@as(u32, @intCast(boundary_header_size)), canonicalized.size);
    try std.testing.expectEqual(@as(u16, ABI_VERSION), canonicalized.abi_version);
    try std.testing.expectEqual(future.flags, canonicalized.flags);
    try std.testing.expect(headerIsCanonical(canonicalized));
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

    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size,
        @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align,
        @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
    );

    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size,
        @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align,
        @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"),
    );

    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size,
        @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align,
        @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"),
    );

    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size,
        @sizeOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align,
        @alignOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"),
    );
    try std.testing.expectEqual(
        chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset,
        @offsetOf(ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"),
    );
}

test "abi binding notifier block keeps the published layout" {
    const raw_size = (@sizeOf(usize) * 2) + @sizeOf(i32);
    const expected_size = std.mem.alignForward(usize, raw_size, @alignOf(usize));

    try std.testing.expectEqual(@as(usize, @alignOf(usize)), notifier_block_align);
    try std.testing.expectEqual(expected_size, notifier_block_size);
    try std.testing.expectEqual(@as(usize, 0), notifier_block_notifier_call_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize)), notifier_block_next_offset);
    try std.testing.expectEqual(@as(usize, @sizeOf(usize) * 2), notifier_block_priority_offset);
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