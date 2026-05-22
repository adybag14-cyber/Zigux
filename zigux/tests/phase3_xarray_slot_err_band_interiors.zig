const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

test "interior err windows stay contiguous across odd and even raws" {
    const lower_window_codes = [_]isize{ -3073, -3072 };
    const upper_window_codes = [_]isize{ -18, -17 };
    const lower_window_raws = [_]usize{
        err_ptr.fromErrorCode(lower_window_codes[0]),
        err_ptr.fromErrorCode(lower_window_codes[1]),
    };
    const upper_window_raws = [_]usize{
        err_ptr.fromErrorCode(upper_window_codes[0]),
        err_ptr.fromErrorCode(upper_window_codes[1]),
    };

    try testing.expect((lower_window_raws[0] & 1) == 1);
    try testing.expect((lower_window_raws[1] & 1) == 0);
    try testing.expect((upper_window_raws[0] & 1) == 0);
    try testing.expect((upper_window_raws[1] & 1) == 1);

    try testing.expectEqual(lower_window_raws[0] + 1, lower_window_raws[1]);
    try testing.expectEqual(upper_window_raws[0] + 1, upper_window_raws[1]);

    for (lower_window_codes, lower_window_raws) |code, raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }

    for (upper_window_codes, upper_window_raws) |code, raw| {
        const slot = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(raw, slot.rawValue());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "interior err constructors and raw views agree away from cutoff edges" {
    const codes = [_]isize{ -2048, -512, -34 };

    for (codes) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const from_raw = xarray_slot_view.fromRaw(raw);
        const from_code = xarray_slot_view.fromErrorCode(code);

        try testing.expect(raw > err_ptr.err_floor);
        try testing.expect(raw < err_ptr.fromErrorCode(-1));
        try testing.expectEqual(raw, from_raw.rawValue());
        try testing.expectEqual(raw, from_code.rawValue());
        try testing.expectEqual(from_raw.kind(), from_code.kind());
        try testing.expectEqual(from_raw.errorCode(), from_code.errorCode());
        try testing.expectEqual(@as(?isize, code), from_raw.errorCode());
        try testing.expectEqual(@as(?isize, code), from_code.errorCode());
        try testing.expectEqual(@as(?usize, null), from_raw.value());
        try testing.expectEqual(@as(?usize, null), from_code.value());
        try testing.expectEqual(@as(?usize, null), from_raw.pointerValue());
        try testing.expectEqual(@as(?usize, null), from_code.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}
