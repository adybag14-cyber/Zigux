const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const LatticeRow = struct {
    name: []const u8,
    raw: usize,
    slot_kind: xarray_slot_view.SlotKind,
    tagged: bool,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
};

fn expectRow(row: LatticeRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try testing.expect(row.name.len > 0);
    try testing.expectEqual(row.raw, slot.rawValue());
    try testing.expectEqual(row.slot_kind, slot.kind());
    try testing.expectEqual(row.tagged, slot.isTaggedEntry());
    try testing.expectEqual(row.value, slot.value());
    try testing.expectEqual(row.error_code, slot.errorCode());
    try testing.expectEqual(row.pointer, slot.pointerValue());
}

test "err_ptr and xarray constants form one pointer-width lattice" {
    const max_raw = std.math.maxInt(usize);
    const expected_floor = max_raw - (err_ptr.max_errno - 1);
    const last_inline_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const first_rejected_inline_value = xa_value.safe_inline_limit + 1;
    const first_rejected_inline_raw =
        (first_rejected_inline_value << 1) | xa_value.value_tag_mask;

    try testing.expectEqual(expected_floor, err_ptr.err_floor);
    try testing.expectEqual(max_raw, err_ptr.fromErrorCode(-1));
    try testing.expectEqual(@as(isize, -1), err_ptr.toErrorCode(max_raw));
    try testing.expectEqual(err_ptr.err_floor - 2, last_inline_raw);
    try testing.expectEqual(err_ptr.err_floor, first_rejected_inline_raw);
    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected_inline_value));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(err_ptr.err_floor - 1));

    const rows = [_]LatticeRow{
        .{
            .name = "inline_zero_uses_low_tag",
            .raw = try xa_value.makeValue(0),
            .slot_kind = .value,
            .tagged = true,
            .value = 0,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "last_inline_before_pointer_gap",
            .raw = last_inline_raw,
            .slot_kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .name = "one_raw_pointer_gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .slot_kind = .pointer,
            .tagged = false,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "first_err_raw_aliases_rejected_inline",
            .raw = err_ptr.err_floor,
            .slot_kind = .err,
            .tagged = true,
            .value = null,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
            .pointer = null,
        },
        .{
            .name = "top_err_raw_is_all_bits_set",
            .raw = max_raw,
            .slot_kind = .err,
            .tagged = true,
            .value = null,
            .error_code = -1,
            .pointer = null,
        },
    };

    for (rows) |row| {
        try expectRow(row);
    }
}

test "constructor rereads preserve the same lattice rows" {
    const from_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const from_floor_error = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const from_top_error = xarray_slot_view.fromErrorCode(-1);
    const from_gap_pointer = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);

    try testing.expectEqual(err_ptr.err_floor - 2, from_value.rawValue());
    try testing.expectEqual(xa_value.safe_inline_limit, from_value.value());
    try testing.expectEqual(err_ptr.err_floor, from_floor_error.rawValue());
    try testing.expectEqual(@as(?isize, -@as(isize, @intCast(err_ptr.max_errno))), from_floor_error.errorCode());
    try testing.expectEqual(std.math.maxInt(usize), from_top_error.rawValue());
    try testing.expectEqual(@as(?isize, -1), from_top_error.errorCode());
    try testing.expectEqual(err_ptr.err_floor - 1, from_gap_pointer.rawValue());
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), from_gap_pointer.pointerValue());
}
