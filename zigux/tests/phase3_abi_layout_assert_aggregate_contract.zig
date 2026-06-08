const std = @import("std");
const layout_assert = @import("layout_assert_helper");
const abi = @import("abi_bindings");

test "layout assert aggregate accepts every published ABI layout" {
    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertMmioRangeLayout();
    try layout_assert.assertRbtreeRootViewLayout();
    try layout_assert.assertPublishedAbiLayouts();
}

test "layout assert aggregate rejects shifted header fields" {
    const ShiftedHeader = extern struct {
        abi_version: u16,
        flags: u16,
        size: u32,
    };

    try std.testing.expectError(
        error.OffsetMismatch,
        layout_assert.expectFieldLayout(ShiftedHeader, "size", abi.boundary_header_size_offset),
    );
    try std.testing.expectError(
        error.OffsetMismatch,
        layout_assert.expectFieldLayout(ShiftedHeader, "abi_version", abi.boundary_header_abi_version_offset),
    );
    try std.testing.expectError(
        error.OffsetMismatch,
        layout_assert.expectFieldLayout(ShiftedHeader, "flags", abi.boundary_header_flags_offset),
    );
}

test "layout assert aggregate reports size and alignment drift distinctly" {
    const PackedStatus = packed struct {
        code: i32,
        facility: u16,
        flags: u16,
    };

    try std.testing.expectError(
        error.SizeMismatch,
        layout_assert.expectSize(PackedStatus, abi.export_status_size + 4),
    );
    try std.testing.expectError(
        error.AlignMismatch,
        layout_assert.expectAlign(PackedStatus, abi.export_status_align),
    );
}

test "layout assert aggregate keeps enum byte relays aligned" {
    layout_assert.assertInteropPolicyModeValues();
    layout_assert.assertStatusAndFacilityValues();
    layout_assert.assertNotifierResultValues();
}
