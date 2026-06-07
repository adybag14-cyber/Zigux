const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const RawCase = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
};

fn expectExclusiveSlot(case: RawCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "raw xarray samples classify into exactly one public slot lane" {
    const max_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    const cases = [_]RawCase{
        .{
            .name = "null raw zero",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .name = "inline zero tag",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged = true,
            .value = 0,
        },
        .{
            .name = "low pointer gap",
            .raw = 2,
            .kind = .pointer,
            .tagged = false,
            .pointer = 2,
        },
        .{
            .name = "inline one tag",
            .raw = try xa_value.makeValue(1),
            .kind = .value,
            .tagged = true,
            .value = 1,
        },
        .{
            .name = "highest inline value",
            .raw = max_value_raw,
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "pointer just below err floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged = false,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged = true,
            .error_code = -4095,
        },
        .{
            .name = "interior errno",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .tagged = true,
            .error_code = -512,
        },
        .{
            .name = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .tagged = true,
            .error_code = -1,
        },
    };

    for (cases) |case| {
        std.debug.assert(case.name.len != 0);
        try expectExclusiveSlot(case);
    }
}

test "err_ptr priority keeps rejected inline aliases out of the value lane" {
    const overlapping_value = xa_value.safe_inline_limit + 1;
    const overlapping_raw = (overlapping_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(overlapping_raw);

    try std.testing.expectEqual(err_ptr.err_floor, overlapping_raw);
    try std.testing.expectEqual(SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expect(slot.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(overlapping_value));
}
