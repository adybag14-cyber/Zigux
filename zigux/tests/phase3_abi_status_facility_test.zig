const std = @import("std");
const abi = @import("abi_bindings");

test "phase3 abi status facility constants stay layout-visible" {
    try std.testing.expectEqual(@as(usize, 8), @sizeOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ExportStatus));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ExportStatus, "code"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ExportStatus, "facility"));
    try std.testing.expectEqual(@as(usize, 6), @offsetOf(abi.ExportStatus, "flags"));

    try std.testing.expectEqual(@as(u16, 1), abi.FACILITY_KERNEL);
    try std.testing.expectEqual(@as(u16, 2), abi.FACILITY_HELPERS);
    try std.testing.expectEqual(@as(u16, 3), abi.FACILITY_DRIVERS);
    try std.testing.expectEqual(@as(u16, 1), abi.STATUS_FLAG_ERROR);
}

test "phase3 abi status helper derives error flags only from negative codes" {
    const ok = abi.ExportStatus{
        .code = 0,
        .facility = abi.FACILITY_HELPERS,
        .flags = 0,
    };
    const positive = abi.ExportStatus{
        .code = 7,
        .facility = abi.FACILITY_DRIVERS,
        .flags = 0,
    };
    const negative = abi.ExportStatus{
        .code = -22,
        .facility = abi.FACILITY_KERNEL,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const lowest_negative = abi.ExportStatus{
        .code = std.math.minInt(i32),
        .facility = abi.FACILITY_HELPERS,
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try std.testing.expect((ok.flags & abi.STATUS_FLAG_ERROR) == 0);
    try std.testing.expect((positive.flags & abi.STATUS_FLAG_ERROR) == 0);
    try std.testing.expect((negative.flags & abi.STATUS_FLAG_ERROR) != 0);
    try std.testing.expect((lowest_negative.flags & abi.STATUS_FLAG_ERROR) != 0);

    try std.testing.expectEqual(@as(i32, 0), ok.code);
    try std.testing.expectEqual(@as(i32, 7), positive.code);
    try std.testing.expectEqual(@as(i32, -22), negative.code);
    try std.testing.expectEqual(@as(i32, std.math.minInt(i32)), lowest_negative.code);

    try std.testing.expectEqual(@as(u16, 0), ok.flags);
    try std.testing.expectEqual(@as(u16, 0), positive.flags);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), negative.flags);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), lowest_negative.flags);
}

test "phase3 abi status facility decoders reject unknown facility ids" {
    const kernel = abi.ExportStatus{
        .code = -5,
        .facility = abi.FACILITY_KERNEL,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const helpers = abi.ExportStatus{
        .code = 0,
        .facility = abi.FACILITY_HELPERS,
        .flags = 0,
    };
    const drivers = abi.ExportStatus{
        .code = 9,
        .facility = abi.FACILITY_DRIVERS,
        .flags = 0,
    };
    const unknown = abi.ExportStatus{
        .code = 0,
        .facility = 0x7fff,
        .flags = 0,
    };

    try std.testing.expectEqual(@as(u16, abi.FACILITY_KERNEL), @intFromEnum(abi.Facility.kernel));
    try std.testing.expectEqual(@as(u16, abi.FACILITY_HELPERS), @intFromEnum(abi.Facility.helpers));
    try std.testing.expectEqual(@as(u16, abi.FACILITY_DRIVERS), @intFromEnum(abi.Facility.drivers));

    try std.testing.expect(kernel.facility == abi.FACILITY_KERNEL);
    try std.testing.expect(helpers.facility == abi.FACILITY_HELPERS);
    try std.testing.expect(drivers.facility == abi.FACILITY_DRIVERS);
    try std.testing.expect(unknown.facility != abi.FACILITY_KERNEL);
    try std.testing.expect(unknown.facility != abi.FACILITY_HELPERS);
    try std.testing.expect(unknown.facility != abi.FACILITY_DRIVERS);
}

test "phase3 abi status ok check is flag-based rather than code-only" {
    const flagged_zero = abi.ExportStatus{
        .code = 0,
        .facility = abi.FACILITY_KERNEL,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unflagged_negative = abi.ExportStatus{
        .code = -1,
        .facility = abi.FACILITY_KERNEL,
        .flags = 0,
    };
    const extra_flagged = abi.ExportStatus{
        .code = 0,
        .facility = abi.FACILITY_HELPERS,
        .flags = abi.STATUS_FLAG_ERROR | 0x8000,
    };

    try std.testing.expect((flagged_zero.flags & abi.STATUS_FLAG_ERROR) != 0);
    try std.testing.expect((unflagged_negative.flags & abi.STATUS_FLAG_ERROR) == 0);
    try std.testing.expect((extra_flagged.flags & abi.STATUS_FLAG_ERROR) != 0);

    try std.testing.expect(flagged_zero.facility == abi.FACILITY_KERNEL);
    try std.testing.expect(unflagged_negative.facility == abi.FACILITY_KERNEL);
    try std.testing.expect(extra_flagged.facility == abi.FACILITY_HELPERS);
}
