const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const export_shim = @import("export_shim");

fn expectStatus(
    status: export_shim.ExportStatus,
    code: i32,
    facility: export_shim.Facility,
    flags: u16,
) !void {
    try testing.expectEqual(code, status.code);
    try testing.expectEqual(@as(u16, @intFromEnum(facility)), status.facility);
    try testing.expectEqual(flags, status.flags);
    try testing.expectEqual(facility, export_shim.facilityFromInt(status.facility).?);
    try testing.expect(export_shim.facilityIsKnown(status.facility));
    try testing.expect(export_shim.statusHasKnownFacility(status));
}

test "export shim status constructors normalize sign and facility" {
    const ok_kernel = export_shim.okStatus(.kernel);
    const ok_helpers = export_shim.okStatus(.helpers);
    const positive_driver = export_shim.errorStatus(11, .drivers);
    const negative_kernel = export_shim.errorStatus(-22, .kernel);
    const negative_helpers = export_shim.errorStatus(-75, .helpers);

    try expectStatus(ok_kernel, 0, .kernel, 0);
    try expectStatus(ok_helpers, 0, .helpers, 0);
    try expectStatus(positive_driver, 11, .drivers, 0);
    try expectStatus(negative_kernel, -22, .kernel, abi.STATUS_FLAG_ERROR);
    try expectStatus(negative_helpers, -75, .helpers, abi.STATUS_FLAG_ERROR);

    try testing.expect(export_shim.statusIsOk(ok_kernel));
    try testing.expect(export_shim.statusIsOk(ok_helpers));
    try testing.expect(export_shim.statusIsOk(positive_driver));
    try testing.expect(!export_shim.statusIsOk(negative_kernel));
    try testing.expect(!export_shim.statusIsOk(negative_helpers));
}

test "export shim status recognition keeps facility separate from flags" {
    const flagged_known = export_shim.ExportStatus{
        .code = 7,
        .facility = @intFromEnum(export_shim.Facility.drivers),
        .flags = abi.STATUS_FLAG_ERROR,
    };
    const unknown_clean = export_shim.ExportStatus{
        .code = 0,
        .facility = 0xff,
        .flags = 0,
    };
    const unknown_flagged = export_shim.ExportStatus{
        .code = -1,
        .facility = 0xfe,
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try testing.expect(!export_shim.statusIsOk(flagged_known));
    try testing.expect(export_shim.statusHasKnownFacility(flagged_known));
    try testing.expectEqual(@as(?export_shim.Facility, .drivers), export_shim.facilityFromInt(flagged_known.facility));

    try testing.expect(export_shim.statusIsOk(unknown_clean));
    try testing.expect(!export_shim.statusHasKnownFacility(unknown_clean));
    try testing.expectEqual(@as(?export_shim.Facility, null), export_shim.facilityFromInt(unknown_clean.facility));

    try testing.expect(!export_shim.statusIsOk(unknown_flagged));
    try testing.expect(!export_shim.statusHasKnownFacility(unknown_flagged));
    try testing.expectEqual(@as(?export_shim.Facility, null), export_shim.facilityFromInt(unknown_flagged.facility));
}

test "export shim validators reuse the normalized invalid argument status" {
    const bad_header = export_shim.BoundaryHeader{
        .size = export_shim.header_size - 1,
        .abi_version = export_shim.abi_version,
        .flags = 0x44,
    };
    const bad_policy = export_shim.InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };
    const invalid_device = export_shim.makeDevTFields(0xffffffff, 0);

    const invalid_header_status = export_shim.validateBoundaryHeader(bad_header);
    const invalid_policy_status = export_shim.validateInteropPolicy(bad_policy);
    const invalid_device_status = export_shim.validateDeviceFields(invalid_device);

    try expectStatus(invalid_header_status, -22, .kernel, abi.STATUS_FLAG_ERROR);
    try expectStatus(invalid_policy_status, -22, .kernel, abi.STATUS_FLAG_ERROR);
    try expectStatus(invalid_device_status, -22, .kernel, abi.STATUS_FLAG_ERROR);
}
