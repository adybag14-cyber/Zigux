const std = @import("std");
const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SlotKind = xarray_slot_view.SlotKind;

const IdentityCase = struct {
    label: []const u8,
    raw: usize,
};

fn expectedKind(raw: usize) SlotKind {
    if (raw == 0) {
        return .null;
    }
    if (err_ptr.isErrValue(raw)) {
        return .err;
    }
    if (xa_value.isValue(raw)) {
        return .value;
    }
    return .pointer;
}

fn expectedValue(raw: usize) ?usize {
    if (!xa_value.isValue(raw)) {
        return null;
    }
    return xa_value.toValue(raw);
}

fn expectedError(raw: usize) ?isize {
    if (!err_ptr.isErrValue(raw)) {
        return null;
    }
    return err_ptr.toErrorCode(raw);
}

fn expectedPointer(raw: usize) ?usize {
    if (raw == 0 or err_ptr.isErrValue(raw) or xa_value.isValue(raw)) {
        return null;
    }
    return raw;
}

fn expectIdentity(case: IdentityCase) !void {
    const slot = xarray_slot_view.fromRaw(case.raw);
    const kind = expectedKind(case.raw);

    try std.testing.expect(case.label.len != 0);
    try std.testing.expectEqual(case.raw, slot.rawValue());
    try std.testing.expectEqual(kind, slot.kind());
    try std.testing.expectEqual(kind == .null, slot.isNull());
    try std.testing.expectEqual(kind == .value, slot.isValue());
    try std.testing.expectEqual(kind == .err, slot.isErr());
    try std.testing.expectEqual(kind == .pointer, slot.isPointer());
    try std.testing.expectEqual(err_ptr.isErrValue(case.raw) or xa_value.isValue(case.raw), slot.isTaggedEntry());
    try std.testing.expectEqual(expectedValue(case.raw), slot.value());
    try std.testing.expectEqual(expectedError(case.raw), slot.errorCode());
    try std.testing.expectEqual(expectedPointer(case.raw), slot.pointerValue());
}

test "slot decoders mirror helper predicates across the raw identity matrix" {
    const inline_zero = try xa_value.makeValue(0);
    const inline_one = try xa_value.makeValue(1);
    const inline_limit = try xa_value.makeValue(xa_value.safe_inline_limit);
    const pointer_low: usize = 2;
    const pointer_before_err = err_ptr.err_floor - 1;
    const err_floor = err_ptr.fromErrorCode(-@as(isize, @intCast(err_ptr.max_errno)));
    const err_mid = err_ptr.fromErrorCode(-2048);
    const err_top = err_ptr.fromErrorCode(-1);

    const cases = [_]IdentityCase{
        .{ .label = "null sentinel", .raw = 0 },
        .{ .label = "inline zero", .raw = inline_zero },
        .{ .label = "inline one", .raw = inline_one },
        .{ .label = "inline limit", .raw = inline_limit },
        .{ .label = "low pointer", .raw = pointer_low },
        .{ .label = "pre-err pointer", .raw = pointer_before_err },
        .{ .label = "err floor", .raw = err_floor },
        .{ .label = "mid errno", .raw = err_mid },
        .{ .label = "top errno", .raw = err_top },
    };

    for (cases) |case| {
        try expectIdentity(case);
    }
}

test "constructor raws reread through the same identity matrix" {
    const constructed = [_]IdentityCase{
        .{ .label = "constructed null", .raw = xarray_slot_view.nullSlot().rawValue() },
        .{ .label = "constructed value", .raw = (try xarray_slot_view.fromValue(29)).rawValue() },
        .{ .label = "constructed pointer", .raw = xarray_slot_view.fromPointer(0x2000).rawValue() },
        .{ .label = "constructed err floor", .raw = xarray_slot_view.fromErrorCode(-4095).rawValue() },
        .{ .label = "constructed err top", .raw = xarray_slot_view.fromErrorCode(-1).rawValue() },
    };

    for (constructed) |case| {
        try expectIdentity(case);
    }
}
