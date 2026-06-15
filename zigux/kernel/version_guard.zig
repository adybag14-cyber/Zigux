const std = @import("std");
const version = @import("version_binding");

pub const Version = version.Version;

pub const VersionAdmissionKind = enum(u8) {
    current,
    stale_abi_major,
    stale_abi_minor,
    stale_header_family_revision,
};

pub const VersionAdmissionError = error{
    StaleAbiMajor,
    StaleAbiMinor,
    StaleHeaderFamilyRevision,
};

pub const VersionAdmission = struct {
    kind: VersionAdmissionKind,
    candidate: Version,
    expected: Version,

    pub fn isCurrent(self: VersionAdmission) bool {
        return self.kind == .current;
    }

    pub fn failure(self: VersionAdmission) ?VersionAdmissionError {
        return switch (self.kind) {
            .current => null,
            .stale_abi_major => error.StaleAbiMajor,
            .stale_abi_minor => error.StaleAbiMinor,
            .stale_header_family_revision => error.StaleHeaderFamilyRevision,
        };
    }
};

pub fn expectedVersion() Version {
    return version.current();
}

pub fn classifyVersion(candidate: Version) VersionAdmission {
    const expected = expectedVersion();
    const kind: VersionAdmissionKind = if (!version.hasCurrentAbiMajor(candidate.abi_major))
        .stale_abi_major
    else if (!version.hasCurrentAbiMinor(candidate.abi_minor))
        .stale_abi_minor
    else if (!version.hasCurrentHeaderFamilyRevision(candidate.header_family_revision))
        .stale_header_family_revision
    else
        .current;

    return .{
        .kind = kind,
        .candidate = candidate,
        .expected = expected,
    };
}

pub fn versionIsCurrent(candidate: Version) bool {
    return classifyVersion(candidate).isCurrent();
}

pub fn requireCurrentVersion(candidate: Version) VersionAdmissionError!void {
    switch (classifyVersion(candidate).kind) {
        .current => return,
        .stale_abi_major => return error.StaleAbiMajor,
        .stale_abi_minor => return error.StaleAbiMinor,
        .stale_header_family_revision => return error.StaleHeaderFamilyRevision,
    }
}

pub fn canonicalizeCurrentVersion(candidate: Version) VersionAdmissionError!Version {
    try requireCurrentVersion(candidate);
    return expectedVersion();
}

test "version guard admits the current ABI tuple" {
    const current = version.current();
    const admission = classifyVersion(current);

    try std.testing.expectEqual(VersionAdmissionKind.current, admission.kind);
    try std.testing.expect(admission.isCurrent());
    try std.testing.expectEqual(@as(?VersionAdmissionError, null), admission.failure());
    try std.testing.expect(versionIsCurrent(current));
    try requireCurrentVersion(current);
    try std.testing.expectEqual(current, try canonicalizeCurrentVersion(current));
}

test "version guard reports stale version fields in ABI order" {
    const current = version.current();
    const stale_major = Version{
        .abi_major = current.abi_major + 1,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision + 1,
    };
    const stale_minor = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision + 1,
    };
    const stale_revision = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };

    const major_admission = classifyVersion(stale_major);
    const minor_admission = classifyVersion(stale_minor);
    const revision_admission = classifyVersion(stale_revision);

    try std.testing.expectEqual(VersionAdmissionKind.stale_abi_major, major_admission.kind);
    try std.testing.expectEqual(VersionAdmissionKind.stale_abi_minor, minor_admission.kind);
    try std.testing.expectEqual(VersionAdmissionKind.stale_header_family_revision, revision_admission.kind);

    try std.testing.expectEqual(@as(?VersionAdmissionError, error.StaleAbiMajor), major_admission.failure());
    try std.testing.expectEqual(@as(?VersionAdmissionError, error.StaleAbiMinor), minor_admission.failure());
    try std.testing.expectEqual(
        @as(?VersionAdmissionError, error.StaleHeaderFamilyRevision),
        revision_admission.failure(),
    );
}

test "version guard fails closed before canonicalizing stale tuples" {
    const current = version.current();
    const stale_major = Version{
        .abi_major = current.abi_major + 1,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor + 1,
        .header_family_revision = current.header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = current.abi_major,
        .abi_minor = current.abi_minor,
        .header_family_revision = current.header_family_revision + 1,
    };

    try std.testing.expect(!versionIsCurrent(stale_major));
    try std.testing.expect(!versionIsCurrent(stale_minor));
    try std.testing.expect(!versionIsCurrent(stale_revision));

    try std.testing.expectError(error.StaleAbiMajor, requireCurrentVersion(stale_major));
    try std.testing.expectError(error.StaleAbiMinor, requireCurrentVersion(stale_minor));
    try std.testing.expectError(error.StaleHeaderFamilyRevision, requireCurrentVersion(stale_revision));

    try std.testing.expectError(error.StaleAbiMajor, canonicalizeCurrentVersion(stale_major));
    try std.testing.expectError(error.StaleAbiMinor, canonicalizeCurrentVersion(stale_minor));
    try std.testing.expectError(error.StaleHeaderFamilyRevision, canonicalizeCurrentVersion(stale_revision));
}
