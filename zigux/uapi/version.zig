const std = @import("std");
const abi = @import("abi_bindings");

pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(abi.BoundaryHeader);
pub const Header = abi.BoundaryHeader;

pub fn boundaryHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
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
    return isCurrentAbiVersion(header.abi_version) and isCompatibleSize(header.size);
}

pub fn isCanonical(header: Header) bool {
    return isCurrentAbiVersion(header.abi_version) and isCanonicalSize(header.size);
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), header_size);
    try std.testing.expect(isCurrentAbiVersion(abi.ABI_VERSION));
    try std.testing.expect(!isCurrentAbiVersion(abi.ABI_VERSION + 1));
}

test "phase3 uapi boundary header stays explicit and compatible" {
    const header = boundaryHeader(0x22);
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
    const canonical = boundaryHeader(0x33);
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));

    const future_compatible: Header = .{
        .size = header_size + 8,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x33,
    };
    try std.testing.expect(!isCanonicalSize(future_compatible.size));
    try std.testing.expect(isCompatibleSize(future_compatible.size));
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expect(isCompatible(future_compatible));
}
