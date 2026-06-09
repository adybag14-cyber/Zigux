const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ExpectedSlot = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
    tagged: bool = false,
};

const KindCounts = struct {
    nulls: usize = 0,
    values: usize = 0,
    errors: usize = 0,
    pointers: usize = 0,

    fn record(self: *KindCounts, kind: SlotKind) void {
        switch (kind) {
            .null => self.nulls += 1,
            .value => self.values += 1,
            .err => self.errors += 1,
            .pointer => self.pointers += 1,
        }
    }
};

fn expectSlotCase(expected: ExpectedSlot) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try std.testing.expectEqual(expected.kind, slot.kind());
    try std.testing.expectEqual(expected.raw, slot.rawValue());
    try std.testing.expectEqual(expected.kind == .null, slot.isNull());
    try std.testing.expectEqual(expected.kind == .value, slot.isValue());
    try std.testing.expectEqual(expected.kind == .err, slot.isErr());
    try std.testing.expectEqual(expected.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(expected.value, slot.value());
    try std.testing.expectEqual(expected.error_code, slot.errorCode());
    try std.testing.expectEqual(expected.pointer, slot.pointerValue());
    try std.testing.expectEqual(expected.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(expected.tagged, xarray_slot_view.isTaggedInternalEntry(expected.raw));
}

test "interleaved slot walk preserves lane order counts and decoder closure" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_small = try xa_value.makeValue(29);
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);
    const low_pointer = @as(usize, 2);
    const mid_pointer = @as(usize, 0x1000);
    const floor_gap_pointer = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_busy = err_ptr.fromErrorCode(-16);
    const err_top = err_ptr.fromErrorCode(-1);

    const cases = [_]ExpectedSlot{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "inline_zero", .raw = inline_zero, .kind = .value, .value = 0, .tagged = true },
        .{ .name = "low_pointer", .raw = low_pointer, .kind = .pointer, .pointer = low_pointer },
        .{ .name = "err_busy", .raw = err_busy, .kind = .err, .error_code = -16, .tagged = true },
        .{ .name = "inline_small", .raw = inline_small, .kind = .value, .value = 29, .tagged = true },
        .{ .name = "mid_pointer", .raw = mid_pointer, .kind = .pointer, .pointer = mid_pointer },
        .{ .name = "inline_limit", .raw = inline_limit, .kind = .value, .value = xa_value.safe_inline_limit, .tagged = true },
        .{ .name = "floor_gap_pointer", .raw = floor_gap_pointer, .kind = .pointer, .pointer = floor_gap_pointer },
        .{ .name = "err_floor", .raw = err_floor, .kind = .err, .error_code = -4095, .tagged = true },
        .{ .name = "err_top", .raw = err_top, .kind = .err, .error_code = -1, .tagged = true },
    };

    var counts = KindCounts{};
    var value_sum: usize = 0;
    var error_sum: isize = 0;
    var pointer_xor: usize = 0;

    for (cases) |case| {
        try expectSlotCase(case);
        counts.record(case.kind);
        value_sum += case.value orelse 0;
        error_sum += case.error_code orelse 0;
        pointer_xor ^= case.pointer orelse 0;
    }

    try std.testing.expectEqual(@as(usize, 1), counts.nulls);
    try std.testing.expectEqual(@as(usize, 3), counts.values);
    try std.testing.expectEqual(@as(usize, 3), counts.errors);
    try std.testing.expectEqual(@as(usize, 3), counts.pointers);
    try std.testing.expectEqual(xa_value.safe_inline_limit + 29, value_sum);
    try std.testing.expectEqual(@as(isize, -4112), error_sum);
    try std.testing.expectEqual(low_pointer ^ mid_pointer ^ floor_gap_pointer, pointer_xor);
}

test "slot constructors and raw views agree when mixed in one replay table" {
    const raw_cases = [_]ExpectedSlot{
        .{ .name = "constructor_null", .raw = xarray_slot_view.nullSlot().rawValue(), .kind = .null },
        .{ .name = "constructor_value", .raw = (try xarray_slot_view.fromValue(7)).rawValue(), .kind = .value, .value = 7, .tagged = true },
        .{ .name = "constructor_pointer", .raw = xarray_slot_view.fromPointer(0x2000).rawValue(), .kind = .pointer, .pointer = 0x2000 },
        .{ .name = "constructor_error", .raw = xarray_slot_view.fromErrorCode(-22).rawValue(), .kind = .err, .error_code = -22, .tagged = true },
        .{ .name = "raw_rejected_inline_alias", .raw = (xa_value.safe_inline_limit + 1) << 1 | xa_value.value_tag_mask, .kind = .err, .error_code = -4095, .tagged = true },
    };

    for (raw_cases) |case| {
        try expectSlotCase(case);
    }

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(xa_value.safe_inline_limit + 1));
    try std.testing.expectEqual(err_ptr.err_floor, raw_cases[4].raw);
}
