const std = @import("std");
const testing = std.testing;

const shim = @import("export_shim");

test "export shim success statuses stay explicit for every known facility" {
    const cases = [_]shim.Facility{
        .kernel,
        .helpers,
        .drivers,
    };

    inline for (cases) |facility| {
        const status = shim.okStatus(facility);

        try testing.expect(shim.statusIsOk(status));
        try testing.expect(shim.statusHasKnownFacility(status));
        try testing.expect(shim.facilityIsKnown(status.facility));
        try testing.expectEqual(@as(i32, 0), status.code);
        try testing.expectEqual(@as(u16, @intFromEnum(facility)), status.facility);
        try testing.expectEqual(@as(u16, 0), status.flags);
        try testing.expectEqual(@as(?shim.Facility, facility), shim.facilityFromInt(status.facility));
    }
}

test "export shim positive status codes remain non-error success packets" {
    const soft_success = shim.errorStatus(7, .drivers);
    const deferred_success = shim.errorStatus(1, .helpers);

    try testing.expect(shim.statusIsOk(soft_success));
    try testing.expect(shim.statusIsOk(deferred_success));
    try testing.expect(shim.statusHasKnownFacility(soft_success));
    try testing.expect(shim.statusHasKnownFacility(deferred_success));

    try testing.expectEqual(@as(i32, 7), soft_success.code);
    try testing.expectEqual(@as(i32, 1), deferred_success.code);
    try testing.expectEqual(@as(u16, @intFromEnum(shim.Facility.drivers)), soft_success.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(shim.Facility.helpers)), deferred_success.facility);
    try testing.expectEqual(@as(u16, 0), soft_success.flags);
    try testing.expectEqual(@as(u16, 0), deferred_success.flags);
}

test "export shim negative and manually flagged statuses do not pass as success" {
    const negative = shim.errorStatus(-22, .kernel);
    const flagged_positive = shim.ExportStatus{
        .code = 7,
        .facility = @intFromEnum(shim.Facility.helpers),
        .flags = 1,
    };

    try testing.expect(!shim.statusIsOk(negative));
    try testing.expect(!shim.statusIsOk(flagged_positive));
    try testing.expect(shim.statusHasKnownFacility(negative));
    try testing.expect(shim.statusHasKnownFacility(flagged_positive));

    try testing.expectEqual(@as(i32, -22), negative.code);
    try testing.expectEqual(@as(u16, @intFromEnum(shim.Facility.kernel)), negative.facility);
    try testing.expectEqual(@as(u16, 1), negative.flags);
    try testing.expectEqual(@as(i32, 7), flagged_positive.code);
    try testing.expectEqual(@as(u16, @intFromEnum(shim.Facility.helpers)), flagged_positive.facility);
    try testing.expectEqual(@as(u16, 1), flagged_positive.flags);
}
