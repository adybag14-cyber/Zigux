const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SeamGapCase = struct {
    raw: usize,
    lower_neighbor: usize,
    upper_neighbor: usize,
    expected_lower_value: ?usize = null,
    expected_upper_value: ?usize = null,
    expected_upper_error: ?isize = null,
};

fn expectPointer(raw: usize) !void {
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, slot.kind());
    try testing.expectEqual(raw, slot.rawValue());
    try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
}

test "pointer gaps below the seam stay explicit while neighboring tagged raws keep their lanes" {
    const cases = [_]SeamGapCase{
        .{
            .raw = err_ptr.err_floor - 5,
            .lower_neighbor = err_ptr.err_floor - 6,
            .upper_neighbor = err_ptr.err_floor - 4,
            .expected_lower_value = xa_value.safe_inline_limit - 2,
            .expected_upper_value = xa_value.safe_inline_limit - 1,
        },
        .{
            .raw = err_ptr.err_floor - 3,
            .lower_neighbor = err_ptr.err_floor - 4,
            .upper_neighbor = err_ptr.err_floor - 2,
            .expected_lower_value = xa_value.safe_inline_limit - 1,
            .expected_upper_value = xa_value.safe_inline_limit,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .lower_neighbor = err_ptr.err_floor - 2,
            .upper_neighbor = err_ptr.err_floor,
            .expected_lower_value = xa_value.safe_inline_limit,
            .expected_upper_error = -4095,
        },
    };

    for (cases) |case| {
        try expectPointer(case.raw);
        try testing.expectEqual(case.raw - 1, case.lower_neighbor);
        try testing.expectEqual(case.raw + 1, case.upper_neighbor);

        const lower_slot = xarray_slot_view.fromRaw(case.lower_neighbor);
        try testing.expectEqual(xarray_slot_view.SlotKind.value, lower_slot.kind());
        try testing.expectEqual(case.expected_lower_value, lower_slot.value());

        const upper_slot = xarray_slot_view.fromRaw(case.upper_neighbor);
        if (case.expected_upper_value) |expected_value| {
            try testing.expectEqual(xarray_slot_view.SlotKind.value, upper_slot.kind());
            try testing.expectEqual(@as(?usize, expected_value), upper_slot.value());
            try testing.expectEqual(@as(?isize, null), upper_slot.errorCode());
        } else {
            try testing.expectEqual(xarray_slot_view.SlotKind.err, upper_slot.kind());
            try testing.expectEqual(@as(?usize, null), upper_slot.value());
            try testing.expectEqual(case.expected_upper_error, upper_slot.errorCode());
        }
    }
}

test "pointer constructor and raw rereads agree for seam gaps and ordinary even pointers" {
    const raws = [_]usize{
        2,
        0x1000,
        0x1002,
        err_ptr.err_floor - 5,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    for (raws) |raw| {
        const constructed = xarray_slot_view.fromPointer(raw);
        const reread = xarray_slot_view.fromRaw(raw);

        try expectPointer(raw);
        try testing.expectEqual(raw, constructed.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, constructed.kind());
        try testing.expectEqual(reread.kind(), constructed.kind());
        try testing.expectEqual(reread.pointerValue(), constructed.pointerValue());
    }
}

test "even pointer-like raws below the seam never reopen value or err decoders" {
    const pointer_gaps = [_]usize{
        err_ptr.err_floor - 7,
        err_ptr.err_floor - 5,
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    for (pointer_gaps, 0..) |raw, index| {
        try expectPointer(raw);
        if (index != 0) {
            try testing.expectEqual(pointer_gaps[index - 1] + 2, raw);
        }

        const adjacent_value = raw + 1;
        if (adjacent_value < err_ptr.err_floor) {
            try testing.expect(xa_value.isValue(adjacent_value));
            try testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(adjacent_value).kind());
        } else {
            try testing.expect(err_ptr.isErrValue(adjacent_value));
            try testing.expectEqual(xarray_slot_view.SlotKind.err, xarray_slot_view.fromRaw(adjacent_value).kind());
        }
    }
}
