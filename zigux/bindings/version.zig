const std = @import("std");
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
pub fn boundaryHeader(flags: u16) Header { return uapi.boundaryHeader(flags); }
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
