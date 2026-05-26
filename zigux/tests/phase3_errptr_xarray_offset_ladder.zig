const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LadderCase = struct {
    offset: usize,
    value_raw: usize,
    pointer_raw: usize,
    err_raw: usize,
};

fn ladderCase(offset: usize) !LadderCase {
    const value = xa_value.safe_inline_limit - offset;
    const value_raw = try xa_value.makeValue(value);
    return .{
        .offset = offset,
        .value_raw = value_raw,
        .pointer_raw = value_raw + 1,
        .err_raw = err_ptr.err_floor + offset,
    };
}

test "offset ladder keeps the inline tail and err band aligned by the same seam distance" {
    const ladder = [_]LadderCase{
        try ladderCase(0),
        try ladderCase(1),
        try ladderCase(2),
        try ladderCase(3),
    };

    for (ladder) |case| {
        try testing.expectEqual(err_ptr.err_floor - (case.offset * 2) - 2, case.value_raw);
        try testing.expectEqual(case.value_raw + 1, case.pointer_raw);
        try testing.expectEqual(err_ptr.err_floor + case.offset, case.err_raw);

        try testing.expectEqual(xa_value.safe_inline_limit - case.offset, xa_value.toValue(case.value_raw));
        try testing.expectEqual(-@as(isize, @intCast(err_ptr.max_errno - case.offset)), err_ptr.toErrorCode(case.err_raw));
    }
}

test "offset ladder keeps value pointer and err rereads on distinct slot lanes" {
    const ladder = [_]LadderCase{
        try ladderCase(0),
        try ladderCase(1),
        try ladderCase(2),
        try ladderCase(3),
    };

    for (ladder) |case| {
        const value_slot = xarray_slot_view.fromRaw(case.value_raw);
        const pointer_slot = xarray_slot_view.fromRaw(case.pointer_raw);
        const err_slot = xarray_slot_view.fromRaw(case.err_raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.value, value_slot.kind());
        try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit - case.offset), value_slot.value());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.value_raw));

        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try testing.expectEqual(@as(?usize, case.pointer_raw), pointer_slot.pointerValue());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.pointer_raw));

        try testing.expectEqual(xarray_slot_view.SlotKind.err, err_slot.kind());
        try testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno - case.offset))), err_slot.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.err_raw));
    }
}

test "constructor outputs land on the same ladder anchors as direct raw rereads" {
    const ladder = [_]LadderCase{
        try ladderCase(0),
        try ladderCase(1),
        try ladderCase(2),
        try ladderCase(3),
    };

    for (ladder) |case| {
        const constructed_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit - case.offset);
        const constructed_pointer = xarray_slot_view.fromPointer(case.pointer_raw);
        const constructed_err = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno - case.offset)));

        try testing.expectEqual(case.value_raw, constructed_value.rawValue());
        try testing.expectEqual(case.pointer_raw, constructed_pointer.rawValue());
        try testing.expectEqual(case.err_raw, constructed_err.rawValue());

        try testing.expectEqual(constructed_value.kind(), xarray_slot_view.fromRaw(case.value_raw).kind());
        try testing.expectEqual(constructed_pointer.kind(), xarray_slot_view.fromRaw(case.pointer_raw).kind());
        try testing.expectEqual(constructed_err.kind(), xarray_slot_view.fromRaw(case.err_raw).kind());
    }
}
