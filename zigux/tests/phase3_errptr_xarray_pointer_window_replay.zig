const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

fn expectPointerWindowRaw(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expect(raw != 0);
    try std.testing.expect(!err_ptr.isErrValue(raw));
    try std.testing.expect(!xa_value.isValue(raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    try std.testing.expectEqual(SlotKind.pointer, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(raw, xarray_slot_view.fromPointer(raw).rawValue());
}

fn expectNonPointerRaw(raw: usize, expected_kind: SlotKind) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try std.testing.expectEqual(expected_kind, slot.kind());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
}

test "non-tagged raws below err floor stay inside the pointer window" {
    const pointer_window = [_]usize{
        0x2,
        0x1000,
        xa_value.value_tag_mask + 1,
        (try xa_value.makeValue(0)) + 1,
        (try xa_value.makeValue(1)) + 1,
        (try xa_value.makeValue(xa_value.safe_inline_limit)) + 1,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    for (pointer_window) |raw| {
        try expectPointerWindowRaw(raw);
    }
}

test "pointer window is closed by null, tagged values, and err_ptr raws" {
    const inline_zero = try xa_value.makeValue(0);
    const highest_value = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_error = err_ptr.err_floor;
    const middle_error = err_ptr.fromErrorCode(-22);
    const top_error = err_ptr.fromErrorCode(-1);

    try expectNonPointerRaw(0, .null);
    try expectNonPointerRaw(inline_zero, .value);
    try expectNonPointerRaw(highest_value, .value);
    try expectNonPointerRaw(first_error, .err);
    try expectNonPointerRaw(middle_error, .err);
    try expectNonPointerRaw(top_error, .err);
}
