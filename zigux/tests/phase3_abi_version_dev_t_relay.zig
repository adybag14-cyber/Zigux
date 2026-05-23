const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const dev_t = @import("dev_t_binding");
const export_shim = @import("export_shim");
const version = @import("version_binding");

test "phase3 abi version relay keeps export shim aligned with version binding" {
    const live = export_shim.currentVersion();
    const stale_major = export_shim.Version{
        .abi_major = version.abi_major + 1,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision,
    };
    const stale_minor = export_shim.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor + 1,
        .header_family_revision = version.header_family_revision,
    };
    const stale_revision = export_shim.Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision + 1,
    };

    try testing.expect(version.eql(live, version.current()));
    try testing.expect(export_shim.versionMatchesCurrent(live));
    try testing.expect(version.matchesCurrent(live));

    try testing.expect(!export_shim.versionMatchesCurrent(stale_major));
    try testing.expect(!export_shim.versionMatchesCurrent(stale_minor));
    try testing.expect(!export_shim.versionMatchesCurrent(stale_revision));

    try testing.expect(std.meta.eql(version.validate(live), export_shim.validateVersion(live)));
    try testing.expect(std.meta.eql(version.validate(stale_major), export_shim.validateVersion(stale_major)));
    try testing.expect(std.meta.eql(version.validate(stale_minor), export_shim.validateVersion(stale_minor)));
    try testing.expect(std.meta.eql(version.validate(stale_revision), export_shim.validateVersion(stale_revision)));

    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), export_shim.validateVersion(live)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), export_shim.validateVersion(stale_major)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), export_shim.validateVersion(stale_minor)));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), export_shim.validateVersion(stale_revision)));
}

test "phase3 abi dev_t relay keeps export shim packing aligned with the binding" {
    const fields = export_shim.makeDevTFields(11, 29);
    const encoded = export_shim.encodeDeviceNumber(fields) orelse return error.TestUnexpectedResult;
    const decoded = export_shim.decodeDeviceNumber(encoded);
    const max_fields = export_shim.makeDevTFields(dev_t.max_major, dev_t.max_minor);
    const max_encoded = export_shim.encodeDeviceNumber(max_fields) orelse return error.TestUnexpectedResult;
    const invalid_fields = export_shim.makeDevTFields(dev_t.max_major + 1, 0);

    try testing.expect(dev_t.eql(fields, dev_t.init(11, 29)));
    try testing.expectEqual(dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expect(dev_t.eql(decoded, fields));
    try testing.expectEqual(dev_t.max_major, dev_t.majorFromDeviceNumber(max_encoded));
    try testing.expectEqual(dev_t.max_minor, dev_t.minorFromDeviceNumber(max_encoded));
    try testing.expect(export_shim.encodeDeviceNumber(invalid_fields) == null);
}

test "phase3 abi dev_t relay keeps kernel-tagged validation statuses explicit" {
    const valid_fields = export_shim.makeDevTFields(dev_t.max_major, dev_t.max_minor);
    const invalid_fields = export_shim.makeDevTFields(dev_t.max_major + 1, 0);
    const earlier = export_shim.makeDevTFields(1, 2);
    const later = export_shim.makeDevTFields(1, 3);
    const valid_number = export_shim.validateDeviceNumber(dev_t.max_major, dev_t.max_minor);
    const invalid_number = export_shim.validateDeviceNumber(dev_t.max_major + 1, 0);
    const valid_fields_status = export_shim.validateDeviceFields(valid_fields);
    const invalid_fields_status = export_shim.validateDeviceFields(invalid_fields);
    const valid_range = export_shim.validateDeviceRange(earlier, later);
    const invalid_range = export_shim.validateDeviceRange(later, earlier);

    try testing.expect(export_shim.statusIsOk(valid_number));
    try testing.expect(!export_shim.statusIsOk(invalid_number));
    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), valid_fields_status));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), invalid_fields_status));
    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), valid_range));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), invalid_range));

    try testing.expect(std.meta.eql(export_shim.okStatus(.kernel), valid_number));
    try testing.expect(std.meta.eql(export_shim.errorStatus(-22, .kernel), invalid_number));
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_number.flags);
}
