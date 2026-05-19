const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const Case = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged_internal: bool,
};

fn buildCases() ![13]Case {
    return .{
        .{ .name = "null", .raw = 0, .kind = .null, .tagged_internal = false },
        .{ .name = "low_value_zero", .raw = try xa_value.makeValue(0), .kind = .value, .tagged_internal = true },
        .{ .name = "low_pointer_two", .raw = 2, .kind = .pointer, .tagged_internal = false },
        .{ .name = "low_value_one", .raw = try xa_value.makeValue(1), .kind = .value, .tagged_internal = true },
        .{ .name = "low_pointer_four", .raw = 4, .kind = .pointer, .tagged_internal = false },
        .{ .name = "mid_value_twenty_nine", .raw = try xa_value.makeValue(29), .kind = .value, .tagged_internal = true },
        .{ .name = "mid_pointer_sixty_four", .raw = 64, .kind = .pointer, .tagged_internal = false },
        .{ .name = "top_value_minus_one", .raw = try xa_value.makeValue(xa_value.safe_inline_limit - 1), .kind = .value, .tagged_internal = true },
        .{ .name = "top_value_limit", .raw = try xa_value.makeValue(xa_value.safe_inline_limit), .kind = .value, .tagged_internal = true },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer, .tagged_internal = false },
        .{ .name = "err_floor", .raw = err_ptr.err_floor, .kind = .err, .tagged_internal = true },
        .{ .name = "err_enomem", .raw = err_ptr.fromErrorCode(-12), .kind = .err, .tagged_internal = true },
        .{ .name = "err_top", .raw = err_ptr.fromErrorCode(-1), .kind = .err, .tagged_internal = true },
    };
}

test "representative xarray slot spectrum keeps a stable lane census" {
    const cases = try buildCases();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;

    for (cases) |case| {
        const slot = xarray_slot_view.fromRaw(case.raw);
        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));

        switch (slot.kind()) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (xarray_slot_view.isTaggedInternalEntry(case.raw)) {
            tagged_internal_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 5), value_count);
    try testing.expectEqual(@as(usize, 4), pointer_count);
    try testing.expectEqual(@as(usize, 3), err_count);
    try testing.expectEqual(value_count + err_count, tagged_internal_count);
}

test "representative spectrum preserves low and high boundary partitions" {
    const cases = try buildCases();

    try testing.expectEqualStrings("null", cases[0].name);
    try testing.expectEqual(@as(usize, 0), cases[0].raw);
    try testing.expectEqual(xarray_slot_view.SlotKind.null, cases[0].kind);

    try testing.expectEqual(@as(usize, 1), cases[1].raw);
    try testing.expectEqual(@as(usize, 2), cases[2].raw);
    try testing.expectEqual(@as(usize, 3), cases[3].raw);
    try testing.expectEqual(@as(usize, 4), cases[4].raw);

    try testing.expect(cases[7].raw < err_ptr.err_floor);
    try testing.expect(cases[8].raw < err_ptr.err_floor);
    try testing.expectEqual(err_ptr.err_floor - 4, cases[7].raw);
    try testing.expectEqual(err_ptr.err_floor - 2, cases[8].raw);
    try testing.expectEqual(err_ptr.err_floor - 1, cases[9].raw);
    try testing.expectEqual(err_ptr.err_floor, cases[10].raw);
    try testing.expect(cases[10].raw < cases[11].raw);
    try testing.expect(cases[11].raw < cases[12].raw);

    for (cases[1..10]) |case| {
        try testing.expect(case.kind != .err);
    }
    for (cases[10..]) |case| {
        try testing.expectEqual(xarray_slot_view.SlotKind.err, case.kind);
    }
}
