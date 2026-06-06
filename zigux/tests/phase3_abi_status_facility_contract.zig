const std = @import("std");

const abi = @import("abi_bindings");

test "status constructors derive error flag only from negative status codes" {
    const helper_ok = abi.okStatus(.helpers);
    const kernel_error = abi.makeStatus(-22, .kernel);
    const driver_positive = abi.makeStatus(7, .drivers);

    try std.testing.expect(abi.statusIsOk(helper_ok));
    try std.testing.expectEqual(@as(i32, 0), helper_ok.code);
    try std.testing.expectEqual(@as(u16, abi.FACILITY_HELPERS), helper_ok.facility);
    try std.testing.expectEqual(@as(u16, 0), helper_ok.flags);

    try std.testing.expect(!abi.statusIsOk(kernel_error));
    try std.testing.expectEqual(@as(i32, -22), kernel_error.code);
    try std.testing.expectEqual(@as(u16, abi.FACILITY_KERNEL), kernel_error.facility);
    try std.testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), kernel_error.flags);

    try std.testing.expect(abi.statusIsOk(driver_positive));
    try std.testing.expectEqual(@as(i32, 7), driver_positive.code);
    try std.testing.expectEqual(@as(u16, abi.FACILITY_DRIVERS), driver_positive.facility);
    try std.testing.expectEqual(@as(u16, 0), driver_positive.flags);
}

test "manual status packets use the explicit error flag for ok/error classification" {
    const flagged_positive = abi.ExportStatus{
        .code = 7,
        .facility = abi.FACILITY_DRIVERS,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const flagged_zero = abi.ExportStatus{
        .code = 0,
        .facility = abi.FACILITY_KERNEL,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const non_error_side_flag = abi.ExportStatus{
        .code = -5,
        .facility = abi.FACILITY_HELPERS,
        .flags = 2,
    };

    try std.testing.expect(!abi.statusIsOk(flagged_positive));
    try std.testing.expect(!abi.statusIsOk(flagged_zero));
    try std.testing.expect(abi.statusIsOk(non_error_side_flag));
}

test "facility decoding stays closed over the published facility roster" {
    try std.testing.expectEqual(@as(?abi.Facility, .kernel), abi.facilityFromInt(abi.FACILITY_KERNEL));
    try std.testing.expectEqual(@as(?abi.Facility, .helpers), abi.facilityFromInt(abi.FACILITY_HELPERS));
    try std.testing.expectEqual(@as(?abi.Facility, .drivers), abi.facilityFromInt(abi.FACILITY_DRIVERS));

    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_KERNEL));
    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_HELPERS));
    try std.testing.expect(abi.facilityIsKnown(abi.FACILITY_DRIVERS));
    try std.testing.expect(!abi.facilityIsKnown(0));
    try std.testing.expect(!abi.facilityIsKnown(4));
    try std.testing.expect(!abi.facilityIsKnown(std.math.maxInt(u16)));
}

test "status facility recognition is independent from status error state" {
    const known_error = abi.ExportStatus{
        .code = -95,
        .facility = abi.FACILITY_KERNEL,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unknown_ok = abi.ExportStatus{
        .code = 0,
        .facility = 99,
        .flags = 0,
    };
    const unknown_error = abi.ExportStatus{
        .code = -95,
        .facility = 99,
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try std.testing.expect(!abi.statusIsOk(known_error));
    try std.testing.expect(abi.statusHasKnownFacility(known_error));

    try std.testing.expect(abi.statusIsOk(unknown_ok));
    try std.testing.expect(!abi.statusHasKnownFacility(unknown_ok));

    try std.testing.expect(!abi.statusIsOk(unknown_error));
    try std.testing.expect(!abi.statusHasKnownFacility(unknown_error));
}
