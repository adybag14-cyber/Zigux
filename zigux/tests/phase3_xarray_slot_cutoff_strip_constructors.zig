const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "cutoff strip keeps contiguous raw order while constructor ownership flips only once" {
    const accepted_prev_value = xa_value.safe_inline_limit - 1;
    const accepted_top_value = xa_value.safe_inline_limit;
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const second_rejected_value = first_rejected_value + 1;

    const accepted_prev_raw = try xa_value.makeValue(accepted_prev_value);
    const accepted_top_raw = try xa_value.makeValue(accepted_top_value);
    const separator_raw = accepted_top_raw + 1;
    const err_floor_raw = err_ptr.err_floor;
    const even_err_raw = err_floor_raw + 1;
    const next_tagged_err_raw = err_floor_raw + 2;

    const cases = [_]struct {
        raw: usize,
        kind: xarray_slot_view.SlotKind,
        value: ?usize,
        error_code: ?isize,
        pointer: ?usize,
    }{
        .{ .raw = accepted_prev_raw, .kind = .value, .value = accepted_prev_value, .error_code = null, .pointer = null },
        .{ .raw = accepted_prev_raw + 1, .kind = .pointer, .value = null, .error_code = null, .pointer = accepted_prev_raw + 1 },
        .{ .raw = accepted_top_raw, .kind = .value, .value = accepted_top_value, .error_code = null, .pointer = null },
        .{ .raw = separator_raw, .kind = .pointer, .value = null, .error_code = null, .pointer = separator_raw },
        .{ .raw = err_floor_raw, .kind = .err, .value = null, .error_code = -4095, .pointer = null },
        .{ .raw = even_err_raw, .kind = .err, .value = null, .error_code = -4094, .pointer = null },
        .{ .raw = next_tagged_err_raw, .kind = .err, .value = null, .error_code = -4093, .pointer = null },
    };

    inline for (0..cases.len - 1) |index| {
        try testing.expectEqual(cases[index].raw + 1, cases[index + 1].raw);
    }

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
                try testing.expect(xarray_slot_view.isTaggedInternalEntry(case.raw));
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

    try testing.expectEqual(err_floor_raw, (first_rejected_value << 1) | xa_value.value_tag_mask);
    try testing.expectEqual(next_tagged_err_raw, (second_rejected_value << 1) | xa_value.value_tag_mask);
}

test "first two rejected xa_value payloads stay on odd err raws while the bridge raw stays even" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const second_rejected_value = first_rejected_value + 1;
    const first_raw = (first_rejected_value << 1) | xa_value.value_tag_mask;
    const bridge_raw = first_raw + 1;
    const second_raw = (second_rejected_value << 1) | xa_value.value_tag_mask;

    try testing.expectEqual(err_ptr.err_floor, first_raw);
    try testing.expectEqual(err_ptr.err_floor + 1, bridge_raw);
    try testing.expectEqual(err_ptr.err_floor + 2, second_raw);

    try testing.expect(!xa_value.canRepresent(first_rejected_value));
    try testing.expect(!xa_value.canRepresent(second_rejected_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(first_rejected_value));
    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(second_rejected_value));

    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(first_raw).errorCode());
    try testing.expectEqual(@as(?isize, -4094), xarray_slot_view.fromRaw(bridge_raw).errorCode());
    try testing.expectEqual(@as(?isize, -4093), xarray_slot_view.fromRaw(second_raw).errorCode());

    try testing.expectEqual(@as(usize, 1), first_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 0), bridge_raw & xa_value.value_tag_mask);
    try testing.expectEqual(@as(usize, 1), second_raw & xa_value.value_tag_mask);
}
