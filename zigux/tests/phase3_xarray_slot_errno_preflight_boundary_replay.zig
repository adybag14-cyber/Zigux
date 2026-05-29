const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Probe = struct {
    code: isize,
    can_construct_err: bool,
};

fn canConstructErrSlot(code: isize) bool {
    return code <= -1 and code >= -@as(isize, @intCast(err_ptr.max_errno));
}

fn expectConstructedErr(code: isize) !void {
    const slot = xarray_slot_view.fromErrorCode(code);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expectEqual(err_ptr.fromErrorCode(code), slot.rawValue());
    try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(err_ptr.isErrValue(slot.rawValue()));
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(slot.rawValue()));
}

test "errno preflight admits only the xarray err constructor range" {
    const probes = [_]Probe{
        .{ .code = -4096, .can_construct_err = false },
        .{ .code = -4095, .can_construct_err = true },
        .{ .code = -4094, .can_construct_err = true },
        .{ .code = -1, .can_construct_err = true },
        .{ .code = 0, .can_construct_err = false },
        .{ .code = 1, .can_construct_err = false },
    };

    for (probes) |probe| {
        try std.testing.expectEqual(probe.can_construct_err, canConstructErrSlot(probe.code));
        if (probe.can_construct_err) {
            try expectConstructedErr(probe.code);
        }
    }
}

test "rejected errno neighbors remain outside the xarray err lane" {
    const below_floor_raw: usize = @bitCast(@as(isize, -4096));
    const zero_raw: usize = @bitCast(@as(isize, 0));
    const lowest_err = xarray_slot_view.fromErrorCode(-4095);
    const highest_err = xarray_slot_view.fromErrorCode(-1);

    try std.testing.expectEqual(err_ptr.err_floor - 1, below_floor_raw);
    try std.testing.expectEqual(@as(usize, 0), zero_raw);

    const below_floor = xarray_slot_view.fromRaw(below_floor_raw);
    const zero = xarray_slot_view.fromRaw(zero_raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, below_floor.kind());
    try std.testing.expectEqual(@as(?usize, below_floor_raw), below_floor.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), below_floor.errorCode());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(below_floor.rawValue()));

    try std.testing.expectEqual(xarray_slot_view.SlotKind.null, zero.kind());
    try std.testing.expect(zero.isNull());
    try std.testing.expectEqual(@as(?isize, null), zero.errorCode());
    try std.testing.expectEqual(@as(?usize, null), zero.pointerValue());
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(zero.rawValue()));

    try std.testing.expectEqual(err_ptr.err_floor, lowest_err.rawValue());
    try std.testing.expectEqual(@as(usize, ~@as(usize, 0)), highest_err.rawValue());
}

test "preflight boundary stays separate from xa_value admission" {
    const top_value = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const overlapping_value = xa_value.safe_inline_limit + 1;

    try std.testing.expectEqual(err_ptr.err_floor - 2, top_value.rawValue());
    try std.testing.expectEqual(xarray_slot_view.SlotKind.value, top_value.kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), top_value.value());
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(overlapping_value));
    try std.testing.expectEqual(err_ptr.err_floor, (overlapping_value << 1) | xa_value.value_tag_mask);
}
