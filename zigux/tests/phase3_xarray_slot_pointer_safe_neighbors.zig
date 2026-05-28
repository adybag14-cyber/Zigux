const std = @import("std");

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

test "fromPointer keeps low even neighbors beside wrapped-low values in the pointer lane" {
    const cases = [_]usize{ 2, 4, 6, 8 };

    inline for (cases) |raw| {
        const pointer_slot = xarray_slot_view.fromPointer(raw);
        const raw_slot = xarray_slot_view.fromRaw(raw);
        const tagged_neighbor = raw - 1;

        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try std.testing.expectEqual(pointer_slot.kind(), raw_slot.kind());
        try std.testing.expect(pointer_slot.isPointer());
        try std.testing.expect(!pointer_slot.isNull());
        try std.testing.expect(!pointer_slot.isValue());
        try std.testing.expect(!pointer_slot.isErr());
        try std.testing.expectEqual(@as(?usize, raw), pointer_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, raw), raw_slot.pointerValue());

        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(tagged_neighbor));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.value, xarray_slot_view.fromRaw(tagged_neighbor).kind());
        try std.testing.expectEqual(@as(?usize, tagged_neighbor >> 1), xarray_slot_view.fromRaw(tagged_neighbor).value());
    }
}

test "fromPointer keeps high even raws below the err floor in the pointer lane" {
    const cases = [_]usize{
        err_ptr.err_floor - 3,
        err_ptr.err_floor - 1,
    };

    inline for (cases) |raw| {
        const pointer_slot = xarray_slot_view.fromPointer(raw);
        const raw_slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(raw));
        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try std.testing.expectEqual(pointer_slot.kind(), raw_slot.kind());
        try std.testing.expect(pointer_slot.isPointer());
        try std.testing.expect(!pointer_slot.isNull());
        try std.testing.expect(!pointer_slot.isValue());
        try std.testing.expect(!pointer_slot.isErr());
        try std.testing.expectEqual(@as(?usize, raw), pointer_slot.pointerValue());
        try std.testing.expectEqual(@as(?usize, raw), raw_slot.pointerValue());
    }
}

test "pointer-safe raws stay disjoint from neighboring tagged lanes at both boundaries" {
    const cases = [_]struct {
        pointer_raw: usize,
        tagged_raw: usize,
        expected_kind: xarray_slot_view.SlotKind,
    }{
        .{ .pointer_raw = 2, .tagged_raw = 1, .expected_kind = .value },
        .{ .pointer_raw = 4, .tagged_raw = 3, .expected_kind = .value },
        .{ .pointer_raw = err_ptr.err_floor - 1, .tagged_raw = err_ptr.err_floor, .expected_kind = .err },
    };

    inline for (cases) |case| {
        const pointer_slot = xarray_slot_view.fromPointer(case.pointer_raw);
        const tagged_slot = xarray_slot_view.fromRaw(case.tagged_raw);

        try std.testing.expectEqual(xarray_slot_view.SlotKind.pointer, pointer_slot.kind());
        try std.testing.expectEqual(case.expected_kind, tagged_slot.kind());
        try std.testing.expect(!xarray_slot_view.isTaggedInternalEntry(case.pointer_raw));
        try std.testing.expect(xarray_slot_view.isTaggedInternalEntry(case.tagged_raw));
        if (case.expected_kind == .value) {
            try std.testing.expectEqual(@as(usize, 1), case.pointer_raw - case.tagged_raw);
            try std.testing.expectEqual(@as(?usize, case.tagged_raw >> 1), tagged_slot.value());
            try std.testing.expectEqual(try xa_value.makeValue(case.tagged_raw >> 1), case.tagged_raw);
        } else {
            try std.testing.expectEqual(@as(usize, 1), case.tagged_raw - case.pointer_raw);
            try std.testing.expectEqual(@as(?isize, -4095), tagged_slot.errorCode());
            try std.testing.expectEqual(err_ptr.fromErrorCode(-4095), case.tagged_raw);
        }
    }
}
