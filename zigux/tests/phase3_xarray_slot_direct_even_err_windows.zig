const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "representative direct even err raws stay in the err lane across floor middle and top windows" {
    const raws = [_]usize{
        err_ptr.fromErrorCode(-4094),
        err_ptr.fromErrorCode(-2048),
        err_ptr.fromErrorCode(-2),
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const code = err_ptr.toErrorCode(raw);

        try testing.expect((raw & xa_value.value_tag_mask) == 0);
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));

        try testing.expect(slot.isErr());
        try testing.expect(!slot.isNull());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "direct even err raws stay bracketed by rejected odd err aliases" {
    const raws = [_]usize{
        err_ptr.fromErrorCode(-4094),
        err_ptr.fromErrorCode(-2048),
        err_ptr.fromErrorCode(-2),
    };

    for (raws) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const lower_slot = xarray_slot_view.fromRaw(raw - 1);
        const upper_slot = xarray_slot_view.fromRaw(raw + 1);
        const code = slot.errorCode().?;

        try testing.expect((raw & xa_value.value_tag_mask) == 0);
        try testing.expect(((raw - 1) & xa_value.value_tag_mask) == xa_value.value_tag_mask);
        try testing.expect(((raw + 1) & xa_value.value_tag_mask) == xa_value.value_tag_mask);

        try testing.expect(slot.isErr());
        try testing.expect(lower_slot.isErr());
        try testing.expect(upper_slot.isErr());
        try testing.expect(!lower_slot.isValue());
        try testing.expect(!upper_slot.isValue());
        try testing.expect(!lower_slot.isPointer());
        try testing.expect(!upper_slot.isPointer());

        try testing.expectEqual(@as(?isize, code - 1), lower_slot.errorCode());
        try testing.expectEqual(@as(?isize, code + 1), upper_slot.errorCode());
    }
}

test "direct even err constructors and raw rereads agree across representative windows" {
    const codes = [_]isize{ -4094, -2048, -2 };

    for (codes) |code| {
        const constructed = xarray_slot_view.fromErrorCode(code);
        const reread = xarray_slot_view.fromRaw(constructed.rawValue());

        try testing.expectEqual(err_ptr.fromErrorCode(code), constructed.rawValue());
        try testing.expectEqual(constructed.rawValue(), reread.rawValue());
        try testing.expect((constructed.rawValue() & xa_value.value_tag_mask) == 0);
        try testing.expect(constructed.isErr());
        try testing.expect(reread.isErr());
        try testing.expectEqual(@as(?isize, code), constructed.errorCode());
        try testing.expectEqual(@as(?isize, code), reread.errorCode());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(constructed.rawValue()));
    }
}
