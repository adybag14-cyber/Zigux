const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    expected_kind: xarray_slot_view.SlotKind,
    expected_error: ?isize = null,
    expected_value: ?usize = null,
    tagged: bool,
};

fn rejectedValueAlias(value: usize) usize {
    return (value << 1) | xa_value.value_tag_mask;
}

fn expectCase(case: Case) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.expected_kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.expected_kind == .null, slot.isNull());
    try testing.expectEqual(case.expected_kind == .value, slot.isValue());
    try testing.expectEqual(case.expected_kind == .err, slot.isErr());
    try testing.expectEqual(case.expected_kind == .pointer, slot.isPointer());
    try testing.expectEqual(case.expected_error, slot.errorCode());
    try testing.expectEqual(case.expected_value, slot.value());
    try testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
}

test "raw xarray slot stream keeps err_ptr precedence before xa_value decoding" {
    const accepted_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_floor_raw = rejectedValueAlias(xa_value.safe_inline_limit + 1);
    const rejected_top_raw = rejectedValueAlias(std.math.maxInt(usize) >> 1);

    try testing.expectEqual(err_ptr.err_floor, rejected_floor_raw);
    try testing.expectEqual(err_ptr.fromErrorCode(-1), rejected_top_raw);

    const cases = [_]Case{
        .{
            .name = "null",
            .raw = 0,
            .expected_kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline_zero",
            .raw = try xa_value.makeValue(0),
            .expected_kind = .value,
            .expected_value = 0,
            .tagged = true,
        },
        .{
            .name = "inline_limit",
            .raw = accepted_limit_raw,
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .name = "gap_below_err_floor",
            .raw = err_ptr.err_floor - 1,
            .expected_kind = .pointer,
            .tagged = false,
        },
        .{
            .name = "rejected_value_aliases_err_floor",
            .raw = rejected_floor_raw,
            .expected_kind = .err,
            .expected_error = -4095,
            .tagged = true,
        },
        .{
            .name = "ordinary_error_mid_band",
            .raw = err_ptr.fromErrorCode(-29),
            .expected_kind = .err,
            .expected_error = -29,
            .tagged = true,
        },
        .{
            .name = "rejected_value_aliases_err_top",
            .raw = rejected_top_raw,
            .expected_kind = .err,
            .expected_error = -1,
            .tagged = true,
        },
        .{
            .name = "aligned_pointer",
            .raw = 0x1000,
            .expected_kind = .pointer,
            .tagged = false,
        },
    };

    for (cases) |case| {
        try expectCase(case);
    }
}

test "accepted and rejected inline values split at the err_ptr floor" {
    const last_value_slot = xarray_slot_view.fromRaw(try xa_value.makeValue(xa_value.safe_inline_limit));
    const first_rejected_slot = xarray_slot_view.fromRaw(rejectedValueAlias(xa_value.safe_inline_limit + 1));
    const second_rejected_slot = xarray_slot_view.fromRaw(rejectedValueAlias(xa_value.safe_inline_limit + 2));

    try testing.expect(last_value_slot.isValue());
    try testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), last_value_slot.value());
    try testing.expectEqual(@as(?isize, null), last_value_slot.errorCode());

    try testing.expect(first_rejected_slot.isErr());
    try testing.expect(!first_rejected_slot.isValue());
    try testing.expectEqual(@as(?isize, -4095), first_rejected_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), first_rejected_slot.value());

    try testing.expect(second_rejected_slot.isErr());
    try testing.expect(!second_rejected_slot.isValue());
    try testing.expectEqual(@as(?isize, -4093), second_rejected_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), second_rejected_slot.value());
}
