const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;
const SlotView = xarray_slot_view.SlotView;

const StreamCase = struct {
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer_raw: ?usize = null,
};

fn rebuild(slot: SlotView) !SlotView {
    return switch (slot.kind()) {
        .null => xarray_slot_view.nullSlot(),
        .value => try xarray_slot_view.fromValue(slot.value().?),
        .err => xarray_slot_view.fromErrorCode(slot.errorCode().?),
        .pointer => xarray_slot_view.fromPointer(slot.pointerValue().?),
    };
}

fn expectCase(case: StreamCase) !SlotView {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try testing.expectEqual(case.kind, slot.kind());
    try testing.expectEqual(case.raw, slot.rawValue());
    try testing.expectEqual(case.value, slot.value());
    try testing.expectEqual(case.error_code, slot.errorCode());
    try testing.expectEqual(case.pointer_raw, slot.pointerValue());

    return slot;
}

test "mixed xarray slot stream keeps lane summaries and rebuilds stable" {
    const safe_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const stream = [_]StreamCase{
        .{ .raw = 0, .kind = .null },
        .{ .raw = try xa_value.makeValue(0), .kind = .value, .value = 0 },
        .{ .raw = 2, .kind = .pointer, .pointer_raw = 2 },
        .{ .raw = try xa_value.makeValue(29), .kind = .value, .value = 29 },
        .{ .raw = 0x1000, .kind = .pointer, .pointer_raw = 0x1000 },
        .{
            .raw = safe_limit_raw,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer_raw = err_ptr.err_floor - 1,
        },
        .{
            .raw = err_ptr.fromErrorCode(-4095),
            .kind = .err,
            .error_code = -4095,
        },
        .{
            .raw = err_ptr.fromErrorCode(-22),
            .kind = .err,
            .error_code = -22,
        },
        .{
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .error_code = -1,
        },
    };

    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var value_sum: usize = 0;
    var pointer_xor: usize = 0;
    var err_abs_sum: usize = 0;

    for (stream) |case| {
        const slot = try expectCase(case);
        const rebuilt = try rebuild(slot);

        try testing.expectEqual(case.kind, rebuilt.kind());
        try testing.expectEqual(case.raw, rebuilt.rawValue());
        try testing.expectEqual(case.value, rebuilt.value());
        try testing.expectEqual(case.error_code, rebuilt.errorCode());
        try testing.expectEqual(case.pointer_raw, rebuilt.pointerValue());

        switch (case.kind) {
            .null => null_count += 1,
            .value => {
                value_count += 1;
                value_sum += case.value.?;
            },
            .pointer => {
                pointer_count += 1;
                pointer_xor ^= case.pointer_raw.?;
            },
            .err => {
                err_count += 1;
                err_abs_sum += @intCast(-case.error_code.?);
            },
        }
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 3), value_count);
    try testing.expectEqual(@as(usize, 3), pointer_count);
    try testing.expectEqual(@as(usize, 3), err_count);
    try testing.expectEqual(@as(usize, xa_value.safe_inline_limit + 29), value_sum);
    try testing.expectEqual(
        @as(usize, 2 ^ 0x1000 ^ (err_ptr.err_floor - 1)),
        pointer_xor,
    );
    try testing.expectEqual(@as(usize, 4095 + 22 + 1), err_abs_sum);
}

test "mixed replay keeps tagged summary distinct from pointer gaps" {
    const stream = [_]usize{
        0,
        try xa_value.makeValue(0),
        2,
        try xa_value.makeValue(1),
        err_ptr.err_floor - 1,
        err_ptr.err_floor,
        err_ptr.fromErrorCode(-1),
    };

    var tagged_count: usize = 0;
    var pointer_count: usize = 0;
    var null_count: usize = 0;

    for (stream) |raw| {
        const slot = xarray_slot_view.fromRaw(raw);
        const tagged = xarray_slot_view.isTaggedInternalEntry(raw);

        if (slot.isNull()) {
            null_count += 1;
            try testing.expect(!tagged);
            continue;
        }

        if (slot.isPointer()) {
            pointer_count += 1;
            try testing.expect(!tagged);
            try testing.expectEqual(@as(?usize, raw), slot.pointerValue());
            continue;
        }

        tagged_count += 1;
        try testing.expect(tagged);
        try testing.expect(!slot.isPointer());
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 4), tagged_count);
}
