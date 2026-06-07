const std = @import("std");

const abi = @import("abi_bindings");

fn expectHeader(header: abi.BoundaryHeader, size: u32, version: u16, flags: u16) !void {
    try std.testing.expectEqual(size, header.size);
    try std.testing.expectEqual(version, header.abi_version);
    try std.testing.expectEqual(flags, header.flags);
}

test "phase3 abi boundary header keeps published layout constants" {
    try std.testing.expectEqual(abi.boundary_header_size, @sizeOf(abi.BoundaryHeader));
    try std.testing.expectEqual(abi.boundary_header_align, @alignOf(abi.BoundaryHeader));
    try std.testing.expectEqual(abi.boundary_header_size_offset, @offsetOf(abi.BoundaryHeader, "size"));
    try std.testing.expectEqual(
        abi.boundary_header_abi_version_offset,
        @offsetOf(abi.BoundaryHeader, "abi_version"),
    );
    try std.testing.expectEqual(abi.boundary_header_flags_offset, @offsetOf(abi.BoundaryHeader, "flags"));

    try std.testing.expectEqual(@as(usize, 8), abi.boundary_header_size);
    try std.testing.expectEqual(@as(usize, 4), abi.boundary_header_align);
    try std.testing.expectEqual(@as(usize, 0), abi.boundary_header_size_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.boundary_header_abi_version_offset);
    try std.testing.expectEqual(@as(usize, 6), abi.boundary_header_flags_offset);
}

test "phase3 abi default and compatible headers preserve caller flags" {
    const default = abi.defaultHeader(0x41);
    const expanded = abi.compatibleHeader(@as(u32, @intCast(abi.boundary_header_size + 24)), 0xA5);

    try expectHeader(default, @as(u32, @intCast(abi.boundary_header_size)), abi.ABI_VERSION, 0x41);
    try std.testing.expect(abi.headerIsCanonical(default));
    try std.testing.expect(abi.headerIsCompatible(default));
    try std.testing.expect(!abi.extendsBoundary(default));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(default));

    try expectHeader(expanded, @as(u32, @intCast(abi.boundary_header_size + 24)), abi.ABI_VERSION, 0xA5);
    try std.testing.expect(!abi.headerIsCanonical(expanded));
    try std.testing.expect(abi.headerIsCompatible(expanded));
    try std.testing.expect(abi.extendsBoundary(expanded));
    try std.testing.expectEqual(@as(u32, 24), abi.requestedExtraBytes(expanded));
}

test "phase3 abi boundary compatibility rejects stale or undersized headers" {
    const undersized = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size - 1)),
        .abi_version = abi.ABI_VERSION,
        .flags = 0,
    };
    const stale = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 16)),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x20,
    };

    try std.testing.expect(abi.headerHasCurrentAbiVersion(undersized.abi_version));
    try std.testing.expect(!abi.headerIsCanonical(undersized));
    try std.testing.expect(!abi.headerIsCompatible(undersized));
    try std.testing.expect(!abi.extendsBoundary(undersized));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(undersized));

    try std.testing.expect(!abi.headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!abi.headerIsCanonical(stale));
    try std.testing.expect(!abi.headerIsCompatible(stale));
    try std.testing.expect(!abi.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(stale));
}

test "phase3 abi boundary canonicalization normalizes size and version only" {
    const future = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 64)),
        .abi_version = abi.ABI_VERSION + 7,
        .flags = 0x5A,
    };
    const canonical = abi.canonicalizeHeader(future);

    try expectHeader(canonical, @as(u32, @intCast(abi.boundary_header_size)), abi.ABI_VERSION, future.flags);
    try std.testing.expect(abi.headerIsCanonical(canonical));
    try std.testing.expect(abi.headerIsCompatible(canonical));
    try std.testing.expect(!abi.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(canonical));
}
