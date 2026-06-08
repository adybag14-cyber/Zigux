// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub const Error = error{Invalid};

pub const LinearRange = struct {
    min: u32,
    min_sel: u32,
    max_sel: u32,
    step: u32,
};

pub const SelectorResult = struct {
    selector: u32,
    found: bool,
};

pub fn valuesInRange(r: ?*const LinearRange) u32 {
    const range = r orelse return 0;
    return range.max_sel - range.min_sel + 1;
}

pub fn valuesInRangeArray(ranges: []const LinearRange) u32 {
    var total: u32 = 0;
    for (ranges) |*range| {
        const values = valuesInRange(range);
        if (values == 0) return 0;
        total += values;
    }
    return total;
}

pub fn maxValue(r: *const LinearRange) u32 {
    return r.min + (r.max_sel - r.min_sel) * r.step;
}

pub fn getValue(r: *const LinearRange, selector: u32) Error!u32 {
    if (r.min_sel > selector or r.max_sel < selector) return Error.Invalid;
    return r.min + (selector - r.min_sel) * r.step;
}

pub fn getValueArray(ranges: []const LinearRange, selector: u32) Error!u32 {
    for (ranges) |*range| {
        if (range.min_sel <= selector and range.max_sel >= selector) {
            return getValue(range, selector);
        }
    }
    return Error.Invalid;
}

pub fn selectorLow(r: *const LinearRange, val: u32) Error!SelectorResult {
    if (r.min > val) return Error.Invalid;
    if (maxValue(r) < val) return .{ .selector = r.max_sel, .found = false };
    return .{
        .selector = if (r.step == 0) r.min_sel else (val - r.min) / r.step + r.min_sel,
        .found = true,
    };
}

pub fn selectorLowArray(ranges: []const LinearRange, val: u32) Error!SelectorResult {
    var result: ?SelectorResult = null;
    for (ranges) |*range| {
        const candidate = selectorLow(range, val) catch continue;
        result = candidate;
        if (candidate.found) return candidate;
    }
    return result orelse Error.Invalid;
}

pub fn selectorHigh(r: *const LinearRange, val: u32) Error!SelectorResult {
    if (maxValue(r) < val) return Error.Invalid;
    if (r.min > val) return .{ .selector = r.min_sel, .found = false };
    return .{
        .selector = if (r.step == 0) r.max_sel else divRoundUp(val - r.min, r.step) + r.min_sel,
        .found = true,
    };
}

pub fn selectorHighArray(ranges: []const LinearRange, val: u32) Error!SelectorResult {
    for (ranges) |*range| {
        if (selectorHigh(range, val)) |candidate| {
            return candidate;
        } else |_| {}
    }
    return Error.Invalid;
}

pub fn selectorWithin(r: *const LinearRange, val: u32) u32 {
    if (r.min > val) return r.min_sel;
    if (maxValue(r) < val) return r.max_sel;
    return if (r.step == 0) r.min_sel else (val - r.min) / r.step + r.min_sel;
}

fn divRoundUp(value: u32, divisor: u32) u32 {
    return (value + divisor - 1) / divisor;
}

test "linear range value helpers mirror C behavior" {
    const ranges = [_]LinearRange{
        .{ .min = 100, .min_sel = 0, .max_sel = 3, .step = 25 },
        .{ .min = 300, .min_sel = 4, .max_sel = 6, .step = 50 },
    };

    try std.testing.expectEqual(@as(u32, 4), valuesInRange(&ranges[0]));
    try std.testing.expectEqual(@as(u32, 7), valuesInRangeArray(&ranges));
    try std.testing.expectEqual(@as(u32, 175), maxValue(&ranges[0]));
    try std.testing.expectEqual(@as(u32, 150), try getValue(&ranges[0], 2));
    try std.testing.expectEqual(@as(u32, 400), try getValueArray(&ranges, 6));
    try std.testing.expectError(Error.Invalid, getValue(&ranges[0], 4));
}

test "linear range selector helpers cover low high and clamped modes" {
    const ranges = [_]LinearRange{
        .{ .min = 100, .min_sel = 0, .max_sel = 3, .step = 25 },
        .{ .min = 300, .min_sel = 4, .max_sel = 6, .step = 50 },
    };

    try std.testing.expectEqual(SelectorResult{ .selector = 2, .found = true }, try selectorLow(&ranges[0], 160));
    try std.testing.expectEqual(SelectorResult{ .selector = 3, .found = false }, try selectorLow(&ranges[0], 250));
    try std.testing.expectEqual(SelectorResult{ .selector = 3, .found = false }, try selectorLowArray(&ranges, 250));
    try std.testing.expectEqual(SelectorResult{ .selector = 2, .found = true }, try selectorHigh(&ranges[0], 126));
    try std.testing.expectEqual(SelectorResult{ .selector = 4, .found = false }, try selectorHighArray(&ranges, 250));
    try std.testing.expectEqual(@as(u32, 0), selectorWithin(&ranges[0], 50));
    try std.testing.expectEqual(@as(u32, 3), selectorWithin(&ranges[0], 250));
}
