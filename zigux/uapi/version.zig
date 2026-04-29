const std = @import("std");
const abi = @import("abi_bindings");

pub const abi_version: u16 = abi.ABI_VERSION;
pub const Header = abi.BoundaryHeader;

pub fn boundaryHeader(flags: u16) Header {
    return abi.defaultHeader(flags);
}

pub fn isCompatible(header: Header) bool {
    return header.abi_version == abi.ABI_VERSION and header.size >= @sizeOf(abi.BoundaryHeader);
}

pub fn isCanonical(header: Header) bool {
    return header.abi_version == abi.ABI_VERSION and header.size == @sizeOf(abi.BoundaryHeader);
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi boundary header stays explicit and compatible" {
    const header = boundaryHeader(0x22);
    try std.testing.expectEqual(@as(u32, @sizeOf(abi.BoundaryHeader)), header.size);
    try std.testing.expectEqual(abi.ABI_VERSION, header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x22), header.flags);
    try std.testing.expect(isCompatible(header));

    try std.testing.expect(!isCompatible(.{
        .size = @sizeOf(abi.BoundaryHeader) - 1,
        .abi_version = abi.ABI_VERSION,
        .flags = 0,
    }));
    try std.testing.expect(!isCompatible(.{
        .size = @sizeOf(abi.BoundaryHeader),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    }));
}

test "phase3 uapi boundary header distinguishes canonical and future-compatible shapes" {
    const canonical = boundaryHeader(0x33);
    try std.testing.expect(isCanonical(canonical));
    try std.testing.expect(isCompatible(canonical));

    const future_compatible: Header = .{
        .size = @sizeOf(abi.BoundaryHeader) + 8,
        .abi_version = abi.ABI_VERSION,
        .flags = 0x33,
    };
    try std.testing.expect(!isCanonical(future_compatible));
    try std.testing.expect(isCompatible(future_compatible));
}
