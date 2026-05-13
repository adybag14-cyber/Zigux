const std = @import("std");

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");

test "phase3 abi keeps starter header and status layouts explicit" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.BoundaryHeader));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.BoundaryHeader, "abi_version"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.BoundaryHeader, "flags"));

    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try std.testing.expectEqual(@as(usize, 4), @sizeOf(abi.InteropPolicy));
    try std.testing.expectEqual(@as(usize, 1), @alignOf(abi.InteropPolicy));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.InteropPolicy, "panic_mode"));
    try std.testing.expectEqual(@as(usize, 1), @offsetOf(abi.InteropPolicy, "allocator_mode"));
    try std.testing.expectEqual(@as(usize, 2), @offsetOf(abi.InteropPolicy, "unsafe_scope"));
    try std.testing.expectEqual(@as(usize, 3), @offsetOf(abi.InteropPolicy, "reserved"));
}

test "phase3 abi keeps exported status helpers and compatibility rules reviewable" {
    const canonical = export_shim.boundaryHeader(0x41);
    const future_compatible = export_shim.compatibleHeader(export_shim.header_size + 16, 0x41);
    const version_mismatch = export_shim.versionedHeader(
        export_shim.header_size,
        export_shim.abi_version + 1,
        0x41,
    );

    const ok_status = export_shim.compatibilityStatus(canonical, -22, .kernel);
    try std.testing.expect(export_shim.isOk(ok_status));
    try std.testing.expectEqual(@as(i32, 0), ok_status.code);
    try std.testing.expectEqual(@as(u16, 0), ok_status.flags);

    const future_status = export_shim.compatibilityStatus(future_compatible, -75, .helpers);
    try std.testing.expect(export_shim.isOk(future_status));
    try std.testing.expectEqual(@as(i32, 0), future_status.code);

    const rejected = export_shim.compatibilityStatus(version_mismatch, -71, .drivers);
    try std.testing.expect(!export_shim.isOk(rejected));
    try std.testing.expectEqual(@as(i32, -71), rejected.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), rejected.flags);
}

test "phase3 abi keeps exported constants and family markers present" {
    try std.testing.expectEqual(@as(u16, 1), abi.FACILITY_KERNEL);
    try std.testing.expectEqual(@as(u16, 2), abi.FACILITY_HELPERS);
    try std.testing.expectEqual(@as(u16, 3), abi.FACILITY_DRIVERS);
    try std.testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
    try std.testing.expectEqual(@as(u8, 0), abi.PANIC_ABORT);
    try std.testing.expectEqual(@as(u8, 2), abi.ALLOC_ARENA);
    try std.testing.expectEqual(@as(u8, 2), abi.UNSAFE_RAW_POINTER_BRIDGE);

    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"),
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"),
    );

    try std.testing.expectEqual(
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"),
    );
}

test "phase3 abi keeps dev_t sample encoding and kernel relay status explicit" {
    const minor_bits: u5 = 20;
    const minor_mask: u32 = 1_048_575;
    const max_major: u32 = 4_095;
    const sample_major: u32 = 42;
    const sample_minor: u32 = 7;
    const range_count: u32 = 4;

    const encoded = export_shim.encodeDeviceNumber(sample_major, sample_minor, .kernel);
    try std.testing.expect(export_shim.isOk(encoded.status));
    try std.testing.expectEqual(@as(u32, 44_040_199), encoded.value);
    try std.testing.expectEqual(@as(u32, sample_major), encoded.value >> minor_bits);
    try std.testing.expectEqual(@as(u32, sample_minor), encoded.value & minor_mask);

    const range_last = export_shim.lastDeviceNumberInRange(sample_major, sample_minor, range_count, .helpers);
    try std.testing.expect(export_shim.isOk(range_last.status));
    try std.testing.expect(sample_minor + range_count - 1 <= minor_mask);
    try std.testing.expectEqual(@as(u32, 44_040_202), range_last.value);

    const bad_major = export_shim.encodeDeviceNumber(max_major + 1, sample_minor, .drivers);
    try std.testing.expect(!export_shim.isOk(bad_major.status));
    try std.testing.expectEqual(@as(i32, -22), bad_major.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), bad_major.status.flags);

    const bad_range = export_shim.lastDeviceNumberInRange(sample_major, minor_mask - 1, 3, .helpers);
    try std.testing.expect(!export_shim.isOk(bad_range.status));
    try std.testing.expectEqual(@as(i32, -34), bad_range.status.code);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), bad_range.status.flags);
}
