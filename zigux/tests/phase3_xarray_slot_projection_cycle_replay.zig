const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ProjectionCase = struct {
    label: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    errno: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
    ok: bool,
};

fn expectProjection(case: ProjectionCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.errno, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.tagged, xarray_slot_view.isTaggedInternalEntry(case.raw));
    try std.testing.expectEqual(case.ok, err_ptr.isOkValue(case.raw));

    switch (case.kind) {
        .null => try std.testing.expect(slot.isNull()),
        .value => try std.testing.expect(slot.isValue()),
        .err => try std.testing.expect(slot.isErr()),
        .pointer => try std.testing.expect(slot.isPointer()),
    }

    _ = case.label;
}

test "public constructors project back through raw xarray slot decoding" {
    const value_slot = try xarray_slot_view.fromValue(42);
    const max_value_slot = try xarray_slot_view.fromValue(xa_value.safe_inline_limit);
    const pointer_slot = xarray_slot_view.fromPointer(0x4000);
    const near_floor_pointer = xarray_slot_view.fromPointer(err_ptr.err_floor - 1);
    const err_floor_slot = xarray_slot_view.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const middle_err_slot = xarray_slot_view.fromErrorCode(-2048);
    const top_err_slot = xarray_slot_view.fromErrorCode(-1);

    const cases = [_]ProjectionCase{
        .{
            .label = "null constructor",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
            .tagged = false,
            .ok = true,
        },
        .{
            .label = "value constructor",
            .raw = value_slot.rawValue(),
            .kind = .value,
            .value = 42,
            .tagged = true,
            .ok = true,
        },
        .{
            .label = "highest accepted value constructor",
            .raw = max_value_slot.rawValue(),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
            .ok = true,
        },
        .{
            .label = "ordinary pointer constructor",
            .raw = pointer_slot.rawValue(),
            .kind = .pointer,
            .pointer = 0x4000,
            .tagged = false,
            .ok = true,
        },
        .{
            .label = "near-floor pointer constructor",
            .raw = near_floor_pointer.rawValue(),
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
            .ok = true,
        },
        .{
            .label = "err floor constructor",
            .raw = err_floor_slot.rawValue(),
            .kind = .err,
            .errno = -@as(isize, @intCast(err_ptr.max_errno)),
            .tagged = true,
            .ok = false,
        },
        .{
            .label = "middle errno constructor",
            .raw = middle_err_slot.rawValue(),
            .kind = .err,
            .errno = -2048,
            .tagged = true,
            .ok = false,
        },
        .{
            .label = "top errno constructor",
            .raw = top_err_slot.rawValue(),
            .kind = .err,
            .errno = -1,
            .tagged = true,
            .ok = false,
        },
    };

    for (cases) |case| {
        try expectProjection(case);
    }
}

test "raw projection rejects constructor-forbidden aliases into their decoded lane" {
    const rejected_value = xa_value.safe_inline_limit + 1;
    const rejected_raw = (rejected_value << 1) | xa_value.value_tag_mask;
    const odd_err_raw = err_ptr.fromErrorCode(-17);
    const pointer_gap = err_ptr.err_floor - 3;

    try std.testing.expectError(error.ValueWouldOverlapErrPtr, xarray_slot_view.fromValue(rejected_value));

    try expectProjection(.{
        .label = "rejected value aliases err floor",
        .raw = rejected_raw,
        .kind = .err,
        .errno = -@as(isize, @intCast(err_ptr.max_errno)),
        .tagged = true,
        .ok = false,
    });
    try expectProjection(.{
        .label = "odd raw in err band is still err",
        .raw = odd_err_raw,
        .kind = .err,
        .errno = -17,
        .tagged = true,
        .ok = false,
    });
    try expectProjection(.{
        .label = "even gap below err floor is pointer-like",
        .raw = pointer_gap,
        .kind = .pointer,
        .pointer = pointer_gap,
        .tagged = false,
        .ok = true,
    });
}
