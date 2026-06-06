const std = @import("std");
const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert");

test "core ABI layout assertions accept the published records" {
    try layout_assert.assertBoundaryHeaderLayout();
    try layout_assert.assertExportStatusLayout();
    try layout_assert.assertInteropPolicyLayout();
    try layout_assert.assertMmioRangeLayout();
}

test "core ABI binding constants match the asserted layouts" {
    try std.testing.expectEqual(@sizeOf(abi.BoundaryHeader), abi.boundary_header_size);
    try std.testing.expectEqual(@alignOf(abi.BoundaryHeader), abi.boundary_header_align);
    try std.testing.expectEqual(@offsetOf(abi.BoundaryHeader, "size"), abi.boundary_header_size_offset);
    try std.testing.expectEqual(@offsetOf(abi.BoundaryHeader, "abi_version"), abi.boundary_header_abi_version_offset);
    try std.testing.expectEqual(@offsetOf(abi.BoundaryHeader, "flags"), abi.boundary_header_flags_offset);

    try std.testing.expectEqual(@sizeOf(abi.ExportStatus), abi.export_status_size);
    try std.testing.expectEqual(@alignOf(abi.ExportStatus), abi.export_status_align);
    try std.testing.expectEqual(@offsetOf(abi.ExportStatus, "code"), abi.export_status_code_offset);
    try std.testing.expectEqual(@offsetOf(abi.ExportStatus, "facility"), abi.export_status_facility_offset);
    try std.testing.expectEqual(@offsetOf(abi.ExportStatus, "flags"), abi.export_status_flags_offset);

    try std.testing.expectEqual(@sizeOf(abi.InteropPolicy), abi.interop_policy_size);
    try std.testing.expectEqual(@alignOf(abi.InteropPolicy), abi.interop_policy_align);
    try std.testing.expectEqual(@offsetOf(abi.InteropPolicy, "panic_mode"), abi.interop_policy_panic_mode_offset);
    try std.testing.expectEqual(@offsetOf(abi.InteropPolicy, "allocator_mode"), abi.interop_policy_allocator_mode_offset);
    try std.testing.expectEqual(@offsetOf(abi.InteropPolicy, "unsafe_scope"), abi.interop_policy_unsafe_scope_offset);
    try std.testing.expectEqual(@offsetOf(abi.InteropPolicy, "reserved"), abi.interop_policy_reserved_offset);
}

test "core ABI layout assertions keep mismatch causes separate" {
    const Header = extern struct {
        size: u32,
        abi_version: u16,
        flags: u16,
    };
    const Status = extern struct {
        code: i32,
        facility: u16,
        flags: u16,
    };
    const Policy = extern struct {
        panic_mode: u8,
        allocator_mode: u8,
        unsafe_scope: u8,
        reserved: u8,
    };

    try layout_assert.expectLayout(Header, 8, 4);
    try layout_assert.expectLayout(Status, 8, 4);
    try layout_assert.expectLayout(Policy, 4, 1);

    try std.testing.expectError(error.SizeMismatch, layout_assert.expectSize(Header, 12));
    try std.testing.expectError(error.AlignMismatch, layout_assert.expectAlign(Status, 2));
    try std.testing.expectError(error.OffsetMismatch, layout_assert.expectOffset(Policy, "reserved", 2));
}

test "MMIO range assertion follows pointer-width padding" {
    const expected_raw_size = @sizeOf(usize) + (@sizeOf(u32) * 2);
    const expected_size = std.mem.alignForward(
        usize,
        expected_raw_size,
        @alignOf(layout_assert.MmioRange),
    );

    try std.testing.expectEqual(expected_size, @sizeOf(layout_assert.MmioRange));
    try std.testing.expectEqual(@alignOf(usize), @alignOf(layout_assert.MmioRange));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(layout_assert.MmioRange, "base_addr"));
    try std.testing.expectEqual(@sizeOf(usize), @offsetOf(layout_assert.MmioRange, "length"));
    try std.testing.expectEqual(@sizeOf(usize) + @sizeOf(u32), @offsetOf(layout_assert.MmioRange, "stride"));

    try layout_assert.assertMmioRangeLayout();
}
