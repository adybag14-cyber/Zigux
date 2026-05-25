const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const odd_err_count: usize = (err_ptr.max_errno + 1) / 2;
const even_err_count: usize = err_ptr.max_errno / 2;

fn oddErrorCode(index: usize) isize {
    return -@as(isize, @intCast(err_ptr.max_errno)) + @as(isize, @intCast(index * 2));
}

fn evenErrorCode(index: usize) isize {
    return oddErrorCode(index) + 1;
}

test "error constructor keeps every odd err code on the rejected tagged ladder" {
    var index: usize = 0;
    while (index < odd_err_count) : (index += 1) {
        const code = oddErrorCode(index);
        const slot = xarray_slot_view.fromErrorCode(code);
        const raw = slot.rawValue();

        try testing.expectEqual(err_ptr.fromErrorCode(code), raw);
        try testing.expectEqual(err_ptr.err_floor + (index * 2), raw);
        try testing.expectEqual(@as(usize, 1), raw & xa_value.value_tag_mask);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "error constructor keeps every even err code on the untagged half of the band" {
    var index: usize = 0;
    while (index < even_err_count) : (index += 1) {
        const code = evenErrorCode(index);
        const slot = xarray_slot_view.fromErrorCode(code);
        const raw = slot.rawValue();

        try testing.expectEqual(err_ptr.fromErrorCode(code), raw);
        try testing.expectEqual(err_ptr.err_floor + 1 + (index * 2), raw);
        try testing.expectEqual(@as(usize, 0), raw & xa_value.value_tag_mask);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
        try testing.expect(slot.isErr());
        try testing.expectEqual(@as(?isize, code), slot.errorCode());
        try testing.expectEqual(@as(?usize, null), slot.value());
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
        try testing.expect(err_ptr.isErrValue(raw));
        try testing.expect(!xa_value.isValue(raw));
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(raw));
    }
}

test "constructor-produced odd even neighbors stay adjacent across representative windows" {
    const indices = [_]usize{ 0, 1, odd_err_count / 2, odd_err_count - 2 };

    for (indices) |index| {
        const odd_code = oddErrorCode(index);
        const even_code = odd_code + 1;
        const odd_slot = xarray_slot_view.fromErrorCode(odd_code);
        const even_slot = xarray_slot_view.fromErrorCode(even_code);
        const odd_raw = odd_slot.rawValue();
        const even_raw = even_slot.rawValue();

        try testing.expectEqual(odd_raw + 1, even_raw);
        try testing.expectEqual(@as(usize, 1), odd_raw & xa_value.value_tag_mask);
        try testing.expectEqual(@as(usize, 0), even_raw & xa_value.value_tag_mask);
        try testing.expectEqual(xarray_slot_view.SlotKind.err, odd_slot.kind());
        try testing.expectEqual(xarray_slot_view.SlotKind.err, even_slot.kind());
        try testing.expectEqual(@as(?isize, odd_code), odd_slot.errorCode());
        try testing.expectEqual(@as(?isize, even_code), even_slot.errorCode());
        try testing.expectEqual(@as(?usize, null), odd_slot.value());
        try testing.expectEqual(@as(?usize, null), even_slot.value());
        try testing.expectEqual(@as(?usize, null), odd_slot.pointerValue());
        try testing.expectEqual(@as(?usize, null), even_slot.pointerValue());
    }
}
