const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const AccessorRow = struct {
    name: []const u8,
    raw: usize,
    kind: SlotKind,
    value: ?usize = null,
    errno: ?isize = null,
    pointer: ?usize = null,
};

fn expectAccessorPresence(row: AccessorRow) !void {
    const slot = xarray_slot_view.fromRaw(row.raw);

    try std.testing.expect(row.name.len != 0);
    try std.testing.expectEqual(row.raw, slot.rawValue());
    try std.testing.expectEqual(row.kind, slot.kind());
    try std.testing.expectEqual(row.value, slot.value());
    try std.testing.expectEqual(row.errno, slot.errorCode());
    try std.testing.expectEqual(row.pointer, slot.pointerValue());

    try std.testing.expectEqual(row.value != null, slot.value() != null);
    try std.testing.expectEqual(row.errno != null, slot.errorCode() != null);
    try std.testing.expectEqual(row.pointer != null, slot.pointerValue() != null);

    try std.testing.expectEqual(row.kind == .null, row.value == null and row.errno == null and row.pointer == null);
    try std.testing.expectEqual(row.kind == .value, row.value != null and row.errno == null and row.pointer == null);
    try std.testing.expectEqual(row.kind == .err, row.value == null and row.errno != null and row.pointer == null);
    try std.testing.expectEqual(row.kind == .pointer, row.value == null and row.errno == null and row.pointer != null);
}

test "phase3 errptr xarray optional accessors expose exactly one payload lane" {
    const rows = [_]AccessorRow{
        .{
            .name = "null slot has no optional payload",
            .raw = xarray_slot_view.nullSlot().rawValue(),
            .kind = .null,
        },
        .{
            .name = "inline zero exposes only value",
            .raw = try xa_value.makeValue(0),
            .kind = .value,
            .value = 0,
        },
        .{
            .name = "safe inline limit exposes only value",
            .raw = try xa_value.makeValue(xa_value.safe_inline_limit),
            .kind = .value,
            .value = xa_value.safe_inline_limit,
        },
        .{
            .name = "first pointer candidate exposes only pointer",
            .raw = 2,
            .kind = .pointer,
            .pointer = 2,
        },
        .{
            .name = "last pointer before err floor exposes only pointer",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .pointer = err_ptr.err_floor - 1,
        },
        .{
            .name = "err floor exposes only errno",
            .raw = err_ptr.err_floor,
            .kind = .err,
            .errno = -@as(isize, @intCast(err_ptr.max_errno)),
        },
        .{
            .name = "odd errno exposes only errno despite xa low bit",
            .raw = err_ptr.fromErrorCode(-1),
            .kind = .err,
            .errno = -1,
        },
    };

    for (rows) |row| {
        try expectAccessorPresence(row);
    }
}

test "phase3 errptr xarray constructor outputs keep optional accessor presence stable after reread" {
    const value_slot = try xarray_slot_view.fromValue(29);
    const err_slot = xarray_slot_view.fromErrorCode(-22);
    const pointer_slot = xarray_slot_view.fromPointer(0x8000);

    try expectAccessorPresence(.{
        .name = "value constructor reread",
        .raw = value_slot.rawValue(),
        .kind = .value,
        .value = 29,
    });
    try expectAccessorPresence(.{
        .name = "errno constructor reread",
        .raw = err_slot.rawValue(),
        .kind = .err,
        .errno = -22,
    });
    try expectAccessorPresence(.{
        .name = "pointer constructor reread",
        .raw = pointer_slot.rawValue(),
        .kind = .pointer,
        .pointer = 0x8000,
    });
}
