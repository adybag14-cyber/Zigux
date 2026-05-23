const std = @import("std");
const testing = std.testing;

const err_ptr = @import("err_ptr");
const xa_value = @import("xa_value");
const xarray_slot_view = @import("xarray_slot_view");

const DumpCase = struct {
    name: []const u8,
    raw: usize,
    kind: xarray_slot_view.SlotKind,
    value: ?usize,
    error_code: ?isize,
    pointer: ?usize,
    tagged_internal: bool,
};

fn dumpCases() ![9]DumpCase {
    const inline_zero_raw = try xa_value.makeValue(0);
    const inline_small_raw = try xa_value.makeValue(29);
    const inline_limit_raw = try xa_value.makeValue(xa_value.safe_inline_limit);

    return .{
        .{ .name = "null", .raw = 0, .kind = .null, .value = null, .error_code = null, .pointer = null, .tagged_internal = false },
        .{ .name = "pointer_like", .raw = 64, .kind = .pointer, .value = null, .error_code = null, .pointer = 64, .tagged_internal = false },
        .{ .name = "inline_zero", .raw = inline_zero_raw, .kind = .value, .value = 0, .error_code = null, .pointer = null, .tagged_internal = true },
        .{ .name = "inline_small", .raw = inline_small_raw, .kind = .value, .value = 29, .error_code = null, .pointer = null, .tagged_internal = true },
        .{ .name = "inline_limit", .raw = inline_limit_raw, .kind = .value, .value = xa_value.safe_inline_limit, .error_code = null, .pointer = null, .tagged_internal = true },
        .{ .name = "gap_before_err_floor", .raw = err_ptr.err_floor - 1, .kind = .pointer, .value = null, .error_code = null, .pointer = err_ptr.err_floor - 1, .tagged_internal = false },
        .{ .name = "err_top", .raw = err_ptr.fromErrorCode(-1), .kind = .err, .value = null, .error_code = -1, .pointer = null, .tagged_internal = true },
        .{ .name = "err_enomem", .raw = err_ptr.fromErrorCode(-12), .kind = .err, .value = null, .error_code = -12, .pointer = null, .tagged_internal = true },
        .{ .name = "err_max", .raw = err_ptr.fromErrorCode(-4095), .kind = .err, .value = null, .error_code = -4095, .pointer = null, .tagged_internal = true },
    };
}

test "dump case matrix keeps slot classifications stable" {
    const cases = try dumpCases();

    const expected_names = [_][]const u8{
        "null",
        "pointer_like",
        "inline_zero",
        "inline_small",
        "inline_limit",
        "gap_before_err_floor",
        "err_top",
        "err_enomem",
        "err_max",
    };

    for (cases, expected_names) |case, expected_name| {
        const slot = xarray_slot_view.fromRaw(case.raw);

        try testing.expectEqualStrings(expected_name, case.name);
        try testing.expectEqual(case.kind, slot.kind());
        try testing.expectEqual(case.raw, slot.rawValue());
        try testing.expectEqual(case.value, slot.value());
        try testing.expectEqual(case.error_code, slot.errorCode());
        try testing.expectEqual(case.pointer, slot.pointerValue());
        try testing.expectEqual(case.tagged_internal, xarray_slot_view.isTaggedInternalEntry(case.raw));
    }
}

test "dump boundary representatives keep the current raw equations" {
    const cases = try dumpCases();

    try testing.expectEqual(@as(usize, 1), cases[2].raw);
    try testing.expectEqual(@as(usize, 59), cases[3].raw);
    try testing.expectEqual(err_ptr.err_floor - 2, cases[4].raw);
    try testing.expectEqual(err_ptr.err_floor - 1, cases[5].raw);
    try testing.expectEqual(err_ptr.err_floor, cases[8].raw);
    try testing.expectEqual(std.math.maxInt(usize), cases[6].raw);
    try testing.expectEqual(std.math.maxInt(usize) - 11, cases[7].raw);

    try testing.expectEqual(cases[4].raw + 1, cases[5].raw);
    try testing.expectEqual(cases[5].raw + 1, cases[8].raw);
    try testing.expect(cases[7].raw >= err_ptr.err_floor);
    try testing.expect(cases[7].raw < cases[6].raw);
}
