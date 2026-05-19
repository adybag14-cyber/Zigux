const std = @import("std");
const abi = @import("abi_bindings");

pub const Header = abi.BoundaryHeader;

pub const abi_major: u32 = 0;
pub const abi_minor: u32 = 1;
pub const header_family_revision: u32 = 1;

pub const Version = extern struct {
    abi_major: u32,
    abi_minor: u32,
    header_family_revision: u32,
};

pub const version_size: usize = @sizeOf(Version);
pub const version_align: usize = @alignOf(Version);
pub const abi_major_offset: usize = @offsetOf(Version, "abi_major");
pub const abi_minor_offset: usize = @offsetOf(Version, "abi_minor");
pub const header_family_revision_offset: usize = @offsetOf(Version, "header_family_revision");

pub const header_size: u32 = @sizeOf(Header);
pub const abi_version: u16 = abi.ABI_VERSION;

pub const Compatibility = enum {
    canonical,
    future_compatible,
};

pub const AcceptedHeader = struct {
    compatibility: Compatibility,
    canonical: Header,

    pub fn isCanonical(self: @This()) bool {
        return self.compatibility == .canonical;
    }

    pub fn extendsBoundary(self: @This()) bool {
        return self.compatibility == .future_compatible;
    }
};

pub const HeaderEvaluation = struct {
    requested: Header,
    acceptance: ?AcceptedHeader,

    pub fn isAccepted(self: @This()) bool {
        return self.acceptance != null;
    }

    pub fn extendsBoundary(self: @This()) bool {
        const accepted = self.acceptance orelse return false;
        return accepted.extendsBoundary();
    }

    pub fn requestedExtraBytes(self: @This()) ?u32 {
        const accepted = self.acceptance orelse return null;
        return self.requested.size - accepted.canonical.size;
    }
};

pub fn versionedHeader(size: u32, version_value: u16, flags: u16) Header {
    return .{
        .size = size,
        .abi_version = version_value,
        .flags = flags,
    };
}

pub fn canonicalHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
}

pub fn boundaryHeader(flags: u16) Header {
    return canonicalHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) Header {
    return versionedHeader(size, abi_version, flags);
}

pub fn hasCurrentAbiMajor(value: u32) bool {
    return value == abi_major;
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return value == abi_minor;
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return value == header_family_revision;
}

pub fn matchesCurrent(version_value: Version) bool {
    return hasCurrentAbiMajor(version_value.abi_major) and
        hasCurrentAbiMinor(version_value.abi_minor) and
        hasCurrentHeaderFamilyRevision(version_value.header_family_revision);
}

pub fn isCurrentAbiVersion(version_value: u16) bool {
    return version_value == abi_version;
}

pub fn isCompatibleSize(size: u32) bool {
    return size >= header_size;
}

pub fn isCanonicalSize(size: u32) bool {
    return size == header_size;
}

pub fn compatibility(header: Header) ?Compatibility {
    if (!isCurrentAbiVersion(header.abi_version)) return null;
    if (isCanonicalSize(header.size)) return .canonical;
    if (isCompatibleSize(header.size)) return .future_compatible;
    return null;
}

pub fn acceptHeader(header: Header) ?AcceptedHeader {
    const kind = compatibility(header) orelse return null;
    return .{
        .compatibility = kind,
        .canonical = canonicalHeader(header.flags),
    };
}

pub fn evaluateHeader(header: Header) HeaderEvaluation {
    return .{
        .requested = header,
        .acceptance = acceptHeader(header),
    };
}

pub fn isCompatible(header: Header) bool {
    return compatibility(header) != null;
}

pub fn isCanonical(header: Header) bool {
    return compatibility(header) == .canonical;
}

pub fn extendsBoundary(header: Header) bool {
    return isCompatible(header) and !isCanonical(header);
}

pub fn requestedExtraBytes(header: Header) u32 {
    if (!extendsBoundary(header)) return 0;
    return header.size - header_size;
}

pub fn canonicalizeHeader(header: Header) ?Header {
    const accepted = acceptHeader(header) orelse return null;
    return accepted.canonical;
}

pub fn current() Version {
    return .{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision,
    };
}

pub fn eql(left: Version, right: Version) bool {
    return left.abi_major == right.abi_major and
        left.abi_minor == right.abi_minor and
        left.header_family_revision == right.header_family_revision;
}

comptime {
    std.debug.assert(version_size == 12);
    std.debug.assert(version_align == 4);
    std.debug.assert(abi_major_offset == 0);
    std.debug.assert(abi_minor_offset == 4);
    std.debug.assert(header_family_revision_offset == 8);
}

test "version helpers keep current compatibility explicit" {
    const live = current();
    const stale_major = Version{
        .abi_major = abi_major + 1,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor + 1,
        .header_family_revision = header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision + 1,
    };

    try std.testing.expect(hasCurrentAbiMajor(live.abi_major));
    try std.testing.expect(hasCurrentAbiMinor(live.abi_minor));
    try std.testing.expect(hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try std.testing.expect(matchesCurrent(live));

    try std.testing.expect(!hasCurrentAbiMajor(stale_major.abi_major));
    try std.testing.expect(!matchesCurrent(stale_major));
    try std.testing.expect(!hasCurrentAbiMinor(stale_minor.abi_minor));
    try std.testing.expect(!matchesCurrent(stale_minor));
    try std.testing.expect(!hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try std.testing.expect(!matchesCurrent(stale_revision));
}

test "version helpers preserve layout and equality semantics" {
    const left = current();
    const same = current();
    const different = Version{
        .abi_major = abi_major,
        .abi_minor = abi_minor,
        .header_family_revision = header_family_revision + 1,
    };

    try std.testing.expectEqual(@as(usize, 12), version_size);
    try std.testing.expectEqual(@as(usize, 4), version_align);
    try std.testing.expectEqual(@as(usize, 0), abi_major_offset);
    try std.testing.expectEqual(@as(usize, 4), abi_minor_offset);
    try std.testing.expectEqual(@as(usize, 8), header_family_revision_offset);

    try std.testing.expect(eql(left, same));
    try std.testing.expect(!eql(left, different));
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {
    const canonical = boundaryHeader(0x11);
    const future_compatible = compatibleHeader(header_size + 8, 0x11);
    const undersized = compatibleHeader(header_size - 1, 0x11);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x11);

    try std.testing.expect(isCanonicalSize(canonical.size));
    try std.testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));
    try std.testing.expectEqual(Compatibility.canonical, compatibility(canonical).?);
    try std.testing.expect(!extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(canonical));

    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
    try std.testing.expect(isCompatible(future_compatible));
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expectEqual(Compatibility.future_compatible, compatibility(future_compatible).?);
    try std.testing.expect(extendsBoundary(future_compatible));
    try std.testing.expectEqual(@as(u32, 8), requestedExtraBytes(future_compatible));

    try std.testing.expect(!isCompatibleSize(undersized.size));
    try std.testing.expect(compatibility(undersized) == null);
    try std.testing.expect(!isCurrentAbiVersion(mismatched_version.abi_version));
    try std.testing.expect(compatibility(mismatched_version) == null);
    try std.testing.expect(!extendsBoundary(mismatched_version));
    try std.testing.expectEqual(@as(u32, 0), requestedExtraBytes(mismatched_version));
}

test "phase3 uapi canonicalizes compatible headers without widening the boundary" {
    const future_compatible = compatibleHeader(header_size + 16, 0x44);
    const canonical = canonicalizeHeader(future_compatible).?;

    try std.testing.expectEqual(boundaryHeader(0x44), canonical);
    try std.testing.expectEqual(header_size, canonical.size);
    try std.testing.expectEqual(abi_version, canonical.abi_version);
    try std.testing.expectEqual(@as(u16, 0x44), canonical.flags);
}

test "phase3 uapi rejects incompatible headers during canonicalization" {
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x55);
    const undersized = versionedHeader(header_size - 1, abi_version, 0x55);

    try std.testing.expect(canonicalizeHeader(mismatched_version) == null);
    try std.testing.expect(canonicalizeHeader(undersized) == null);
}

test "phase3 uapi evaluation keeps requested boundary shape explicit" {
    const canonical = boundaryHeader(0x77);
    const future_compatible = compatibleHeader(header_size + 16, 0x77);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x77);

    const accepted_canonical = acceptHeader(canonical).?;
    const accepted_future = acceptHeader(future_compatible).?;
    const rejected = acceptHeader(mismatched_version);

    try std.testing.expect(accepted_canonical.isCanonical());
    try std.testing.expect(!accepted_canonical.extendsBoundary());
    try std.testing.expectEqual(canonical, accepted_canonical.canonical);
    try std.testing.expect(!accepted_future.isCanonical());
    try std.testing.expect(accepted_future.extendsBoundary());
    try std.testing.expectEqual(canonical, accepted_future.canonical);
    try std.testing.expect(rejected == null);

    const canonical_evaluation = evaluateHeader(canonical);
    const future_evaluation = evaluateHeader(future_compatible);
    const mismatch_evaluation = evaluateHeader(mismatched_version);

    try std.testing.expectEqual(canonical, canonical_evaluation.requested);
    try std.testing.expect(canonical_evaluation.isAccepted());
    try std.testing.expect(!canonical_evaluation.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 0), canonical_evaluation.requestedExtraBytes().?);
    try std.testing.expectEqual(future_compatible, future_evaluation.requested);
    try std.testing.expect(future_evaluation.isAccepted());
    try std.testing.expect(future_evaluation.extendsBoundary());
    try std.testing.expectEqual(@as(u32, 16), future_evaluation.requestedExtraBytes().?);
    try std.testing.expectEqual(mismatched_version, mismatch_evaluation.requested);
    try std.testing.expect(!mismatch_evaluation.isAccepted());
    try std.testing.expect(!mismatch_evaluation.extendsBoundary());
    try std.testing.expect(mismatch_evaluation.requestedExtraBytes() == null);
}
