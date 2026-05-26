const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    slot: xarray_slot_view.SlotView,
    expected_kind: xarray_slot_view.SlotKind,
    expected_tagged: bool,
    expected_ok: bool,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
};

fn expectSlotState(slot: xarray_slot_view.SlotView, case: Case) !void {
    const raw = slot.rawValue();

    try testing.expectEqual(case.expected_kind, slot.kind());
    try testing.expectEqual(case.expected_tagged, xarray_slot_view.isTaggedInternalEntry(raw));
    try testing.expectEqual(case.expected_ok, err_ptr.isOkValue(raw));
    try testing.expectEqual(!case.expected_ok, err_ptr.isErrValue(raw));
    try testing.expectEqual(case.expected_value, slot.value());
    try testing.expectEqual(case.expected_error, slot.errorCode());
    try testing.expectEqual(case.expected_pointer, slot.pointerValue());
    try testing.expectEqual(case.expected_kind == .value, xa_value.isValue(raw));

    switch (case.expected_kind) {
        .null => {
            try testing.expect(slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
        },
        .value => {
            try testing.expect(!slot.isNull());
            try testing.expect(slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(case.expected_value.?, xa_value.toValue(raw));
        },
        .err => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(slot.isErr());
            try testing.expect(!slot.isPointer());
            try testing.expectEqual(case.expected_error.?, err_ptr.toErrorCode(raw));
        },
        .pointer => {
            try testing.expect(!slot.isNull());
            try testing.expect(!slot.isValue());
            try testing.expect(!slot.isErr());
            try testing.expect(slot.isPointer());
        },
    }
}

fn expectRoundTrip(case: Case) !void {
    const raw = case.slot.rawValue();
    const reread = xarray_slot_view.fromRaw(raw);

    _ = case.name;

    try expectSlotState(case.slot, case);
    try testing.expectEqual(raw, reread.rawValue());
    try expectSlotState(reread, case);
}

test "constructor outputs survive a raw roundtrip without crossing slot lanes" {
    const cases = [_]Case{
        .{
            .name = "null",
            .slot = xarray_slot_view.nullSlot(),
            .expected_kind = .null,
            .expected_tagged = false,
            .expected_ok = true,
        },
        .{
            .name = "inline_zero",
            .slot = try xarray_slot_view.fromValue(0),
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = 0,
        },
        .{
            .name = "inline_small",
            .slot = try xarray_slot_view.fromValue(29),
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = 29,
        },
        .{
            .name = "inline_limit",
            .slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "pointer_gap",
            .slot = xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_ok = true,
            .expected_pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "ordinary_pointer",
            .slot = xarray_slot_view.fromPointer(0x1000),
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_ok = true,
            .expected_pointer = 0x1000,
        },
        .{
            .name = "err_floor",
            .slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -4095,
        },
        .{
            .name = "err_nomem",
            .slot = xarray_slot_view.fromErrorCode(-12),
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -12,
        },
        .{
            .name = "err_top",
            .slot = xarray_slot_view.fromErrorCode(-1),
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -1,
        },
    };

    for (cases) |case| {
        try expectRoundTrip(case);
    }
}

test "seam-adjacent raws stay stable when viewed repeatedly through fromRaw" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const gap_raw = err_ptr.err_floor - 1;
    const err_floor_raw = err_ptr.err_floor;
    const err_next_raw = err_ptr.err_floor + 1;

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expectEqual(inline_limit_raw + 1, gap_raw);
    try testing.expectEqual(gap_raw + 1, err_floor_raw);
    try testing.expectEqual(err_floor_raw + 1, err_next_raw);

    const cases = [_]Case{
        .{
            .name = "inline_limit_raw",
            .slot = xarray_slot_view.fromRaw(inline_limit_raw),
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_ok = true,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "gap_raw",
            .slot = xarray_slot_view.fromRaw(gap_raw),
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_ok = true,
            .expected_pointer = gap_raw,
        },
        .{
            .name = "err_floor_raw",
            .slot = xarray_slot_view.fromRaw(err_floor_raw),
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -4095,
        },
        .{
            .name = "err_next_raw",
            .slot = xarray_slot_view.fromRaw(err_next_raw),
            .expected_kind = .err,
            .expected_tagged = true,
            .expected_ok = false,
            .expected_error = -4094,
        },
    };

    for (cases) |case| {
        try expectRoundTrip(case);
    }
}

test "rejected inline overlap roundtrips as the err floor once viewed as a raw slot" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const overlapping_slot = xarray_slot_view.fromRaw(overlapping_raw);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-4095);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try testing.expectEqual(err_floor_slot.rawValue(), overlapping_slot.rawValue());

    try expectRoundTrip(.{
        .name = "overlap_alias",
        .slot = overlapping_slot,
        .expected_kind = .err,
        .expected_tagged = true,
        .expected_ok = false,
        .expected_error = -4095,
    });
}
