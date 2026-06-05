const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const RawCase = struct {
    raw: usize,
    expected_kind: SlotKind,
    expected_tagged: bool,
};

fn rejectedValueRaw(offset: usize) usize {
    return ((xa_value.safe_inline_limit + 1 + offset) << 1) | xa_value.value_tag_mask;
}

fn expectRawCase(case: RawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.expected_kind, slot.kind());
    try std.testing.expectEqual(case.expected_tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(case.raw), slot.isTaggedEntry());

    switch (case.expected_kind) {
        .null => {
            try std.testing.expect(slot.isNull());
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => {
            try std.testing.expect(slot.isValue());
            try std.testing.expectEqual(@as(?usize, case.raw >> 1), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .err => {
            try std.testing.expect(slot.isErr());
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, err_ptr.toErrorCode(case.raw)), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => {
            try std.testing.expect(slot.isPointer());
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
        },
    }
}

test "slot-level tagged query tracks low raw xarray lanes" {
    const cases = [_]RawCase{
        .{ .raw = 0, .expected_kind = .null, .expected_tagged = false },
        .{ .raw = 1, .expected_kind = .value, .expected_tagged = true },
        .{ .raw = 2, .expected_kind = .pointer, .expected_tagged = false },
        .{ .raw = 3, .expected_kind = .value, .expected_tagged = true },
        .{ .raw = 4, .expected_kind = .pointer, .expected_tagged = false },
        .{ .raw = 5, .expected_kind = .value, .expected_tagged = true },
    };

    for (cases) |case| {
        try expectRawCase(case);
    }
}

test "slot-level tagged query tracks inline ceiling and pointer gap" {
    const ceiling_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const cases = [_]RawCase{
        .{ .raw = ceiling_raw - 3, .expected_kind = .pointer, .expected_tagged = false },
        .{ .raw = ceiling_raw - 2, .expected_kind = .value, .expected_tagged = true },
        .{ .raw = ceiling_raw - 1, .expected_kind = .pointer, .expected_tagged = false },
        .{ .raw = ceiling_raw, .expected_kind = .value, .expected_tagged = true },
        .{ .raw = err_ptr.err_floor - 1, .expected_kind = .pointer, .expected_tagged = false },
    };

    try std.testing.expectEqual(err_ptr.err_floor - 2, ceiling_raw);

    for (cases) |case| {
        try expectRawCase(case);
    }
}

test "slot-level tagged query tracks rejected aliases and even err neighbors" {
    const cases = [_]RawCase{
        .{ .raw = rejectedValueRaw(0), .expected_kind = .err, .expected_tagged = true },
        .{ .raw = rejectedValueRaw(0) + 1, .expected_kind = .err, .expected_tagged = true },
        .{ .raw = rejectedValueRaw(11), .expected_kind = .err, .expected_tagged = true },
        .{ .raw = rejectedValueRaw(11) + 1, .expected_kind = .err, .expected_tagged = true },
        .{ .raw = err_ptr.fromErrorCode(-1), .expected_kind = .err, .expected_tagged = true },
    };

    for (cases) |case| {
        try std.testing.expect(err_ptr.isErrValue(case.raw));
        try expectRawCase(case);
    }
}

test "constructor paths preserve tagged state across all slot kinds" {
    const cases = [_]xarray_slot_view.SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(0),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-4095),
        xarray_slot_view.fromErrorCode(-1),
    };

    for (cases) |slot| {
        const replay = xarray_slot_view.fromRaw(slot.rawValue());

        try std.testing.expectEqual(slot.kind(), replay.kind());
        try std.testing.expectEqual(slot.isTaggedEntry(), replay.isTaggedEntry());
        try std.testing.expectEqual(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()), slot.isTaggedEntry());
    }
}
