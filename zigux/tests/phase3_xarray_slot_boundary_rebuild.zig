const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "boundary seam raws rebuild only through their owning constructor lane" {
    const inline_limit_value = xa_value.safe_inline_limit;
    const inline_limit_raw = try xa_value.makeValue(inline_limit_value);
    const gap_raw = err_ptr.err_floor - 1;
    const first_err_code: isize = -@as(isize, @intCast(err_ptr.max_errno));
    const second_err_code = first_err_code + 1;

    const cases = [_]struct {
        name: []const u8,
        raw: usize,
        kind: xarray_slot_view.SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{
            .name = "inline_limit",
            .raw = inline_limit_raw,
            .kind = .value,
            .value = inline_limit_value,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = gap_raw,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = gap_raw,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .value = null,
            .error_code = first_err_code,
            .pointer = null,
        },
        .{
            .name = "second_err",
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .value = null,
            .error_code = second_err_code,
            .pointer = null,
        },
    };

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.value, slot.value());
        try testing.expectEqual(case.error_code, slot.errorCode());
        try testing.expectEqual(case.pointer, slot.pointerValue());

        switch (case.kind) {
            .value => {
                const rebuilt = try xarray_slot_view.fromValue(case.value.?);
                try testing.expectEqual(case.raw, rebuilt.rawValue());
            },
            .pointer => {
                const rebuilt = xarray_slot_view.fromPointer(case.pointer.?);
                try testing.expectEqual(case.raw, rebuilt.rawValue());
                try testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.raw));
            },
            .err => {
                const rebuilt = xarray_slot_view.fromErrorCode(case.error_code.?);
                try testing.expectEqual(case.raw, rebuilt.rawValue());
                try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
            },
            .null => unreachable,
        }
    }
}

test "first rejected xa_value payload aliases err floor and only rebuilds as an err slot" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(overlapping_raw);

    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());

    try testing.expectError(
        error.ValueWouldOverlapErrPtr,
        xarray_slot_view.fromValue(overlapping_value),
    );

    const rebuilt = xarray_slot_view.fromErrorCode(-4095);
    try testing.expectEqual(overlapping_raw, rebuilt.rawValue());
}
