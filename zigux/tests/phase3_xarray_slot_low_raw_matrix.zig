const std = @import("std");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LowRawCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    pointer: ?usize = null,
    tagged_internal: bool,
};

fn expectLowRawCase(case: LowRawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(false, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "xarray slot view keeps zero and the first low raws in separate lanes" {
    const cases = [_]LowRawCase{
        .{ .raw = 0, .kind = .null, .tagged_internal = false },
        .{ .raw = 1, .kind = .value, .value = 0, .tagged_internal = true },
        .{ .raw = 2, .kind = .pointer, .pointer = 2, .tagged_internal = false },
        .{ .raw = 3, .kind = .value, .value = 1, .tagged_internal = true },
        .{ .raw = 4, .kind = .pointer, .pointer = 4, .tagged_internal = false },
        .{ .raw = 5, .kind = .value, .value = 2, .tagged_internal = true },
        .{ .raw = 8, .kind = .pointer, .pointer = 8, .tagged_internal = false },
    };

    for (cases) |case| {
        try expectLowRawCase(case);
    }
}

test "public low constructors agree with the raw low-lane matrix" {
    const null_slot = xarray_slot_view.nullSlot();
    const zero_value = try xarray_slot_view.fromValue(0);
    const one_value = try xarray_slot_view.fromValue(1);
    const low_pointer = xarray_slot_view.fromPointer(2);

    try std.testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, null_slot.kind());
    try std.testing.expectEqual(false, xarray_slot_view.isTaggedInternalEntry(null_slot.rawValue()));

    try std.testing.expectEqual(try xa_value.makeValue(0), zero_value.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, zero_value.kind());
    try std.testing.expectEqual(@as(?usize, 0), zero_value.value());

    try std.testing.expectEqual(try xa_value.makeValue(1), one_value.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, one_value.kind());
    try std.testing.expectEqual(@as(?usize, 1), one_value.value());

    try std.testing.expectEqual(@as(usize, 2), low_pointer.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, low_pointer.kind());
    try std.testing.expectEqual(@as(?usize, 2), low_pointer.pointerValue());
}
