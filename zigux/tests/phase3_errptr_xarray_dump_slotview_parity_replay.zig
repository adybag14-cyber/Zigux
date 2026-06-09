const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const DumpKind = enum {
    null,
    xa_value,
    err_ptr,
    pointer_like,
};

const Case = struct {
    name: []const u8,
    raw: usize,
    dump_kind: DumpKind,
    slot_kind: xarray_slot_view.SlotKind,
    decoded_value: ?usize,
    decoded_error: ?isize,
    tagged_entry: bool,
};

fn dumpKindFor(raw: usize) DumpKind {
    if (raw == 0) {
        return .null;
    }
    if (xa_value.isValue(raw)) {
        return .xa_value;
    }
    if (err_ptr.isErrValue(raw)) {
        return .err_ptr;
    }
    return .pointer_like;
}

fn slotKindForDumpKind(kind: DumpKind) xarray_slot_view.SlotKind {
    return switch (kind) {
        .null => .null,
        .xa_value => .value,
        .err_ptr => .err,
        .pointer_like => .pointer,
    };
}

fn expectCase(row: Case) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try testing.expectEqual(row.dump_kind, dumpKindFor(row.raw));
    try testing.expectEqual(row.slot_kind, slot.kind());
    try testing.expectEqual(slotKindForDumpKind(row.dump_kind), slot.kind());
    try testing.expectEqual(row.raw, slot.rawValue());
    try testing.expectEqual(row.decoded_value, slot.value());
    try testing.expectEqual(row.decoded_error, slot.errorCode());
    try testing.expectEqual(row.tagged_entry, slot.isTaggedEntry());

    if (row.slot_kind == .pointer) {
        try testing.expectEqual(@as(?usize, row.raw), slot.pointerValue());
    } else {
        try testing.expectEqual(@as(?usize, null), slot.pointerValue());
    }
}

test "dump classifier and slot view stay in parity for representative rows" {
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);
    const rejected_inline_raw =
        ((xa_value.safe_inline_limit + 1) << 1) | xa_value.value_tag_mask;

    const rows = [_]Case{
        .{
            .name = "null",
            .raw = 0,
            .dump_kind = .null,
            .slot_kind = .null,
            .decoded_value = null,
            .decoded_error = null,
            .tagged_entry = false,
        },
        .{
            .name = "pointer_like_low_even",
            .raw = 64,
            .dump_kind = .pointer_like,
            .slot_kind = .pointer,
            .decoded_value = null,
            .decoded_error = null,
            .tagged_entry = false,
        },
        .{
            .name = "inline_zero",
            .raw = inline_zero_raw,
            .dump_kind = .xa_value,
            .slot_kind = .value,
            .decoded_value = 0,
            .decoded_error = null,
            .tagged_entry = true,
        },
        .{
            .name = "inline_limit",
            .raw = inline_limit_raw,
            .dump_kind = .xa_value,
            .slot_kind = .value,
            .decoded_value = xa_value.safe_inline_limit,
            .decoded_error = null,
            .tagged_entry = true,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .dump_kind = .pointer_like,
            .slot_kind = .pointer,
            .decoded_value = null,
            .decoded_error = null,
            .tagged_entry = false,
        },
        .{
            .name = "rejected_inline_overlap",
            .raw = rejected_inline_raw,
            .dump_kind = .err_ptr,
            .slot_kind = .err,
            .decoded_value = null,
            .decoded_error = -4095,
            .tagged_entry = true,
        },
        .{
            .name = "err_enomem",
            .raw = err_ptr.fromErrorCode(-12),
            .dump_kind = .err_ptr,
            .slot_kind = .err,
            .decoded_value = null,
            .decoded_error = -12,
            .tagged_entry = true,
        },
        .{
            .name = "err_top",
            .raw = err_ptr.fromErrorCode(-1),
            .dump_kind = .err_ptr,
            .slot_kind = .err,
            .decoded_value = null,
            .decoded_error = -1,
            .tagged_entry = true,
        },
    };

    for (rows) |row| {
        try testing.expect(row.name.len > 0);
        try expectCase(row);
    }
}

test "rejected inline raw aliases the err_ptr floor in both views" {
    const first_rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_inline_raw =
        (first_rejected_value << 1) | xa_value.value_tag_mask;
    const slot = xarray_slot_view.fromRaw(rejected_inline_raw);

    try testing.expectError(error.ValueWouldOverlapErrPtr, xa_value.makeValue(first_rejected_value));
    try testing.expectEqual(err_ptr.err_floor, rejected_inline_raw);
    try testing.expectEqual(DumpKind.err_ptr, dumpKindFor(rejected_inline_raw));
    try testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try testing.expectEqual(@as(?isize, -4095), slot.errorCode());
    try testing.expectEqual(@as(?usize, null), slot.value());
    try testing.expectEqual(@as(?usize, null), slot.pointerValue());
}
