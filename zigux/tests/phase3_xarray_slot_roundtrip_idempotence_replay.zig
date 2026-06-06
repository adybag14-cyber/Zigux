const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotView = xarray_slot_view.SlotView;
const SlotKind = xarray_slot_view.SlotKind;

fn expectInactiveAccessors(slot: SlotView) !void {
    switch (slot.kind()) {
        .null => {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .value => {
            try std.testing.expect(slot.value() != null);
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .err => {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expect(slot.errorCode() != null);
            try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
        },
        .pointer => {
            try std.testing.expectEqual(@as(?usize, null), slot.value());
            try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
            try std.testing.expect(slot.pointerValue() != null);
        },
    }
}

fn rebuildThroughOwningConstructor(slot: SlotView) !SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
    };
}

fn expectRoundTrip(raw: usize, expected_kind: SlotKind) !void {
    const first = xarray_slot_view.fromRaw(raw);
    const second = xarray_slot_view.fromRaw(first.rawValue());
    const rebuilt = try rebuildThroughOwningConstructor(second);
    const reread = xarray_slot_view.fromRaw(rebuilt.rawValue());

    try std.testing.expectEqual(expected_kind, first.kind());
    try std.testing.expectEqual(expected_kind, second.kind());
    try std.testing.expectEqual(expected_kind, rebuilt.kind());
    try std.testing.expectEqual(expected_kind, reread.kind());

    try std.testing.expectEqual(raw, first.rawValue());
    try std.testing.expectEqual(raw, second.rawValue());
    try std.testing.expectEqual(raw, rebuilt.rawValue());
    try std.testing.expectEqual(raw, reread.rawValue());

    try std.testing.expectEqual(
        xarray_slot_view.isTaggedInternalEntry(raw),
        reread.isTaggedEntry(),
    );
    try expectInactiveAccessors(reread);
}

test "raw xarray slots rebuild through their owning public constructor without drift" {
    const high_value_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const mid_err_raw = err_ptr.fromErrorCode(-2048);

    try expectRoundTrip(0, .null);
    try expectRoundTrip(try xa_value.makeValue(0), .value);
    try expectRoundTrip(try xa_value.makeValue(17), .value);
    try expectRoundTrip(high_value_raw, .value);
    try expectRoundTrip(2, .pointer);
    try expectRoundTrip(0x1000, .pointer);
    try expectRoundTrip(err_ptr.err_floor - 1, .pointer);
    try expectRoundTrip(err_ptr.err_floor, .err);
    try expectRoundTrip(mid_err_raw, .err);
    try expectRoundTrip(err_ptr.fromErrorCode(-1), .err);
}

test "rejected inline aliases roundtrip as err_ptr slots, not values" {
    const rejected_values = [_]usize{
        xa_value.safe_inline_limit + 1,
        xa_value.safe_inline_limit + 2,
        xa_value.safe_inline_limit + 2048,
    };

    for (rejected_values) |value| {
        const raw = (value << 1) | xa_value.value_tag_mask;
        const slot = xarray_slot_view.fromRaw(raw);
        const rebuilt = try rebuildThroughOwningConstructor(slot);

        try std.testing.expect(!xa_value.canRepresent(value));
        try std.testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(value));
        try std.testing.expectEqual(SlotKind.err, slot.kind());
        try std.testing.expectEqual(SlotKind.err, rebuilt.kind());
        try std.testing.expectEqual(raw, rebuilt.rawValue());
        try std.testing.expectEqual(err_ptr.toErrorCode(raw), rebuilt.errorCode().?);
        try std.testing.expectEqual(@as(?usize, null), rebuilt.value());
        try std.testing.expectEqual(@as(?usize, null), rebuilt.pointerValue());
    }
}

test "constructor-created slots remain raw-idempotent after repeated rereads" {
    const constructors = [_]SlotView{
        xarray_slot_view.nullSlot(),
        try xarray_slot_view.fromValue(1),
        try xarray_slot_view.fromValue(xa_value.safe_inline_limit),
        xarray_slot_view.fromPointer(0x2000),
        xarray_slot_view.fromPointer(err_ptr.err_floor - 1),
        xarray_slot_view.fromErrorCode(-22),
        xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno))),
    };

    for (constructors) |slot| {
        const first = xarray_slot_view.fromRaw(slot.rawValue());
        const second = xarray_slot_view.fromRaw(first.rawValue());
        const rebuilt = try rebuildThroughOwningConstructor(second);

        try std.testing.expectEqual(slot.kind(), first.kind());
        try std.testing.expectEqual(slot.kind(), second.kind());
        try std.testing.expectEqual(slot.kind(), rebuilt.kind());
        try std.testing.expectEqual(slot.rawValue(), rebuilt.rawValue());
        try expectInactiveAccessors(rebuilt);
    }
}
