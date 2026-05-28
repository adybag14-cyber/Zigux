const std = @import("std");
const abi = @import("../bindings/abi.zig");

fn statusHasConsistentErrorFlag(status: abi.ExportStatus) bool {
    const flagged = (status.flags & abi.STATUS_FLAG_ERROR) != 0;
    return if (status.code < 0) flagged else !flagged;
}

fn statusIsRuntimeSafe(status: abi.ExportStatus) bool {
    return abi.statusHasKnownFacility(status) and statusHasConsistentErrorFlag(status);
}

test "phase3 export status packet keeps constructor-shaped statuses runtime-safe" {
    const ok = abi.okStatus(.helpers);
    const negative = abi.makeStatus(-22, .kernel);
    const positive = abi.makeStatus(7, .drivers);

    try std.testing.expect(abi.statusIsOk(ok));
    try std.testing.expect(!abi.statusIsOk(negative));
    try std.testing.expect(abi.statusIsOk(positive));

    try std.testing.expect(statusHasConsistentErrorFlag(ok));
    try std.testing.expect(statusHasConsistentErrorFlag(negative));
    try std.testing.expect(statusHasConsistentErrorFlag(positive));

    try std.testing.expect(statusIsRuntimeSafe(ok));
    try std.testing.expect(statusIsRuntimeSafe(negative));
    try std.testing.expect(statusIsRuntimeSafe(positive));
}

test "phase3 export status packet rejects malformed flag and facility combinations" {
    const negative_without_error = abi.ExportStatus{
        .code = -22,
        .facility = abi.FACILITY_KERNEL,
        .flags = 0,
    };
    const positive_with_error = abi.ExportStatus{
        .code = 7,
        .facility = abi.FACILITY_DRIVERS,
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unknown_facility = abi.ExportStatus{
        .code = 0,
        .facility = 9,
        .flags = 0,
    };

    try std.testing.expect(abi.statusHasKnownFacility(negative_without_error));
    try std.testing.expect(abi.statusHasKnownFacility(positive_with_error));
    try std.testing.expect(!abi.statusHasKnownFacility(unknown_facility));

    try std.testing.expect(abi.statusIsOk(negative_without_error));
    try std.testing.expect(!abi.statusIsOk(positive_with_error));
    try std.testing.expect(abi.statusIsOk(unknown_facility));

    try std.testing.expect(!statusHasConsistentErrorFlag(negative_without_error));
    try std.testing.expect(!statusHasConsistentErrorFlag(positive_with_error));
    try std.testing.expect(statusHasConsistentErrorFlag(unknown_facility));

    try std.testing.expect(!statusIsRuntimeSafe(negative_without_error));
    try std.testing.expect(!statusIsRuntimeSafe(positive_with_error));
    try std.testing.expect(!statusIsRuntimeSafe(unknown_facility));
}

test "phase3 export status packet keeps facility decoding explicit for runtime review" {
    const ok = abi.okStatus(.helpers);
    const err = abi.makeStatus(-71, .drivers);
    const unknown = abi.ExportStatus{
        .code = -71,
        .facility = 9,
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try std.testing.expectEqual(@as(?abi.Facility, .helpers), abi.facilityFromInt(ok.facility));
    try std.testing.expectEqual(@as(?abi.Facility, .drivers), abi.facilityFromInt(err.facility));
    try std.testing.expectEqual(@as(?abi.Facility, null), abi.facilityFromInt(unknown.facility));

    try std.testing.expect(statusIsRuntimeSafe(ok));
    try std.testing.expect(statusIsRuntimeSafe(err));
    try std.testing.expect(!statusIsRuntimeSafe(unknown));
}
