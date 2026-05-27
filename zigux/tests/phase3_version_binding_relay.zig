const std = @import("std");
const version_binding = @import("version_binding");
const uapi_version = @import("uapi_version");

test "phase3 version binding keeps current compatibility relays explicit" {
    const live_binding = version_binding.current();
    const live_uapi = uapi_version.current();
    const stale = version_binding.Version{
        .abi_major = version_binding.abi_major,
        .abi_minor = version_binding.abi_minor + 1,
        .header_family_revision = version_binding.header_family_revision,
    };

    try std.testing.expect(version_binding.eql(live_binding, live_uapi));
    try std.testing.expectEqual(version_binding.abi_major, uapi_version.abi_major);
    try std.testing.expectEqual(version_binding.abi_minor, uapi_version.abi_minor);
    try std.testing.expectEqual(
        version_binding.header_family_revision,
        uapi_version.header_family_revision,
    );

    try std.testing.expect(version_binding.hasCurrentAbiMajor(live_binding.abi_major));
    try std.testing.expect(version_binding.hasCurrentAbiMinor(live_binding.abi_minor));
    try std.testing.expect(
        version_binding.hasCurrentHeaderFamilyRevision(
            live_binding.header_family_revision,
        ),
    );
    try std.testing.expect(version_binding.matchesCurrent(live_binding));
    try std.testing.expect(!version_binding.matchesCurrent(stale));
}

test "phase3 version binding keeps boundary header relays explicit" {
    const canonical = version_binding.canonicalHeader(0x21);
    const boundary = version_binding.boundaryHeader(0x21);
    const expanded = version_binding.compatibleHeader(
        version_binding.header_size + 12,
        0x21,
    );

    try std.testing.expectEqual(canonical, boundary);
    try std.testing.expectEqual(canonical, uapi_version.canonicalHeader(0x21));
    try std.testing.expectEqual(expanded, uapi_version.compatibleHeader(
        version_binding.header_size + 12,
        0x21,
    ));

    try std.testing.expect(version_binding.hasCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(version_binding.isCanonicalSize(canonical.size));
    try std.testing.expect(version_binding.isCompatibleSize(canonical.size));
    try std.testing.expect(version_binding.isCanonical(canonical));
    try std.testing.expect(version_binding.isCompatible(canonical));
    try std.testing.expect(!version_binding.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), version_binding.requestedExtraBytes(canonical));

    try std.testing.expect(!version_binding.isCanonical(expanded));
    try std.testing.expect(version_binding.isCompatible(expanded));
    try std.testing.expect(version_binding.extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 12), version_binding.requestedExtraBytes(expanded));

    try std.testing.expectEqual(
        uapi_version.canonicalizeHeader(expanded),
        version_binding.canonicalizeHeader(expanded),
    );
    try std.testing.expectEqual(
        uapi_version.validateBoundaryHeader(canonical),
        version_binding.validateBoundaryHeader(canonical),
    );
}

test "phase3 version binding keeps validation relays explicit" {
    const live = version_binding.current();
    const stale = version_binding.Version{
        .abi_major = version_binding.abi_major + 1,
        .abi_minor = version_binding.abi_minor,
        .header_family_revision = version_binding.header_family_revision,
    };

    try std.testing.expectEqual(uapi_version.validate(live), version_binding.validate(live));
    try std.testing.expectEqual(uapi_version.validate(stale), version_binding.validate(stale));
    try std.testing.expectEqual(@as(i32, 0), version_binding.validate(live).code);
    try std.testing.expectEqual(
        @as(i32, -22),
        version_binding.validate(stale).code,
    );
}
