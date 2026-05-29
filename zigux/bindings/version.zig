const std = @import("std");
const testing = std.testing;
const uapi = @import("uapi_version");

pub const abi_major = uapi.abi_major;
pub const abi_minor = uapi.abi_minor;
pub const header_family_revision = uapi.header_family_revision;
pub const version_size: usize = uapi.version_size;
pub const version_align: usize = uapi.version_align;
pub const abi_major_offset: usize = uapi.abi_major_offset;
pub const abi_minor_offset: usize = uapi.abi_minor_offset;
pub const header_family_revision_offset: usize = uapi.header_family_revision_offset;
pub const header_size: u32 = uapi.header_size;
pub const header_align: usize = uapi.header_align;
pub const header_size_offset: usize = uapi.header_size_offset;
pub const header_abi_version_offset: usize = uapi.header_abi_version_offset;
pub const header_flags_offset: usize = uapi.header_flags_offset;

pub const Version = uapi.Version;
pub const Header = uapi.Header;
pub const ExportStatus = @TypeOf(uapi.validate(uapi.current()));

pub fn current() Version { return uapi.current(); }
pub fn eql(left: Version, right: Version) bool {
    return left.abi_major == right.abi_major and left.abi_minor == right.abi_minor and left.header_family_revision == right.header_family_revision;
}
pub fn hasCurrentAbiMajor(value: u32) bool { return uapi.hasCurrentAbiMajor(value); }
pub fn hasCurrentAbiMinor(value: u32) bool { return uapi.hasCurrentAbiMinor(value); }
pub fn hasCurrentHeaderFamilyRevision(value: u32) bool { return uapi.hasCurrentHeaderFamilyRevision(value); }
pub fn matchesCurrent(version: Version) bool { return uapi.matchesCurrent(version); }
pub fn validate(version: Version) ExportStatus { return uapi.validate(version); }
pub fn canonicalHeader(flags: u16) Header { return uapi.canonicalHeader(flags); }
pub fn boundaryHeader(flags: u16) Header { return canonicalHeader(flags); }
pub fn compatibleHeader(size: u32, flags: u16) Header { return uapi.compatibleHeader(size, flags); }
pub fn hasCurrentAbiVersion(value: u16) bool { return uapi.hasCurrentAbiVersion(value); }
pub fn isCanonicalSize(value: u32) bool { return uapi.isCanonicalSize(value); }
pub fn isCompatibleSize(value: u32) bool { return uapi.isCompatibleSize(value); }
pub fn isCanonical(header: Header) bool { return uapi.isCanonical(header); }
pub fn isCompatible(header: Header) bool { return uapi.isCompatible(header); }
pub fn extendsBoundary(header: Header) bool { return uapi.extendsBoundary(header); }
pub fn requestedExtraBytes(header: Header) u32 { return uapi.requestedExtraBytes(header); }
pub fn canonicalizeHeader(header: Header) Header { return uapi.canonicalizeHeader(header); }
pub fn validateBoundaryHeader(header: Header) ExportStatus { return uapi.validateBoundaryHeader(header); }

test "version binding relays boundary header layout constants" {
    try testing.expectEqual(uapi.header_size, header_size);
    try testing.expectEqual(uapi.header_align, header_align);
    try testing.expectEqual(uapi.header_size_offset, header_size_offset);
    try testing.expectEqual(uapi.header_abi_version_offset, header_abi_version_offset);
    try testing.expectEqual(uapi.header_flags_offset, header_flags_offset);
    try testing.expectEqual(@as(u32, @sizeOf(Header)), header_size);
    try testing.expectEqual(@alignOf(Header), header_align);
    try testing.expectEqual(@offsetOf(Header, "size"), header_size_offset);
    try testing.expectEqual(@offsetOf(Header, "abi_version"), header_abi_version_offset);
    try testing.expectEqual(@offsetOf(Header, "flags"), header_flags_offset);
}
