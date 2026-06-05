const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotExpectation = struct {
    label: []const u8,
    slot: xarray_slot_view.SlotView,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    is_tagged: bool,
};

fn expectSlot(expected: SlotExpectation) !void {
    const slot = expected.slot;

    try std.testing.expectEqual(expected.raw, slot.rawValue());
    try std.testing.expectEqual(expected.kind, slot.kind());
    try std.testing.expectEqual(expected.is_tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(expected.is_tagged, xarray_slot_view.isTaggedInternalEntry(expected.raw));

    try std.testing.expectEqual(expected.kind == .null, slot.isNull());
    try std.testing.expectEqual(expected.kind == .value, slot.isValue());
    try std.testing.expectEqual(expected.kind == .err, slot.isErr());
    try std.testing.expectEqual(expected.kind == .pointer, slot.isPointer());

    const predicate_count =
        @as(u8, @intFromBool(slot.isNull())) +
        @as(u8, @intFromBool(slot.isValue())) +
        @as(u8, @intFromBool(slot.isErr())) +
        @as(u8, @intFromBool(slot.isPointer()));
    try std.testing.expectEqual(@as(u8, 1), predicate_count);

    std.testing.refAllDecls(@TypeOf(expected));
}

test "xarray slot kind table keeps enum, predicates, tags, and raw identity aligned" {
    const inline_tail_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_gap_raw = err_ptr.err_floor - 1;

    const expectations = [_]SlotExpectation{
        .{
            .label = "null raw",
            .slot = xarray_slot_view.nullSlot(),
            .raw = 0,
            .kind = .null,
            .is_tagged = false,
        },
        .{
            .label = "inline zero constructor",
            .slot = try xarray_slot_view.fromValue(0),
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .is_tagged = true,
        },
        .{
            .label = "inline tail raw",
            .slot = xarray_slot_view.fromRaw(inline_tail_raw),
            .raw = inline_tail_raw,
            .kind = .value,
            .is_tagged = true,
        },
        .{
            .label = "pointer gap raw",
            .slot = xarray_slot_view.fromRaw(pointer_gap_raw),
            .raw = pointer_gap_raw,
            .kind = .pointer,
            .is_tagged = false,
        },
        .{
            .label = "aligned pointer constructor",
            .slot = xarray_slot_view.fromPointer(0x4000),
            .raw = 0x4000,
            .kind = .pointer,
            .is_tagged = false,
        },
        .{
            .label = "err floor raw",
            .slot = xarray_slot_view.fromRaw(err_ptr.err_floor),
            .raw = err_ptr.err_floor,
            .kind = .err,
            .is_tagged = true,
        },
        .{
            .label = "errno constructor",
            .slot = xarray_slot_view.fromErrorCode(-22),
            .raw = err_ptr.fromErrorCode(-22),
            .kind = .err,
            .is_tagged = true,
        },
        .{
            .label = "top errno raw",
            .slot = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(-1)),
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .is_tagged = true,
        },
    };

    for (expectations) |expected| {
        errdefer std.debug.print("failed slot expectation: {s}\n", .{expected.label});
        try expectSlot(expected);
    }
}

test "rejected inline aliases enter the err lane before value decoding" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(rejected_raw);

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(rejected_value));
    try std.testing.expectEqual(err_ptr.err_floor, rejected_raw);
    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(slot.isTaggedEntry());
}
