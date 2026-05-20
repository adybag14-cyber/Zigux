const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
};

fn buildCases() ![8]Case {
    return .{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "inline_zero", .raw = try xa_value.makeValue(0), .kind = .value },
        .{ .name = "pointer_two", .raw = 2, .kind = .pointer },
        .{ .name = "inline_mid", .raw = try xa_value.makeValue(29), .kind = .value },
        .{ .name = "pointer_gap", .raw = 0x20, .kind = .pointer },
        .{ .name = "inline_limit", .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer },
        .{ .name = "err_floor", .raw = err_ptr.err_floor, .kind = .err },
    };
}

fn truePredicateCount(slot: xarray_slot_view.SlotView) u8 {
    var count: u8 = 0;
    if (slot.isNull()) count += 1;
    if (slot.isValue()) count += 1;
    if (slot.isErr()) count += 1;
    if (slot.isPointer()) count += 1;
    return count;
}

fn rebuild(slot: xarray_slot_view.SlotView) !xarray_slot_view.SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
    };
}

test "xarray-slot predicates stay one-hot across representative lane samples" {
    const cases = try buildCases();

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.raw, slot.rawValue());
        try testing.expectEqual(@as(u8, 1), truePredicateCount(slot));
        try testing.expectEqual(case.kind == .null, slot.isNull());
        try testing.expectEqual(case.kind == .value, slot.isValue());
        try testing.expectEqual(case.kind == .err, slot.isErr());
        try testing.expectEqual(case.kind == .pointer, slot.isPointer());
        try testing.expectEqual(case.kind == .value or case.kind == .err, xarray_slot_view.isTaggedInternalEntry(case.raw));
    }
}

test "xarray-slot accessors only open for their own lane and rebuild exactly" {
    const cases = try buildCases();

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        const rebuilt = try rebuild(slot);

        try testing.expectEqual(case.kind, rebuilt.kind());
        try testing.expectEqual(case.raw, rebuilt.rawValue());

        switch (case.kind) {
            .null => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
            },
            .value => {
                try testing.expect(slot.value() != null);
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
                try testing.expectEqual(slot.value(), rebuilt.value());
            },
            .pointer => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
                try testing.expectEqual(@as(?usize, case.raw), slot.pointerValue());
                try testing.expectEqual(slot.pointerValue(), rebuilt.pointerValue());
            },
            .err => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expect(slot.errorCode() != null);
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
                try testing.expectEqual(slot.errorCode(), rebuilt.errorCode());
            },
        }
    }
}
