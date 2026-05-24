const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const SharedCase = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged_internal: bool,
};

fn buildSharedCases() ![7]SharedCase {
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    return .{
        .{
            .name = "null",
            .raw = 0,
            .kind = .null,
            .value = null,
            .error_code = null,
            .pointer = null,
            .tagged_internal = false,
        },
        .{
            .name = "pointer_like",
            .raw = 64,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = 64,
            .tagged_internal = false,
        },
        .{
            .name = "inline_small",
            .raw = try xa_value.makeValue(29),
            .kind = .value,
            .value = 29,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "inline_limit",
            .raw = inline_limit_raw,
            .kind = .value,
            .value = xa_value.safe_inline_limit,
            .error_code = null,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "gap_before_err_floor",
            .raw = err_ptr.err_floor - 1,
            .kind = .pointer,
            .value = null,
            .error_code = null,
            .pointer = err_ptr.err_floor - 1,
            .tagged_internal = false,
        },
        .{
            .name = "err_enomem",
            .raw = err_ptr.fromErrorCode(-12),
            .kind = .err,
            .value = null,
            .error_code = -12,
            .pointer = null,
            .tagged_internal = true,
        },
        .{
            .name = "err_max",
            .raw = err_ptr.fromErrorCode(-4095),
            .kind = .err,
            .value = null,
            .error_code = -4095,
            .pointer = null,
            .tagged_internal = true,
        },
    };
}

fn expectSharedCase(shared: SharedCase) !void {
    const slot = xarray_slot_view.fromRaw(shared.raw);

    try testing.expectEqual(shared.kind, slot.kind());
    try testing.expectEqual(shared.kind == .null, slot.isNull());
    try testing.expectEqual(shared.kind == .value, slot.isValue());
    try testing.expectEqual(shared.kind == .err, slot.isErr());
    try testing.expectEqual(shared.kind == .pointer, slot.isPointer());
    try testing.expectEqual(shared.value, slot.value());
    try testing.expectEqual(shared.error_code, slot.errorCode());
    try testing.expectEqual(shared.pointer, slot.pointerValue());
    try testing.expectEqual(shared.tagged_internal, xarray_slot_view.isTaggedInternalEntry(shared.raw));
}

test "shared err_ptr dump cases keep slot-view lane classification aligned" {
    const shared_cases = try buildSharedCases();

    for (shared_cases) |shared| {
        try expectSharedCase(shared);
    }
}

test "shared dump decoders stay aligned across value and err lanes" {
    const shared_cases = try buildSharedCases();

    for (shared_cases) |shared| {
        const slot = xarray_slot_view.fromRaw(shared.raw);

        switch (shared.kind) {
            .value => {
                try testing.expectEqual(shared.value.?, xa_value.toValue(shared.raw));
                try testing.expectEqual(shared.value, slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
            },
            .err => {
                try testing.expectEqual(shared.error_code.?, err_ptr.toErrorCode(shared.raw));
                try testing.expectEqual(shared.error_code, slot.errorCode());
                try testing.expectEqual(@as(?usize, null), slot.value());
            },
            .pointer => {
                try testing.expectEqual(shared.pointer, slot.pointerValue());
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
            },
            .null => {
                try testing.expectEqual(@as(?usize, null), slot.value());
                try testing.expectEqual(@as(?usize, null), slot.pointerValue());
                try testing.expectEqual(@as(?isize, null), slot.errorCode());
            },
        }
    }
}

test "shared dump parity counts keep the live seven-case packet stable" {
    const shared_cases = try buildSharedCases();
    var null_count: usize = 0;
    var value_count: usize = 0;
    var pointer_count: usize = 0;
    var err_count: usize = 0;
    var tagged_internal_count: usize = 0;

    for (shared_cases) |shared| {
        switch (shared.kind) {
            .null => null_count += 1,
            .value => value_count += 1,
            .pointer => pointer_count += 1,
            .err => err_count += 1,
        }
        if (shared.tagged_internal) {
            tagged_internal_count += 1;
        }
    }

    try testing.expectEqual(@as(usize, 1), null_count);
    try testing.expectEqual(@as(usize, 2), value_count);
    try testing.expectEqual(@as(usize, 2), pointer_count);
    try testing.expectEqual(@as(usize, 2), err_count);
    try testing.expectEqual(@as(usize, 4), tagged_internal_count);
}
