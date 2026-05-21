const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

fn expectErrStep(code: isize) !void {
    const raw = err_ptr.fromErrorCode(code);
    const slot = xarray_slot_view.fromRaw(raw);

    try testing.expect(err_ptr.isErrValue(raw));
    try testing.expect(!err_ptr.isOkValue(raw));
    try testing.expect(slot.isErr());
    try testing.expectEqual(@as(?isize, code), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expect(!xa_value.isValue(raw));
    try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
}

fn expectErrWindow(start_code: isize) !void {
    const first_raw = err_ptr.fromErrorCode(start_code);
    var previous_raw = first_raw;

    inline for (0..3) |offset| {
        const code = start_code + @as(isize, @intCast(offset));
        const raw = err_ptr.fromErrorCode(code);

        try expectErrStep(code);
        try testing.expectEqual(raw, xarray_slot_view.fromErrorCode(code).rawValue());
        try testing.expectEqual(code, err_ptr.toErrorCode(raw));

        if (offset != 0) {
            try testing.expectEqual(previous_raw + 1, raw);
        }
        previous_raw = raw;

        if ((raw & xa_value.value_tag_mask) == xa_value.value_tag_mask) {
            try testing.expect(!xa_value.isValue(raw));
        }
    }
}

test "bottom err-band raws stay on a decoded staircase across odd and even neighbors" {
    try expectErrWindow(-4095);
}

test "mid-band err raws keep consecutive decoded errors without reopening xa_value" {
    try expectErrWindow(-128);
}

test "top err-band raws keep the same staircase all the way to err_top" {
    try expectErrWindow(-3);
    try testing.expectEqual(err_ptr.fromErrorCode(-2) + 1, err_ptr.fromErrorCode(-1));
}
