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

const case_count = 10;

fn buildCases() ![case_count]Case {
    return .{
        .{ .name = "null", .raw = 0, .kind = .null },
        .{ .name = "inline_zero", .raw = try xa_value.makeValue(0), .kind = .value },
        .{ .name = "pointer_two", .raw = 2, .kind = .pointer },
        .{ .name = "inline_one", .raw = try xa_value.makeValue(1), .kind = .value },
        .{ .name = "pointer_four", .raw = 4, .kind = .pointer },
        .{ .name = "inline_twenty_nine", .raw = try xa_value.makeValue(29), .kind = .value },
        .{ .name = "inline_limit", .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer },
        .{ .name = "err_floor", .raw = err_ptr.err_floor, .kind = .err },
        .{ .name = "err_top", .raw = err_ptr.fromErrorCode(-1), .kind = .err },
    };
}

fn rebuild(slot: xarray_slot_view.SlotView) !xarray_slot_view.SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
    };
}

test "canonical xarray-slot walk stays strictly monotonic across lane boundaries" {
    const cases = try buildCases();

    for (cases, 0..) |case, index| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.raw, slot.rawValue());

        if (index != 0) {
            try testing.expect(cases[index - 1].raw < case.raw);
        }
    }

    try testing.expectEqualStrings("null", cases[0].name);
    try testing.expectEqual(@as(usize, 0), cases[0].raw);
    try testing.expectEqual(@as(usize, 1), cases[1].raw);
    try testing.expectEqual(@as(usize, 2), cases[2].raw);
    try testing.expectEqual(@as(usize, 3), cases[3].raw);
    try testing.expectEqual(@as(usize, 4), cases[4].raw);
    try testing.expectEqual(err_ptr.err_floor - 2, cases[6].raw);
    try testing.expectEqual(err_ptr.err_floor - 1, cases[7].raw);
    try testing.expectEqual(err_ptr.err_floor, cases[8].raw);

    for (cases[0..8]) |case| {
        try testing.expect(case.kind != .err);
    }
    for (cases[8..]) |case| {
        try testing.expectEqual(xarray_slot_view.SlotKind.err, case.kind);
    }
}

test "constructor rebuild preserves the same ordered xarray-slot walk" {
    const cases = try buildCases();
    var rebuilt_raws: [case_count]usize = undefined;

    for (cases, 0..) |case, index| {
        const decoded = xarray_slot_view.fromRaw(case.raw);
        const rebuilt = try rebuild(decoded);

        try testing.expectEqual(case.kind, rebuilt.kind());
        try testing.expectEqual(case.raw, rebuilt.rawValue());

        switch (case.kind) {
            .null => {
                try testing.expectEqual(@as(?usize, null), rebuilt.value());
                try testing.expectEqual(@as(?isize, null), rebuilt.errorCode());
                try testing.expectEqual(@as(?usize, null), rebuilt.pointerValue());
            },
            .value => try testing.expectEqual(decoded.value(), rebuilt.value()),
            .pointer => try testing.expectEqual(decoded.pointerValue(), rebuilt.pointerValue()),
            .err => try testing.expectEqual(decoded.errorCode(), rebuilt.errorCode()),
        }

        rebuilt_raws[index] = rebuilt.rawValue();
        if (index != 0) {
            try testing.expect(rebuilt_raws[index - 1] < rebuilt_raws[index]);
        }
    }

    try testing.expectEqual(err_ptr.err_floor - 1, rebuilt_raws[7]);
    try testing.expectEqual(err_ptr.err_floor, rebuilt_raws[8]);
    try testing.expect(rebuilt_raws[8] < rebuilt_raws[9]);
}
