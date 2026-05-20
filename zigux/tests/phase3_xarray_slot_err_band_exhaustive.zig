const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const err_top = err_ptr.fromErrorCode(-1);
const odd_err_raw_count_expected = (err_ptr.max_errno + 1) / 2;
const even_err_raw_count_expected = err_ptr.max_errno / 2;

test "every raw in the err_ptr band stays in the xarray-slot err lane" {
    var raw = err_ptr.err_floor;
    var expected_code = -@as(isize, @intCast(err_ptr.max_errno));
    var count: usize = 0;

    while (true) {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, expected_code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
        try testing.expect(!xa_value.isValue(raw));

        count += 1;
        if (raw == err_top) break;
        raw += 1;
        expected_code += 1;
    }

    try testing.expectEqual(err_ptr.max_errno, count);
}

test "odd err raws stay rejected aliases while even err raws stay between them" {
    var raw = err_ptr.err_floor;
    var odd_count: usize = 0;
    var even_count: usize = 0;
    var previous_odd_raw: ?usize = null;

    while (true) {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expect(slot.isErr());
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(slot.errorCode().?).rawValue());

        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            odd_count += 1;
            try testing.expect(!xa_value.canRepresent(raw >> 1));
            try testing.expect(!xa_value.isValue(raw));

            if (previous_odd_raw) |previous| {
                try testing.expectEqual(previous + 2, raw);
            }
            previous_odd_raw = raw;
        } else {
            even_count += 1;
            try testing.expect(raw > err_ptr.err_floor);
            try testing.expect(raw < err_top);
            try testing.expectEqual(@as(usize, 1), (raw - 1) & xa_value.value_tag_mask);
            try testing.expectEqual(@as(usize, 1), (raw + 1) & xa_value.value_tag_mask);
            try testing.expectEqual(raw - 1, xarray_slot_view.fromErrorCode(slot.errorCode().? - 1).rawValue());
            try testing.expectEqual(raw + 1, xarray_slot_view.fromErrorCode(slot.errorCode().? + 1).rawValue());
            try testing.expectEqual(((raw - 1) >> 1) + 1, (raw + 1) >> 1);
        }

        if (raw == err_top) break;
        raw += 1;
    }

    try testing.expectEqual(odd_err_raw_count_expected, odd_count);
    try testing.expectEqual(even_err_raw_count_expected, even_count);
    try testing.expectEqual(err_top, previous_odd_raw.?);
}

test "error constructors and raw rereads agree for the full err_ptr band" {
    var code = -@as(isize, @intCast(err_ptr.max_errno));
    var expected_raw = err_ptr.err_floor;

    while (true) {
        const constructed = xarray_slot_view.fromErrorCode(code);
        const reread = xarray_slot_view.fromRaw(expected_raw);

        try testing.expectEqual(expected_raw, constructed.rawValue());
        try testing.expectEqual(expected_raw, reread.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, constructed.kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, reread.kind());
        try testing.expectEqual(@as(?isize, code), constructed.errorCode());
        try testing.expectEqual(@as(?isize, code), reread.errorCode());

        if (code == -1) break;
        code += 1;
        expected_raw += 1;
    }

    try testing.expectEqual(err_top, expected_raw);
}
