const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const TransitionCase = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    tagged_internal: bool,
};

fn expectTransitionCase(expected: TransitionCase) !void {
    const slot = xarray_slot_view.fromRaw(expected.raw);

    try testing.expectEqual(expected.kind, slot.kind());
    try testing.expectEqual(expected.kind == .null, slot.isNull());
    try testing.expectEqual(expected.kind == .value, slot.isValue());
    try testing.expectEqual(expected.kind == .err, slot.isErr());
    try testing.expectEqual(expected.kind == .pointer, slot.isPointer());
    try testing.expectEqual(expected.tagged_internal, xarray_slot_view.isTaggedInternalEntry(expected.raw));
}

fn buildCycle() ![7]TransitionCase {
    return .{
        .{
            .name = "null_start",
            .raw = 0,
            .kind = .null,
            .tagged_internal = false,
        },
        .{
            .name = "inline_zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .tagged_internal = true,
        },
        .{
            .name = "plain_pointer",
            .raw = 0x1000,
            .kind = .pointer,
            .tagged_internal = false,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged_internal = true,
        },
        .{
            .name = "gap_before_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged_internal = false,
        },
        .{
            .name = "inline_limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .tagged_internal = true,
        },
        .{
            .name = "null_end",
            .raw = 0,
            .kind = .null,
            .tagged_internal = false,
        },
    };
}

test "transition matrix walks all four slot kinds in both directions" {
    const cycle = try buildCycle();
    const expected_pairs = [_][2]xarray_slot_view.SlotKind{
        .{ .null, .value },
        .{ .value, .pointer },
        .{ .pointer, .err },
        .{ .err, .pointer },
        .{ .pointer, .value },
        .{ .value, .null },
    };

    for (cycle) |expected| {
        try expectTransitionCase(expected);
    }

    var transition_index: usize = 0;
    while (transition_index < expected_pairs.len) : (transition_index += 1) {
        const current = xarray_slot_view.fromRaw(cycle[transition_index].raw);
        const next = xarray_slot_view.fromRaw(cycle[transition_index + 1].raw);
        try testing.expectEqual(expected_pairs[transition_index][0], current.kind());
        try testing.expectEqual(expected_pairs[transition_index][1], next.kind());
    }
}

test "transition matrix keeps the cutoff seam directional and exact" {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const seam = [_]TransitionCase{
        .{
            .name = "inline_limit",
            .raw = inline_limit_raw,
            .kind = .value,
            .tagged_internal = true,
        },
        .{
            .name = "gap_before_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .tagged_internal = false,
        },
        .{
            .name = "err_floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .tagged_internal = true,
        },
        .{
            .name = "err_floor_plus_one",
            .raw = err_ptr.err_floor + 1,
            .kind = .err,
            .tagged_internal = true,
        },
    };

    for (seam) |expected| {
        try expectTransitionCase(expected);
    }

    try testing.expectEqual(err_ptr.err_floor - 2, inline_limit_raw);
    try testing.expectEqual(@as(usize, 1), seam[1].raw - seam[0].raw);
    try testing.expectEqual(@as(usize, 1), seam[2].raw - seam[1].raw);
    try testing.expectEqual(@as(usize, 1), seam[3].raw - seam[2].raw);
    try testing.expectEqual(@as(?usize, err_ptr.err_floor - 1), xarray_slot_view.fromRaw(seam[1].raw).pointerValue());
    try testing.expectEqual(@as(?isize, -4095), xarray_slot_view.fromRaw(seam[2].raw).errorCode());
    try testing.expectEqual(@as(?isize, -4094), xarray_slot_view.fromRaw(seam[3].raw).errorCode());
}

test "transition matrix summary counts stay stable across the cycle" {
    const cycle = try buildCycle();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;

    for (cycle) |expected| {
        switch (expected.kind) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (expected.tagged_internal) {
            tagged_internal_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 2), null_count);
    try testing.expectEqual(@as(usize, 2), value_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 1), err_count);
    try testing.expectEqual(@as(usize, 3), tagged_internal_count);
}