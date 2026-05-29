const testing = @import("std").testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "value constructor and raw view agree across the inline range" {
    const values = [_]usize{
        0,
        1,
        29,
        xa_value.safe_inline_limit - 1,
        xa_value.safe_inline_limit,
    };

    for (values) |value| {
        const constructed = try xarray_slot_view.fromValue(value);
        const raw = try xa_value.makeValue(value);
        const viewed = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(raw, constructed.rawValue());
        try testing.expectEqual(raw, viewed.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.value, constructed.kind());
        try testing.expectEqual(constructed.kind(), viewed.kind());
        try testing.expectEqual(@as(?usize, value), constructed.value());
        try testing.expectEqual(constructed.value(), viewed.value());
        try testing.expectEqual(@as(?isize, null), constructed.errorCode());
        try testing.expectEqual(@as(?usize, null), constructed.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "error constructor and raw view agree across the err_ptr band" {
    const codes = [_]isize{ -4095, -4094, -2048, -22, -1 };

    for (codes) |code| {
        const constructed = xarray_slot_view.fromErrorCode(code);
        const raw = err_ptr.fromErrorCode(code);
        const viewed = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(raw, constructed.rawValue());
        try testing.expectEqual(raw, viewed.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, constructed.kind());
        try testing.expectEqual(constructed.kind(), viewed.kind());
        try testing.expectEqual(@as(?isize, code), constructed.errorCode());
        try testing.expectEqual(constructed.errorCode(), viewed.errorCode());
        try testing.expectEqual(@as(?usize, null), constructed.value());
        try testing.expectEqual(@as(?usize, null), constructed.pointerValue());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "pointer constructor and raw view agree for untagged nonzero gaps" {
    const pointers = [_]usize{
        2,
        4,
        0x1000,
        err_ptr.err_floor - 1,
    };

    for (pointers) |raw| {
        const constructed = xarray_slot_view.fromPointer(raw);
        const viewed = xarray_slot_view.fromRaw(raw);

        try testing.expectEqual(raw, constructed.rawValue());
        try testing.expectEqual(raw, viewed.rawValue());
        try testing.expectEqual(xarray_slot_view.SlotKind.pointer, constructed.kind());
        try testing.expectEqual(constructed.kind(), viewed.kind());
        try testing.expectEqual(@as(?usize, raw), constructed.pointerValue());
        try testing.expectEqual(constructed.pointerValue(), viewed.pointerValue());
        try testing.expectEqual(@as(?usize, null), constructed.value());
        try testing.expectEqual(@as(?isize, null), constructed.errorCode());
        try testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "null slot remains the lone zero-valued slot" {
    const constructed = xarray_slot_view.nullSlot();
    const viewed = xarray_slot_view.fromRaw(0);

    try testing.expectEqual(@as(usize, 0), constructed.rawValue());
    try testing.expectEqual(constructed.rawValue(), viewed.rawValue());
    try testing.expectEqual(xarray_slot_view.SlotKind.null, constructed.kind());
    try testing.expectEqual(constructed.kind(), viewed.kind());
    try testing.expect(constructed.isNull());
    try testing.expectEqual(@as(?usize, null), constructed.value());
    try testing.expectEqual(@as(?isize, null), constructed.errorCode());
    try testing.expectEqual(@as(?usize, null), constructed.pointerValue());
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(0));
}
