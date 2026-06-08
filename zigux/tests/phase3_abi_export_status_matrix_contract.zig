const std = @import("std");

const abi = @import("abi_bindings");

const StatusCase = struct {
    code: i32,
    facility: abi.Facility,
    expect_error_flag: bool,
};

fn expectStatus(case: StatusCase) !void {
    const status = abi.makeStatus(case.code, case.facility);
    const expected_flags: u16 = if (case.expect_error_flag) abi.STATUS_FLAG_ERROR else 0;

    try std.testing.expectEqual(case.code, status.code);
    try std.testing.expectEqual(@as(u16, @intFromEnum(case.facility)), status.facility);
    try std.testing.expectEqual(expected_flags, status.flags);
    try std.testing.expectEqual(!case.expect_error_flag, abi.statusIsOk(status));
    try std.testing.expect(abi.statusHasKnownFacility(status));
}

test "export status matrix keeps facility relays closed" {
    try std.testing.expectEqual(@as(?abi.Facility, .kernel), abi.facilityFromInt(abi.FACILITY_KERNEL));
    try std.testing.expectEqual(@as(?abi.Facility, .helpers), abi.facilityFromInt(abi.FACILITY_HELPERS));
    try std.testing.expectEqual(@as(?abi.Facility, .drivers), abi.facilityFromInt(abi.FACILITY_DRIVERS));

    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_KERNEL));
    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_HELPERS));
    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_DRIVERS));

    try std.testing.expectEqual(@as(?abi.Facility, null), abi.facilityFromInt(0));
    try std.testing.expectEqual(@as(?abi.Facility, null), abi.facilityFromInt(4));
    try std.testing.expectEqual(@as(?abi.Facility, null), abi.facilityFromInt(std.math.maxInt(u16)));
    try std.testing.expect(!abi.facilityIsKnown(0));
    try std.testing.expect(!abi.facilityIsKnown(4));
    try std.testing.expect(!abi.facilityIsKnown(std.math.maxInt(u16)));
}

test "export status matrix marks only negative generated codes as errors" {
    try expectStatus(.{
        .code = 0,
        .facility = .kernel,
        .expect_error_flag = false,
    });
    try expectStatus(.{
        .code = 1,
        .facility = .helpers,
        .expect_error_flag = false,
    });
    try expectStatus(.{
        .code = std.math.maxInt(i32),
        .facility = .drivers,
        .expect_error_flag = false,
    });
    try expectStatus(.{
        .code = -1,
        .facility = .kernel,
        .expect_error_flag = true,
    });
    try expectStatus(.{
        .code = std.math.minInt(i32),
        .facility = .drivers,
        .expect_error_flag = true,
    });
}

test "export status matrix keeps okStatus as the zero-code shorthand" {
    inline for (.{ abi.Facility.kernel, abi.Facility.helpers, abi.Facility.drivers }) |facility| {
        const ok = abi.okStatus(facility);
        const direct = abi.makeStatus(0, facility);

        try std.testing.expect(std.meta.eql(direct, ok));
        try std.testing.expect(abi.statusIsOk(ok));
        try std.testing.expect(abi.statusHasKnownFacility(ok));
        try std.testing.expectEqual(@as(i32, 0), ok.code);
        try std.testing.expectEqual(@as(u16, 0), ok.flags);
        try std.testing.expectEqual(@as(u16, @intFromEnum(facility)), ok.facility);
    }
}

test "export status matrix separates error flags from facility validity" {
    const flagged_positive = abi.ExportStatus{
        .code = 27,
        .facility = abi.FACILITY_HELPERS,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unknown_ok = abi.ExportStatus{
        .code = 0,
        .facility = 0,
        .flags = 0,
    };
    const unknown_error = abi.ExportStatus{
        .code = -27,
        .facility = std.math.maxInt(u16),
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try std.testing.expect(!abi.statusIsOk(flagged_positive));
    try std.testing.expect(abi.statusHasKnownFacility(flagged_positive));

    try std.testing.expect(abi.statusIsOk(unknown_ok));
    try std.testing.expect(!abi.statusHasKnownFacility(unknown_ok));

    try std.testing.expect(!abi.statusIsOk(unknown_error));
    try std.testing.expect(!abi.statusHasKnownFacility(unknown_error));
}
