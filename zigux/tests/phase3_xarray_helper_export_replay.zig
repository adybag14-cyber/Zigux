const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");
const uapi_dev_t = @import("uapi_dev_t");
const uapi_version = @import("uapi_version");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");
const header_family = @import("header_family_binding");
const export_shim = @import("export_shim");

test "xarray helper cluster and export shim stay runnable from one focused replay" {
    const value_slot = try xarray_slot_view.fromValue(29);
    const encoded = export_shim.encodeDeviceNumber(export_shim.makeDevTFields(11, 29)) orelse unreachable;

    try testing.expect(value_slot.isValue());
    try testing.expectEqual(@as(?usize, 29), value_slot.value());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(value_slot.rawValue()));
    try testing.expectEqual(uapi_dev_t.makeDeviceNumber(11, 29), encoded);
    try testing.expectEqual(dev_t.makeDeviceNumber(11, 29), encoded);
}

test "err_ptr-tagged xarray entries stay distinct while export boundary validation stays open" {
    const err_slot = xarray_slot_view.fromErrorCode(-22);
    const header = export_shim.canonicalHeader(0x31);
    const status = export_shim.validateBoundaryHeader(header);

    try testing.expect(err_slot.isErr());
    try testing.expectEqual(@as(?isize, -22), err_slot.errorCode());
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(err_slot.rawValue()));
    try testing.expect(export_shim.statusIsOk(status));
    try testing.expectEqual(version.current(), export_shim.currentVersion());
}

test "header-family relay stays aligned while xarray tagged values remain below err_ptr space" {
    const expanded = header_family.compatibleBoundaryHeader(
        @sizeOf(header_family.BoundaryHeader) + 8,
        0x41,
    );
    const raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), slot.value());
    try testing.expect(raw < err_ptr.err_floor);
    try testing.expect(header_family.boundaryHeaderIsCompatible(expanded));
    try testing.expect(header_family.boundaryHeaderExtendsBoundary(expanded));
    try testing.expectEqual(@as(u32, 8), header_family.boundaryHeaderRequestedExtraBytes(expanded));
    try testing.expect(version.eql(version.current(), uapi_version.current()));
}

test "pointer-like xarray slots stay separate from export-side dev_t decoding" {
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);
    const decoded = export_shim.decodeDeviceNumber(uapi_dev_t.makeDeviceNumber(11, 29));

    try testing.expect(pointer_slot.isPointer());
    try testing.expectEqual(@as(?usize, 0x1000), pointer_slot.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(pointer_slot.rawValue()));
    try testing.expectEqual(@as(u32, 11), decoded.major);
    try testing.expectEqual(@as(u32, 29), decoded.minor);
}
