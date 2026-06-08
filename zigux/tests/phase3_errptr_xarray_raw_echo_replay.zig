const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const EchoCase = struct {
    label: []const u8,
    raw: usize,
    kind: SlotKind,
    tagged: bool,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
};

fn expectEcho(case: EchoCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);

    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(case.kind, slot.kind());
    try std.testing.expectEqual(case.tagged, slot.isTaggedEntry());
    try std.testing.expectEqual(case.value, slot.value());
    try std.testing.expectEqual(case.error_code, slot.errorCode());
    try std.testing.expectEqual(case.pointer, slot.pointerValue());

    switch (case.kind) {
        .null => {
            try std.testing.expect(slot.isNull());
            try std.testing.expect(!slot.isValue());
            try std.testing.expect(!slot.isErr());
            try std.testing.expect(!slot.isPointer());
        },
        .value => {
            try std.testing.expect(!slot.isNull());
            try std.testing.expect(slot.isValue());
            try std.testing.expect(!slot.isErr());
            try std.testing.expect(!slot.isPointer());
        },
        .err => {
            try std.testing.expect(!slot.isNull());
            try std.testing.expect(!slot.isValue());
            try std.testing.expect(slot.isErr());
            try std.testing.expect(!slot.isPointer());
        },
        .pointer => {
            try std.testing.expect(!slot.isNull());
            try std.testing.expect(!slot.isValue());
            try std.testing.expect(!slot.isErr());
            try std.testing.expect(slot.isPointer());
        },
    }

    try std.testing.expect(case.label.len != 0);
}

test "raw echo preserves slot words across public xarray lanes" {
    const value_zero = try xa_value.makeValue(0);
    const value_limit = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_after_null: usize = 2;
    const pointer_before_err = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_mid = err_ptr.fromErrorCode(-2048);
    const err_top = err_ptr.fromErrorCode(-1);

    const cases = [_]EchoCase{
        .{
            .label = "null sentinel",
            .raw = 0,
            .kind = .null,
            .tagged = false,
            .value = null,
            .error_code = null,
            .pointer = null,
        },
        .{
            .label = "inline zero",
            .raw = value_zero,
            .kind = .value,
            .tagged = true,
            .value = 0,
            .error_code = null,
            .pointer = null,
        },
        .{
            .label = "highest inline value",
            .raw = value_limit,
            .kind = .value,
            .tagged = true,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
        },
        .{
            .label = "first simple pointer",
            .raw = pointer_after_null,
            .kind = .pointer,
            .tagged = false,
            .value = null,
            .error_code = null,
            .pointer = pointer_after_null,
        },
        .{
            .label = "last pointer before err floor",
            .raw = pointer_before_err,
            .kind = .pointer,
            .tagged = false,
            .value = null,
            .error_code = null,
            .pointer = pointer_before_err,
        },
        .{
            .label = "err floor",
            .raw = err_floor,
            .kind = .err,
            .tagged = true,
            .value = null,
            .error_code = -4095,
            .pointer = null,
        },
        .{
            .label = "middle errno",
            .raw = err_mid,
            .kind = .err,
            .tagged = true,
            .value = null,
            .error_code = -2048,
            .pointer = null,
        },
        .{
            .label = "top errno",
            .raw = err_top,
            .kind = .err,
            .tagged = true,
            .value = null,
            .error_code = -1,
            .pointer = null,
        },
    };

    for (cases) |case| {
        try expectEcho(case);
    }
}

test "constructor outputs echo back through raw slot rereads" {
    const value_slot = try xarray_slot_view.fromValue(57);
    const pointer_slot = xarray_slot_view.fromPointer(0x2000);
    const err_slot = xarray_slot_view.fromErrorCode(-57);

    try expectEcho(.{
        .label = "constructed value",
        .raw = value_slot.rawValue(),
        .kind = .value,
        .tagged = true,
        .value = 57,
        .error_code = null,
        .pointer = null,
    });
    try expectEcho(.{
        .label = "constructed pointer",
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .tagged = false,
        .value = null,
        .error_code = null,
        .pointer = 0x2000,
    });
    try expectEcho(.{
        .label = "constructed errno",
        .raw = err_slot.rawValue(),
        .kind = .err,
        .tagged = true,
        .value = null,
        .error_code = -57,
        .pointer = null,
    });
}
