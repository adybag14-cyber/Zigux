const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const PointerGapCase = struct {
    label: []const u8,
    raw: usize,
    previous_value: ?usize = null,
    next_value: ?usize = null,
};

fn expectPointerGap(row: PointerGapCase) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expect(row.raw != 0);
    try std.testing.expectEqual(@as(usize, 0), row.raw & xa_value.value_tag_mask);
    try std.testing.expect(err_ptr.isOkValue(row.raw));
    try std.testing.expect(!err_ptr.isErrValue(row.raw));
    try std.testing.expect(!xa_value.isValue(row.raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(row.raw));

    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(SlotKind.pointer, slot.kind());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isErr());
    try std.testing.expect(slot.isPointer());
    try std.testing.expect(!slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, row.raw), slot.pointerValue());

    if (row.previous_value) |value| {
        const previous_raw = try xa_value.makeValue(value);
        try std.testing.expectEqual(previous_raw + 1, row.raw);
        try std.testing.expect(xa_value.isValue(previous_raw));
    }
    if (row.next_value) |value| {
        const next_raw = try xa_value.makeValue(value);
        try std.testing.expectEqual(row.raw + 1, next_raw);
        try std.testing.expect(xa_value.isValue(next_raw));
    }
}

test "even raw stride gaps stay pointer-like between adjacent inline values" {
    const cases = [_]PointerGapCase{
        .{
            .label = "gap after inline zero",
            .raw = 2,
            .previous_value = 0,
            .next_value = 1,
        },
        .{
            .label = "middle inline stride gap",
            .raw = try xa_value.makeValue(2048) + 1,
            .previous_value = 2048,
            .next_value = 2049,
        },
        .{
            .label = "gap before highest inline value",
            .raw = (try xa_value.makeValue(xa_value.safe_inline_limit)) - 1,
            .previous_value = xa_value.safe_inline_limit - 1,
            .next_value = xa_value.safe_inline_limit,
        },
    };

    for (cases) |row| {
        try expectPointerGap(row);
    }
}

test "pointer constructor accepts sampled even gaps and preserves raw identity" {
    const raws = [_]usize{
        2,
        try xa_value.makeValue(4096) + 1,
        err_ptr.err_floor - 1,
    };

    for (raws) |raw| {
        const constructed = xarray_slot_view.fromPointer(raw);
        const decoded = xarray_slot_view.fromRaw(constructed.rawValue());

        try std.testing.expectEqual(raw, constructed.rawValue());
        try std.testing.expectEqual(raw, decoded.rawValue());
        try std.testing.expectEqual(SlotKind.pointer, constructed.kind());
        try std.testing.expectEqual(SlotKind.pointer, decoded.kind());
        try std.testing.expectEqual(@as(?usize, raw), constructed.pointerValue());
        try std.testing.expectEqual(@as(?usize, raw), decoded.pointerValue());
        try std.testing.expect(!constructed.isTaggedEntry());
        try std.testing.expect(!decoded.isTaggedEntry());
    }
}

test "neighboring odd raws remain value or err slots while the even gap is pointer" {
    const high_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const high_gap_raw = high_value_raw + 1;
    const err_floor_raw = high_gap_raw + 1;

    try std.testing.expectEqual(err_ptr.err_floor - 2, high_value_raw);
    try std.testing.expectEqual(err_ptr.err_floor - 1, high_gap_raw);
    try std.testing.expectEqual(err_ptr.err_floor, err_floor_raw);

    try std.testing.expectEqual(SlotKind.value, xarray_slot_view.fromRaw(high_value_raw).kind());
    try std.testing.expectEqual(SlotKind.pointer, xarray_slot_view.fromRaw(high_gap_raw).kind());
    try std.testing.expectEqual(SlotKind.err, xarray_slot_view.fromRaw(err_floor_raw).kind());
    try std.testing.expectEqual(@as(?usize, xa_value.safe_inline_limit), xarray_slot_view.fromRaw(high_value_raw).value());
    try std.testing.expectEqual(@as(?usize, high_gap_raw), xarray_slot_view.fromRaw(high_gap_raw).pointerValue());
    try std.testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(err_floor_raw).errorCode());
}
