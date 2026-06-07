const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ConstructorCase = struct {
    name: []const u8,
    raw: usize,
    expected_kind: SlotKind,
    expected_value: ?usize = null,
    expected_error: ?isize = null,
    expected_pointer: ?usize = null,
    expected_tagged: bool,
};

fn expectRoundTrip(case: ConstructorCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);
    const reread = xarray_slot_view.fromRaw(slot.rawValue());

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.raw, reread.rawValue());
    try std.testing.expectEqual(case.expected_kind, slot.kind());
    try std.testing.expectEqual(case.expected_kind, reread.kind());
    try std.testing.expectEqual(case.expected_value, reread.value());
    try std.testing.expectEqual(case.expected_error, reread.errorCode());
    try std.testing.expectEqual(case.expected_pointer, reread.pointerValue());
    try std.testing.expectEqual(case.expected_tagged, reread.isTaggedEntry());
}

test "public constructors round-trip through raw slot classification" {
    const cases = [_]ConstructorCase{
        .{
            .name = "null",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .expected_kind = .null,
            .expected_tagged = false,
        },
        .{
            .name = "inline zero",
            .raw = (try xarray_slot_view.fromValue(0)).rawValue(),
            .expected_kind = .value,
            .expected_value = 0,
            .expected_tagged = true,
        },
        .{
            .name = "inline safe limit",
            .raw = (try xarray_slot_view.fromValue(xa_value.safe_inline_limit)).rawValue(),
            .expected_kind = .value,
            .expected_value = xa_value.safe_inline_limit,
            .expected_tagged = true,
        },
        .{
            .name = "aligned pointer",
            .raw = xarray_slot_view.fromPointer(0x2000).rawValue(),
            .expected_kind = .pointer,
            .expected_pointer = 0x2000,
            .expected_tagged = false,
        },
        .{
            .name = "high pointer below err floor",
            .raw = xarray_slot_view.fromPointer(err_ptr.err_floor - 1).rawValue(),
            .expected_kind = .pointer,
            .expected_pointer = err_ptr.err_floor - 1,
            .expected_tagged = false,
        },
        .{
            .name = "err floor",
            .raw = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))).rawValue(),
            .expected_kind = .err,
            .expected_error = -@as(isize, @intCast(err_ptr.max_errno)),
            .expected_tagged = true,
        },
        .{
            .name = "top errno",
            .raw = xarray_slot_view.fromErrorCode(-1).rawValue(),
            .expected_kind = .err,
            .expected_error = -1,
            .expected_tagged = true,
        },
    };

    for (cases) |case| {
        try std.testing.expect(case.name.len != 0);
        try expectRoundTrip(case);
    }
}

test "raw constructor rejects no public lane after constructor output reread" {
    const value_slot = try xarray_slot_view.fromValue(41);
    const err_slot = xarray_slot_view.fromErrorCode(-22);
    const pointer_slot = xarray_slot_view.fromPointer(0x4000);

    const rows = [_]xarray_slot_view.SlotView{
        xarray_slot_view.fromRaw(xarray_slot_view.nullSlot().rawValue()),
        xarray_slot_view.fromRaw(value_slot.rawValue()),
        xarray_slot_view.fromRaw(err_slot.rawValue()),
        xarray_slot_view.fromRaw(pointer_slot.rawValue()),
    };

    for (rows) |slot| {
        const lane_count = @intFromBool(slot.isNull()) +
            @intFromBool(slot.isValue()) +
            @intFromBool(slot.isErr()) +
            @intFromBool(slot.isPointer());

        try std.testing.expectEqual(@as(u2, 1), lane_count);
    }
}
