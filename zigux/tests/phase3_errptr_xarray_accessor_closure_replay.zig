const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const AccessorCase = struct {
    label: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    error_code: ?isize = null,
    pointer: ?usize = null,
    tagged: bool,
};

fn expectAccessorClosure(case: AccessorCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expect(case.label.len != 0);
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.kind == .null, slot.isNull());
    try std.testing.expectEqual(case.kind == .value, slot.isValue());
    try std.testing.expectEqual(case.kind == .err, slot.isErr());
    try std.testing.expectEqual(case.kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());
}

test "xarray slot accessors are closed outside their matching lane" {
    const cases = [_]AccessorCase{
        .{
            .label = "null",
            .raw = 0,
            .kind = .null,
            .tagged = false,
        },
        .{
            .label = "inline zero",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
            .tagged = true,
        },
        .{
            .label = "inline safe limit",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .tagged = true,
        },
        .{
            .label = "aligned pointer",
            .raw = 0x2000,
            .kind = .pointer,
            .pointer = 0x2000,
            .tagged = false,
        },
        .{
            .label = "highest pointer-like raw",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
            .tagged = false,
        },
        .{
            .label = "err floor",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .error_code = -@as(isize, @intCast(err_ptr.max_errno)),
            .tagged = true,
        },
        .{
            .label = "middle errno",
            .raw = err_ptr.fromErrorCode(-512),
            .kind = .err,
            .error_code = -512,
            .tagged = true,
        },
        .{
            .label = "top errno",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .error_code = -1,
            .tagged = true,
        },
    };

    for (cases) |case| {
        try expectAccessorClosure(case);
    }
}

test "constructor outputs preserve the same accessor closure after raw reread" {
    const rows = [_]AccessorCase{
        .{
            .label = "constructor null",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
            .tagged = false,
        },
        .{
            .label = "constructor value",
            .raw = (try xarray_slot_view.fromValue(73)).rawValue(),
            .kind = .value,
            .value = 73,
            .tagged = true,
        },
        .{
            .label = "constructor pointer",
            .raw = xarray_slot_view.fromPointer(0x8000).rawValue(),
            .kind = .pointer,
            .pointer = 0x8000,
            .tagged = false,
        },
        .{
            .label = "constructor error",
            .raw = xarray_slot_view.fromErrorCode(-22).rawValue(),
            .kind = .err,
            .error_code = -22,
            .tagged = true,
        },
    };

    for (rows) |row| {
        try expectAccessorClosure(row);
    }
}
