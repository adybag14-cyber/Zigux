const std = @import("std");
const hweight = @import("hweight");

fn expectSubsetClear8(value: u32, subset: u32) !void {
    try std.testing.expectEqual(@as(u32, 0), subset & ~value);

    const remaining = value ^ subset;
    try std.testing.expectEqual(
        hweight.swHweight8(value),
        hweight.swHweight8(remaining) + hweight.swHweight8(subset),
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight8(value),
        hweight.__sw_hweight8(remaining) + hweight.__sw_hweight8(subset),
    );
}

fn expectSubsetClear16(value: u32, subset: u32) !void {
    try std.testing.expectEqual(@as(u32, 0), subset & ~value);

    const remaining = value ^ subset;
    try std.testing.expectEqual(
        hweight.swHweight16(value),
        hweight.swHweight16(remaining) + hweight.swHweight16(subset),
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight16(value),
        hweight.__sw_hweight16(remaining) + hweight.__sw_hweight16(subset),
    );
}

fn expectSubsetClear32(value: u32, subset: u32) !void {
    try std.testing.expectEqual(@as(u32, 0), subset & ~value);

    const remaining = value ^ subset;
    try std.testing.expectEqual(
        hweight.swHweight32(value),
        hweight.swHweight32(remaining) + hweight.swHweight32(subset),
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight32(value),
        hweight.__sw_hweight32(remaining) + hweight.__sw_hweight32(subset),
    );
}

fn expectSubsetClear64(value: u64, subset: u64) !void {
    try std.testing.expectEqual(@as(u64, 0), subset & ~value);

    const remaining = value ^ subset;
    try std.testing.expectEqual(
        hweight.swHweight64(value),
        hweight.swHweight64(remaining) + hweight.swHweight64(subset),
    );
    try std.testing.expectEqual(
        hweight.__sw_hweight64(value),
        hweight.__sw_hweight64(remaining) + hweight.__sw_hweight64(subset),
    );
}

fn expectSubsetClearLong(value: usize, subset: usize) !void {
    try std.testing.expectEqual(@as(usize, 0), subset & ~value);

    const remaining = value ^ subset;
    try std.testing.expectEqual(
        hweight.hweightLong(value),
        hweight.hweightLong(remaining) + hweight.hweightLong(subset),
    );
    try std.testing.expectEqual(
        hweight.hweight_long(value),
        hweight.hweight_long(remaining) + hweight.hweight_long(subset),
    );
}

test "hweight subset clear replay keeps 8-bit population sums aligned" {
    var value: u32 = 0;
    while (value < 0x100) : (value += 1) {
        try expectSubsetClear8(value, value & 0x55);
        try expectSubsetClear8(value, value & 0xaa);
        try expectSubsetClear8(value, value & 0x33);
    }
}

test "hweight subset clear replay stays aligned across fixed widths and native routing" {
    for ([_]struct { value: u32, subset: u32 }{
        .{ .value = 0x0000, .subset = 0x0000 },
        .{ .value = 0x00ff, .subset = 0x0055 },
        .{ .value = 0x1234, .subset = 0x1030 },
        .{ .value = 0xa55a, .subset = 0x0550 },
        .{ .value = 0xffff, .subset = 0x0f0f },
    }) |case| {
        try expectSubsetClear16(case.value, case.subset);
    }

    for ([_]struct { value: u32, subset: u32 }{
        .{ .value = 0x0000_0000, .subset = 0x0000_0000 },
        .{ .value = 0x00ff_00ff, .subset = 0x0055_0055 },
        .{ .value = 0x1234_5678, .subset = 0x1030_5060 },
        .{ .value = 0xa55a_5aa5, .subset = 0x0550_0a05 },
        .{ .value = 0xffff_ffff, .subset = 0x0f0f_f0f0 },
    }) |case| {
        try expectSubsetClear32(case.value, case.subset);
    }

    for ([_]struct { value: u64, subset: u64 }{
        .{ .value = 0x0000_0000_0000_0000, .subset = 0x0000_0000_0000_0000 },
        .{ .value = 0x00ff_00ff_00ff_00ff, .subset = 0x0055_0055_0055_0055 },
        .{ .value = 0x0123_4567_89ab_cdef, .subset = 0x0022_4466_88aa_00ef },
        .{ .value = 0xa55a_5aa5_c33c_3cc3, .subset = 0x0550_0a05_0330_00c3 },
        .{ .value = 0xffff_ffff_ffff_ffff, .subset = 0x0f0f_f0f0_3333_cccc },
    }) |case| {
        try expectSubsetClear64(case.value, case.subset);
    }

    if (@sizeOf(usize) == 4) {
        for ([_]struct { value: usize, subset: usize }{
            .{ .value = 0x0000_0000, .subset = 0x0000_0000 },
            .{ .value = 0x00ff_00ff, .subset = 0x0055_0055 },
            .{ .value = 0x1234_5678, .subset = 0x1030_5060 },
            .{ .value = 0xa55a_5aa5, .subset = 0x0550_0a05 },
            .{ .value = 0xffff_ffff, .subset = 0x0f0f_f0f0 },
        }) |case| {
            try expectSubsetClearLong(case.value, case.subset);
        }
    } else {
        for ([_]struct { value: usize, subset: usize }{
            .{ .value = 0x0000_0000_0000_0000, .subset = 0x0000_0000_0000_0000 },
            .{ .value = 0x00ff_00ff_00ff_00ff, .subset = 0x0055_0055_0055_0055 },
            .{ .value = 0x0123_4567_89ab_cdef, .subset = 0x0022_4466_88aa_00ef },
            .{ .value = 0xa55a_5aa5_c33c_3cc3, .subset = 0x0550_0a05_0330_00c3 },
            .{ .value = 0xffff_ffff_ffff_ffff, .subset = 0x0f0f_f0f0_3333_cccc },
        }) |case| {
            try expectSubsetClearLong(case.value, case.subset);
        }
    }
}
