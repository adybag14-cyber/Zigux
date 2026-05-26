const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_tagged: bool,
    expected_value: ?usize = null,
    expected_pointer: ?usize = null,
};

fn expectOkCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    _ = case.name;
    try testing.expect(err_ptr.isOkValue(case.raw));
    try testing.expect(!err_ptr.isErrValue(case.raw));
    try testing.expect(case.raw < err_ptr.err_floor);
    try testing.expectEqual(case.expected_kind, slot.kind());
    try testing.expectEqual(case.expected_kind == .null, slot.isNull());
    try testing.expectEqual(case.expected_kind == .value, slot.isValue());
    try testing.expectEqual(case.expected_kind == .pointer, slot.isPointer());
    try testing.expect(!slot.isErr());
    try testing.expectEqual(case.expected_value, slot.value());
    try testing.expectEqual(@as(?isize, null), slot.errorCode());
    try testing.expectEqual(case.expected_pointer, slot.pointerValue());
    try testing.expectEqual(case.expected_tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try testing.expectEqual(case.expected_kind == .value, xa_value.isValue(case.raw));
}

test "ok-band matrix keeps representative non-error raws outside the err_ptr band" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_small = try xa_value.makeValue(29);
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]Case{
        .{ .name = "null", .raw = 0, .expected_kind = .null, .expected_tagged = false },
        .{ .name = "pointer_like", .raw = 64, .expected_kind = .pointer, .expected_tagged = false, .expected_pointer = 64 },
        .{ .name = "inline_zero", .raw = inline_zero, .expected_kind = .value, .expected_tagged = true, .expected_value = 0 },
        .{ .name = "inline_small", .raw = inline_small, .expected_kind = .value, .expected_tagged = true, .expected_value = 29 },
        .{
            .name = "inline_limit",
            .raw = inline_limit,
            .expected_kind = .value,
            .expected_tagged = true,
            .expected_value = xa_value.safe_inline_limit,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .expected_tagged = false,
            .expected_pointer = err_ptr.err_floor - 1,
        },
    };

    for (cases) |case| {
        try expectOkCase(case);
    }
}

test "ok-band matrix keeps constructor outputs aligned with the raw classifier on the ok side" {
    const null_slot = xarray_slot_view.nullSlot();
    const pointer_slot = xarray_slot_view.fromPointer(0x1000);
    const inline_zero_slot = try xarray_slot_view.fromValue(0);
    const inline_limit_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const gap_slot = xarray_slot_view.fromRaw(err_ptr.err_floor - 1);

    try testing.expectEqual(@as(usize, 0), null_slot.rawValue());
    try testing.expectEqual(@as(usize, 1), inline_zero_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_slot.rawValue());
    try testing.expectEqual(err_ptr.err_floor - 1, gap_slot.rawValue());

    try testing.expect(null_slot.rawValue() < inline_zero_slot.rawValue());
    try testing.expect(inline_zero_slot.rawValue() < pointer_slot.rawValue());
    try testing.expect(pointer_slot.rawValue() < inline_limit_slot.rawValue());
    try testing.expect(inline_limit_slot.rawValue() < gap_slot.rawValue());

    try expectOkCase(.{ .name = "null_slot", .raw = null_slot.rawValue(), .expected_kind = .null, .expected_tagged = false });
    try expectOkCase(.{ .name = "pointer_slot", .raw = pointer_slot.rawValue(), .expected_kind = .pointer, .expected_tagged = false, .expected_pointer = 0x1000 });
    try expectOkCase(.{ .name = "inline_zero_slot", .raw = inline_zero_slot.rawValue(), .expected_kind = .value, .expected_tagged = true, .expected_value = 0 });
    try expectOkCase(.{
        .name = "inline_limit_slot",
        .raw = inline_limit_slot.rawValue(),
        .expected_kind = .value,
        .expected_tagged = true,
        .expected_value = xa_value.safe_inline_limit,
    });
    try expectOkCase(.{
        .name = "gap_slot",
        .raw = gap_slot.rawValue(),
        .expected_kind = .pointer,
        .expected_tagged = false,
        .expected_pointer = err_ptr.err_floor - 1,
    });
}

test "ok-band matrix keeps the err floor and rejected inline values outside the ok partition" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const err_floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    const err_top_slot = xarray_slot_view.fromErrorCode(-1);
    const overlapping_slot = xarray_slot_view.fromRaw(overlapping_raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
    try testing.expectEqual(err_ptr.err_floor, overlapping_raw);

    for ([_]xarray_slot_view.SlotView{ err_floor_slot, err_top_slot, overlapping_slot }) |slot| {
        try testing.expect(!err_ptr.isOkValue(slot.rawValue()));
        try testing.expect(err_ptr.isErrValue(slot.rawValue()));
        try testing.expect(slot.isErr());
        try testing.expect(!slot.isValue());
        try testing.expect(!slot.isPointer());
        try testing.expect(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()));
    }

    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expectEqual(@as(?isize, -1), err_top_slot.errorCode());
    try testing.expectEqual(@as(?isize, -4095), overlapping_slot.errorCode());
}
