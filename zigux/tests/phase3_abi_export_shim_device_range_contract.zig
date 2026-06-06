const std = @import("std");
const testing = std.testing;

const export_shim = @import("export_shim");

fn expectOk(status: export_shim.ExportStatus) !void {
    try testing.expect(export_shim.statusIsOk(status));
    try testing.expectEqual(@as(i32, 0), status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), status.facility);
    try testing.expectEqual(@as(u16, 0), status.flags);
}

fn expectInvalidArgument(status: export_shim.ExportStatus) !void {
    try testing.expect(!export_shim.statusIsOk(status));
    try testing.expectEqual(@as(i32, -22), status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), status.facility);
    try testing.expectEqual(@as(u16, 1), status.flags);
}

test "export shim accepts same-device and forward dev_t ranges" {
    const same = export_shim.makeDevTFields(12, 34);
    const later_minor = export_shim.makeDevTFields(12, 35);
    const later_major = export_shim.makeDevTFields(13, 0);

    try testing.expect(export_shim.deviceFieldsAreValid(same));
    try testing.expect(export_shim.deviceRangeIsValid(same, same));
    try testing.expect(export_shim.deviceRangeIsValid(same, later_minor));
    try testing.expect(export_shim.deviceRangeIsValid(same, later_major));

    try expectOk(export_shim.validateDeviceFields(same));
    try expectOk(export_shim.validateDeviceRange(same, same));
    try expectOk(export_shim.validateDeviceRange(same, later_minor));
    try expectOk(export_shim.validateDeviceRange(same, later_major));
}

test "export shim rejects reversed dev_t ranges through status helpers" {
    const first = export_shim.makeDevTFields(12, 35);
    const earlier_minor = export_shim.makeDevTFields(12, 34);
    const earlier_major = export_shim.makeDevTFields(11, 99);

    try testing.expect(!export_shim.deviceRangeIsValid(first, earlier_minor));
    try testing.expect(!export_shim.deviceRangeIsValid(first, earlier_major));

    try expectInvalidArgument(export_shim.validateDeviceRange(first, earlier_minor));
    try expectInvalidArgument(export_shim.validateDeviceRange(first, earlier_major));
}

test "export shim rejects out-of-range dev_t fields before range ordering" {
    const valid = export_shim.makeDevTFields(12, 34);
    const invalid_major = export_shim.makeDevTFields(4096, 0);
    const invalid_minor = export_shim.makeDevTFields(0, 1 << 20);

    try testing.expect(!export_shim.deviceFieldsAreValid(invalid_major));
    try testing.expect(!export_shim.deviceFieldsAreValid(invalid_minor));
    try testing.expect(!export_shim.deviceRangeIsValid(valid, invalid_minor));
    try testing.expect(!export_shim.deviceRangeIsValid(invalid_major, valid));
    try testing.expect(!export_shim.deviceRangeIsValid(invalid_major, invalid_minor));

    try expectInvalidArgument(export_shim.validateDeviceFields(invalid_major));
    try expectInvalidArgument(export_shim.validateDeviceFields(invalid_minor));
    try expectInvalidArgument(export_shim.validateDeviceRange(valid, invalid_minor));
    try expectInvalidArgument(export_shim.validateDeviceRange(invalid_major, valid));
    try expectInvalidArgument(export_shim.validateDeviceRange(invalid_major, invalid_minor));
}

test "export shim encodes only valid dev_t fields" {
    const fields = export_shim.makeDevTFields(73, 0x34567);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse return error.TestUnexpectedResult;
    const decoded = export_shim.decodeDeviceNumber(encoded);
    const invalid = export_shim.makeDevTFields(4096, 0);

    try testing.expect(export_shim.deviceFieldsAreValid(fields));
    try testing.expect(export_shim.deviceComponentsAreValid(fields.major, fields.minor));
    try testing.expect(export_shim.deviceFieldsAreValid(decoded));
    try testing.expectEqual(fields.major, decoded.major);
    try testing.expectEqual(fields.minor, decoded.minor);
    try testing.expect(export_shim.encodeDeviceNumber(invalid) == null);
}
