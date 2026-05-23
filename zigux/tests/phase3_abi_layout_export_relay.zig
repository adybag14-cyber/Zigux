const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");
const layout_assert = @import("layout_assert");

test "phase3 abi layout/export relay keeps published layout assertions wired into the shim surface" {
    const canonical = export_shim.canonicalHeader(0x41);

    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();
    layout_assert.assertInteropPolicyModeValues();

    try testing.expectEqual(@sizeOf(abi.BoundaryHeader), @sizeOf(export_shim.BoundaryHeader));
    try testing.expectEqual(@alignOf(abi.BoundaryHeader), @alignOf(export_shim.BoundaryHeader));
    try testing.expectEqual(@sizeOf(abi.ExportStatus), @sizeOf(export_shim.ExportStatus));
    try testing.expectEqual(@alignOf(abi.ExportStatus), @alignOf(export_shim.ExportStatus));
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), export_shim.abi_version);
    try testing.expectEqual(@as(u32, @sizeOf(export_shim.BoundaryHeader)), export_shim.header_size);
    try testing.expect(std.meta.eql(abi.defaultHeader(0x41), canonical));
}

test "phase3 abi layout/export relay keeps boundary-header predicate and canonicalization relays aligned" {
    const canonical = abi.defaultHeader(0x52);
    const expanded = export_shim.compatibleHeader(@sizeOf(abi.BoundaryHeader) + 16, 0x52);
    const undersized = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader) - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x52,
    };
    const stale = abi.BoundaryHeader{
        .size = @sizeOf(abi.BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x52,
    };
    const canonicalized = export_shim.canonicalizeHeader(expanded);

    try testing.expect(export_shim.headerIsCanonical(canonical));
    try testing.expect(export_shim.headerIsCompatible(canonical));
    try testing.expect(!export_shim.extendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(canonical));

    try testing.expect(!export_shim.headerIsCanonical(expanded));
    try testing.expect(export_shim.headerIsCompatible(expanded));
    try testing.expect(export_shim.extendsBoundary(expanded));
    try testing.expectEqual(@as(u32, 16), export_shim.requestedExtraBytes(expanded));

    try testing.expect(!export_shim.headerIsCanonical(undersized));
    try testing.expect(!export_shim.headerIsCompatible(undersized));
    try testing.expect(!export_shim.extendsBoundary(undersized));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(undersized));

    try testing.expect(!export_shim.headerIsCanonical(stale));
    try testing.expect(!export_shim.headerIsCompatible(stale));
    try testing.expect(!export_shim.extendsBoundary(stale));
    try testing.expectEqual(@as(u32, 0), export_shim.requestedExtraBytes(stale));

    try testing.expect(std.meta.eql(canonicalized, export_shim.canonicalizeHeader(expanded)));
    try testing.expect(std.meta.eql(export_shim.compatibleHeader(expanded.size, expanded.flags), expanded));
}
