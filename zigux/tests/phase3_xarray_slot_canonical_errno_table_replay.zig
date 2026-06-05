const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const ErrnoCase = struct {
    name: []const u8,
    code: isize,
};

fn expectCanonicalErrno(case: ErrnoCase) !void {
    const raw = err_ptr.fromErrorCode(case.code);
    const raw_slot = xarray_slot_view.fromRaw(raw);
    const constructed = xarray_slot_view.fromErrorCode(case.code);

    try std.testing.expect(case.name.len != 0);
    try std.testing.expectEqual(raw, constructed.rawValue());
    try std.testing.expectEqual(SlotKind.err, raw_slot.kind());
    try std.testing.expectEqual(SlotKind.err, constructed.kind());
    try std.testing.expect(raw_slot.isErr());
    try std.testing.expect(constructed.isErr());
    try std.testing.expect(raw_slot.isTaggedEntry());
    try std.testing.expect(constructed.isTaggedEntry());
    try std.testing.expectEqual(@as(?isize, case.code), raw_slot.errorCode());
    try std.testing.expectEqual(@as(?isize, case.code), constructed.errorCode());
    try std.testing.expectEqual(@as(?usize, null), raw_slot.value());
    try std.testing.expectEqual(@as(?usize, null), raw_slot.pointerValue());
}

test "canonical errno constructors decode through the xarray error lane" {
    const cases = [_]ErrnoCase{
        .{ .name = "EPERM", .code = -1 },
        .{ .name = "ENOENT", .code = -2 },
        .{ .name = "EIO", .code = -5 },
        .{ .name = "ENOMEM", .code = -12 },
        .{ .name = "EINVAL", .code = -22 },
        .{ .name = "MAX_ERRNO", .code = -@as(isize, @intCast(err_ptr.max_errno)) },
    };

    for (cases) |case| {
        try expectCanonicalErrno(case);
    }
}

test "non-canonical positive and boundary neighbors keep the error accessor closed" {
    const neighbors = [_]struct {
        raw: usize,
        kind: SlotKind,
    }{
        .{ .raw = 0, .kind = .null },
        .{ .raw = 1, .kind = .value },
        .{ .raw = 2, .kind = .pointer },
        .{ .raw = try xa_value.makeValue(12), .kind = .value },
        .{ .raw = err_ptr.err_floor - 2, .kind = .value },
        .{ .raw = err_ptr.err_floor - 1, .kind = .pointer },
    };

    for (neighbors) |neighbor| {
        const slot = xarray_slot_view.fromRaw(neighbor.raw);

        try std.testing.expectEqual(neighbor.kind, slot.kind());
        try std.testing.expect(!slot.isErr());
        try std.testing.expectEqual(@as(?isize, null), slot.errorCode());
    }
}

test "xarray error lane preserves the raw Linux err_ptr ordering for the table" {
    const ordered_codes = [_]isize{ -@as(isize, @intCast(err_ptr.max_errno)), -1024, -255, -22, -5, -2, -1 };

    var previous = err_ptr.fromErrorCode(ordered_codes[0]);
    for (ordered_codes[1..]) |code| {
        const raw = err_ptr.fromErrorCode(code);
        const slot = xarray_slot_view.fromRaw(raw);

        try std.testing.expect(raw > previous);
        try std.testing.expectEqual(@as(?isize, code), slot.errorCode());
        previous = raw;
    }
}
