const std = @import("std");
const err_ptr = @import("err_ptr");
const xarray_slot_view = @import("xarray_slot_view");

const Sample = struct {
    code: isize,
    raw: usize,
};

fn sample(code: isize) Sample {
    return .{
        .code = code,
        .raw = err_ptr.fromErrorCode(code),
    };
}

fn expectErrSlot(sample_value: Sample) !void {
    const slot = xarray_slot_view.fromRaw(sample_value.raw);

    try std.testing.expectEqual(xarray_slot_view.SlotKind.err, slot.kind());
    try std.testing.expect(slot.isErr());
    try std.testing.expect(!slot.isNull());
    try std.testing.expect(!slot.isValue());
    try std.testing.expect(!slot.isPointer());
    try std.testing.expectEqual(sample_value.raw, slot.rawValue());
    try std.testing.expectEqual(@as(?isize, sample_value.code), slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), slot.value());
    try std.testing.expectEqual(@as(?usize, null), slot.pointerValue());
    try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(sample_value.raw));
}

test "err_ptr codes advance monotonically through the xarray err lane" {
    const samples = [_]Sample{
        sample(-4095),
        sample(-2048),
        sample(-512),
        sample(-22),
        sample(-1),
    };

    try std.testing.expectEqual(err_ptr.err_floor, samples[0].raw);

    for (samples) |entry| {
        try expectErrSlot(entry);
    }

    for (samples[1..], 1..) |entry, index| {
        try std.testing.expect(samples[index - 1].raw < entry.raw);
        try std.testing.expect(samples[index - 1].code < entry.code);
    }
}

test "err lane boundaries stay closed to value and pointer decoders" {
    const floor_slot = xarray_slot_view.fromErrorCode(-4095);
    const near_floor_slot = xarray_slot_view.fromErrorCode(-4094);
    const top_slot = xarray_slot_view.fromErrorCode(-1);

    try std.testing.expectEqual(err_ptr.err_floor, floor_slot.rawValue());
    try std.testing.expectEqual(err_ptr.err_floor + 1, near_floor_slot.rawValue());
    try std.testing.expect(top_slot.rawValue() > near_floor_slot.rawValue());

    try std.testing.expectEqual(@as(?isize, -4095), floor_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -4094), near_floor_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, -1), top_slot.errorCode());

    try std.testing.expectEqual(@as(?usize, null), floor_slot.value());
    try std.testing.expectEqual(@as(?usize, null), near_floor_slot.pointerValue());
    try std.testing.expectEqual(@as(?usize, null), top_slot.value());
}

test "the raw gap immediately below err_floor remains pointer-like" {
    const gap_raw = err_ptr.err_floor - 1;
    const gap_slot = xarray_slot_view.fromRaw(gap_raw);

    try std.testing.expect(err_ptr.isOkValue(gap_raw));
    try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(gap_raw));
    try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, gap_slot.kind());
    try std.testing.expectEqual(@as(?usize, gap_raw), gap_slot.pointerValue());
    try std.testing.expectEqual(@as(?isize, null), gap_slot.errorCode());
    try std.testing.expectEqual(@as(?usize, null), gap_slot.value());
}
