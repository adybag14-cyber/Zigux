const std = @import("std");
const testing = std.testing;

const export_shim = @import("export_shim");
const dev_t = @import("dev_t_binding");

const invalid_argument: i32 = -22;

test "export shim keeps dev_t field layout and component boundaries explicit" {
    try testing.expectEqual(@as(usize, 8), @sizeOf(export_shim.DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(export_shim.DevTFields));
    try testing.expectEqual(@as(usize, 0), @offsetOf(export_shim.DevTFields, "major"));
    try testing.expectEqual(@as(usize, 4), @offsetOf(export_shim.DevTFields, "minor"));

    const max_fields = export_shim.makeDevTFields(dev_t.max_major, dev_t.max_minor);
    const invalid_major = export_shim.makeDevTFields(dev_t.max_major + 1, 0);
    const invalid_minor = export_shim.makeDevTFields(0, dev_t.max_minor + 1);

    try testing.expect(export_shim.deviceFieldsAreValid(max_fields));
    try testing.expect(export_shim.deviceComponentsAreValid(dev_t.max_major, dev_t.max_minor));
    try testing.expect(!export_shim.deviceFieldsAreValid(invalid_major));
    try testing.expect(!export_shim.deviceFieldsAreValid(invalid_minor));
    try testing.expect(!export_shim.deviceComponentsAreValid(dev_t.max_major + 1, 0));
    try testing.expect(!export_shim.deviceComponentsAreValid(0, dev_t.max_minor + 1));
}

test "export shim keeps dev_t encode decode round-trips guarded by validation" {
    const fields = export_shim.makeDevTFields(11, 29);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse unreachable;
    const decoded = export_shim.decodeDeviceNumber(encoded);
    const invalid = export_shim.makeDevTFields(dev_t.max_major + 1, 0);
    const max_encoded = export_shim.encodeDeviceNumber(export_shim.makeDevTFields(dev_t.max_major, dev_t.max_minor)) orelse unreachable;
    const max_decoded = export_shim.decodeDeviceNumber(max_encoded);

    try testing.expectEqual(dev_t.makeDeviceNumber(11, 29), encoded);
    try testing.expectEqual(@as(u32, 11), decoded.major);
    try testing.expectEqual(@as(u32, 29), decoded.minor);
    try testing.expectEqual(dev_t.max_major, max_decoded.major);
    try testing.expectEqual(dev_t.max_minor, max_decoded.minor);
    try testing.expect(export_shim.encodeDeviceNumber(invalid) == null);
}

test "export shim relays dev_t field validation through status helpers" {
    const valid = export_shim.validateDeviceFields(export_shim.makeDevTFields(dev_t.max_major, dev_t.max_minor));
    const invalid_major = export_shim.validateDeviceFields(export_shim.makeDevTFields(dev_t.max_major + 1, 0));
    const invalid_minor = export_shim.validateDeviceNumber(0, dev_t.max_minor + 1);

    try testing.expect(export_shim.statusIsOk(valid));
    try testing.expect(!export_shim.statusIsOk(invalid_major));
    try testing.expect(!export_shim.statusIsOk(invalid_minor));

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, invalid_argument), invalid_major.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_minor.code);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_major.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(export_shim.Facility.kernel)), invalid_minor.facility);
    try testing.expect(!export_shim.statusIsOk(invalid_major));
    try testing.expect(!export_shim.statusIsOk(invalid_minor));
}

test "export shim keeps dev_t range ordering and invalid endpoint statuses explicit" {
    const first = export_shim.makeDevTFields(1, 2);
    const same = export_shim.makeDevTFields(1, 2);
    const later_minor = export_shim.makeDevTFields(1, 3);
    const later_major = export_shim.makeDevTFields(2, 0);
    const invalid_endpoint = export_shim.makeDevTFields(0, dev_t.max_minor + 1);

    try testing.expect(export_shim.deviceRangeIsValid(first, same));
    try testing.expect(export_shim.deviceRangeIsValid(first, later_minor));
    try testing.expect(export_shim.deviceRangeIsValid(first, later_major));
    try testing.expect(!export_shim.deviceRangeIsValid(later_minor, first));
    try testing.expect(!export_shim.deviceRangeIsValid(first, invalid_endpoint));

    const ok_same = export_shim.validateDeviceRange(first, same);
    const ok_later = export_shim.validateDeviceRange(first, later_major);
    const bad_reverse = export_shim.validateDeviceRange(later_minor, first);
    const bad_endpoint = export_shim.validateDeviceRange(first, invalid_endpoint);

    try testing.expect(export_shim.statusIsOk(ok_same));
    try testing.expect(export_shim.statusIsOk(ok_later));
    try testing.expect(!export_shim.statusIsOk(bad_reverse));
    try testing.expect(!export_shim.statusIsOk(bad_endpoint));
    try testing.expectEqual(@as(i32, invalid_argument), bad_reverse.code);
    try testing.expectEqual(@as(i32, invalid_argument), bad_endpoint.code);
}
