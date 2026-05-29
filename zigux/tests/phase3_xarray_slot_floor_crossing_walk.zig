const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const FloorCase = struct {
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
    tagged_internal: bool,
};

fn expectRawCase(case: FloorCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "xarray slot view walks cleanly across the err_ptr floor" {
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 6,
        .kind = .value,
        .value = xa_value.safe_inline_limit - 2,
        .tagged_internal = true,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 5,
        .kind = .pointer,
        .pointer = err_ptr.err_floor - 5,
        .tagged_internal = false,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 4,
        .kind = .value,
        .value = xa_value.safe_inline_limit - 1,
        .tagged_internal = true,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 3,
        .kind = .pointer,
        .pointer = err_ptr.err_floor - 3,
        .tagged_internal = false,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 2,
        .kind = .value,
        .value = xa_value.safe_inline_limit,
        .tagged_internal = true,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor - 1,
        .kind = .pointer,
        .pointer = err_ptr.err_floor - 1,
        .tagged_internal = false,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor,
        .kind = .err,
        .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
        .tagged_internal = true,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor + 1,
        .kind = .err,
        .error_code = -@as(isize, @intCast(err_ptr.max_errno - 1)),
        .tagged_internal = true,
    });
    try expectRawCase(.{
        .raw = err_ptr.err_floor + 2,
        .kind = .err,
        .error_code = -@as(isize, @intCast(err_ptr.max_errno - 2)),
        .tagged_internal = true,
    });
}

test "public constructors agree with raw floor crossing classification" {
    const top_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const top_pointer = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const floor_err = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, top_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());

    try std.testing.expectEqual(err_ptr.err_floor - 1, top_pointer.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, top_pointer.kind());
    try std.testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), top_pointer.pointerValue());

    try std.testing.expectEqual(err_ptr.err_floor, floor_err.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, floor_err.kind());
    try std.testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), floor_err.errorCode());
}
