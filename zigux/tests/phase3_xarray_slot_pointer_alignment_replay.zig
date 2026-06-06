const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const PointerSample = struct {
    name: []const u8,
    raw: usize,
};

const aligned_pointer_samples = [_]PointerSample{
    .{ .name = "low word aligned", .raw = 0x2 },
    .{ .name = "cacheline aligned", .raw = 0x40 },
    .{ .name = "page aligned", .raw = 0x1000 },
    .{ .name = "large aligned below err floor", .raw = err_ptr.err_floor - 0x1001 },
    .{ .name = "last even pointer before err floor", .raw = err_ptr.err_floor - 1 },
};

fn expectPointerSlot(sample: PointerSample) !void {
    const raw_slot = xarray_slot_view.fromRaw(sample.raw);
    const pointer_slot = xarray_slot_view.fromPointer(sample.raw);

    try testing.expect(sample.raw != 0);
    try testing.expect((sample.raw & xa_value.value_tag_mask) == 0);
    try testing.expect(err_ptr.isOkValue(sample.raw));
    try testing.expect(!xarray_slot_view.isTaggedInternalEntry(sample.raw));

    try testing.expectEqual(xarray_slot_view.SlotKind.pointer, raw_slot.kind());
    try testing.expect(raw_slot.isPointer());
    try testing.expect(!raw_slot.isNull());
    try testing.expect(!raw_slot.isValue());
    try testing.expect(!raw_slot.isErr());
    try testing.expect(!raw_slot.isTaggedEntry());
    try testing.expectEqual(sample.raw, raw_slot.rawValue());
    try testing.expectEqual(@as(?usize, sample.raw), raw_slot.pointerValue());
    try testing.expectEqual(@as(?usize, null), raw_slot.value());
    try testing.expectEqual(@as(?isize, null), raw_slot.errorCode());

    try testing.expectEqual(raw_slot.kind(), pointer_slot.kind());
    try testing.expectEqual(raw_slot.rawValue(), pointer_slot.rawValue());
    try testing.expectEqual(raw_slot.pointerValue(), pointer_slot.pointerValue());
    try testing.expectEqual(raw_slot.value(), pointer_slot.value());
    try testing.expectEqual(raw_slot.errorCode(), pointer_slot.errorCode());
}

test "aligned non-tagged xarray slots remain pointer lanes" {
    for (aligned_pointer_samples) |sample| {
        try expectPointerSlot(sample);
    }
}

test "aligned pointer neighbors keep low-tagged values and err raws separate" {
    for (aligned_pointer_samples[0 .. aligned_pointer_samples.len - 1]) |sample| {
        const value_neighbor = sample.raw - 1;
        const value_slot = xarray_slot_view.fromRaw(value_neighbor);

        try testing.expect(xa_value.isValue(value_neighbor));
        try testing.expect(value_slot.isValue());
        try testing.expect(!value_slot.isPointer());
        try testing.expectEqual(@as(?usize, value_neighbor >> 1), value_slot.value());
        try testing.expectEqual(@as(?usize, null), value_slot.pointerValue());
    }

    const err_floor_slot = xarray_slot_view.fromRaw(err_ptr.err_floor);
    try testing.expect(err_floor_slot.isErr());
    try testing.expect(!err_floor_slot.isPointer());
    try testing.expectEqual(@as(?isize, -4095), err_floor_slot.errorCode());
    try testing.expectEqual(@as(?usize, null), err_floor_slot.pointerValue());

    const top_err_slot = xarray_slot_view.fromRaw(err_ptr.fromErrorCode(-1));
    try testing.expect(top_err_slot.isErr());
    try testing.expect(!top_err_slot.isPointer());
    try testing.expectEqual(@as(?isize, -1), top_err_slot.errorCode());
}

test "zero remains the only null raw outside the pointer constructor route" {
    const null_slot = xarray_slot_view.fromRaw(0);
    const first_pointer = xarray_slot_view.fromPointer(0x2);

    try testing.expect(null_slot.isNull());
    try testing.expect(!null_slot.isPointer());
    try testing.expectEqual(@as(?usize, null), null_slot.pointerValue());

    try testing.expect(!first_pointer.isNull());
    try testing.expect(first_pointer.isPointer());
    try testing.expectEqual(@as(?usize, 0x2), first_pointer.pointerValue());
}
