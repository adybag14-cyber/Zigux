const std = @import("std");
const abi = @import("abi_bindings");

pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(abi.BoundaryHeader);
pub const Header = abi.BoundaryHeader;
pub const Compatibility = enum(u8) {
    canonical,
    future_compatible,
};

pub fn canonicalHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
}

pub fn boundaryHeader(flags: u16) Header {
    return canonicalHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) Header {
    return .{
        .size = size,
        .abi_version = abi_version,
        .flags = flags,
    };
}

pub fn compatibility(header: Header) ?Compatibility {
    if (!isCurrentAbiVersion(header.abi_version)) return null;
    if (!isCompatibleSize(header.size)) return null;
    return if (isCanonicalSize(header.size)) .canonical else .future_compatible;
}

pub fn canonicalizeHeader(header: Header) ?Header {
    if (compatibility(header) == null) return null;
    return canonicalHeader(header.flags);
}

pub fn isCurrentAbiVersion(version: u16) bool {
    return version == abi_version;
}

pub fn isCompatibleSize(size: u32) bool {
    return size >= header_size;
}

pub fn isCanonicalSize(size: u32) bool {
    return size == header_size;
}

pub fn isCompatible(header: Header) bool {
    return compatibility(header) != null;
}

pub fn isCanonical(header: Header) bool {
    return compatibility(header) == .canonical;
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), header_size);
    try std.testing.expect(isCurrentAbiVersion(abi.ABI_VERSION));
    try std.testing.expect(!isCurrentAbiVersion(abi.ABI_VERSION + 1));
}

test "phase3 uapi boundary header stays explicit and compatible" {
    const header = canonicalHeader(0x22);
    try std.testing.expectEqual(header, boundaryHeader(0x22));
    try std.testing.expectEqual(header_size, header.size);
    try std.testing.expectEqual(abi.ABI_VERSION, header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x22), header.flags);
    try std.testing.expect(isCompatible(header));
    try std.testing.expect(isCompatibleSize(header.size));
    try std.testing.expect(isCanonicalSize(header.size));

    try std.testing.expect(!isCompatible(.{
        .size = header_size - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0,
    }));
    try std.testing.expect(!isCompatibleSize(header_size - 1));
    try std.testing.expect(!isCompatible(.{
        .size = header_size,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    }));
}

test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {
    const canonical = canonicalHeader(0x33);
    try std.testing.expectEqual(canonical, boundaryHeader(0x33));
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));

    const future_compatible = compatibleHeader(header_size + 8, 0x33);
    try std.testing.expectEqual(abi.ABI_VERSION, future_compatible.abi_version);
    try std.testing.expectEqual(@as(u16, 0x33), future_compatible.flags);
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expect(isCompatible(future_compatible));
}

test "phase3 uapi compatibility helper keeps header shape explicit" {
    const canonical = canonicalHeader(0x44);
    try std.testing.expectEqual(Compatibility.canonical, compatibility(canonical).?);

    const future_compatible = compatibleHeader(header_size + 8, 0x44);
    try std.testing.expectEqual(Compatibility.future_compatible, compatibility(future_compatible).?);

    const undersized = compatibleHeader(header_size - 1, 0x44);
    try std.testing.expect(compatibility(undersized) == null);

    const incompatible_version: Header = .{
        .size = header_size,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x44,
    };
    try std.testing.expect(compatibility(incompatible_version) == null);
}

test "phase3 uapi compatible header helper keeps explicit future-size replay reviewable" {
    const undersized = compatibleHeader(header_size - 1, 0x55);
    try std.testing.expectEqual(@as(u16, 0x55), undersized.flags);
    try std.testing.expectEqual(abi.ABI_VERSION, undersized.abi_version);
    try std.testing.expect(!isCompatible(undersized));
    try std.testing.expect(!isCanonical(undersized));
}

test "phase3 uapi canonicalizes compatible headers without widening the boundary" {
    const canonical = canonicalHeader(0x66);
    try std.testing.expectEqual(canonical, canonicalizeHeader(canonical).?);

    const future_compatible = compatibleHeader(header_size + 16, 0x66);
    try std.testing.expectEqual(canonical, canonicalizeHeader(future_compatible).?);

    const incompatible_version: Header = .{
        .size = header_size,
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x66,
    };
    try std.testing.expect(canonicalizeHeader(incompatible_version) == null);
}
