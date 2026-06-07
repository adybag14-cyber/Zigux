const std = @import("std");
const abi = @import("abi_bindings");

test "boundary headers classify canonical, extended, undersized, and stale shapes" {
    const canonical = abi.defaultHeader(0x0015);
    const extended = abi.compatibleHeader(
        @as(u32, @intCast(abi.boundary_header_size + 32)),
        0x0015,
    );
    const undersized = abi.compatibleHeader(
        @as(u32, @intCast(abi.boundary_header_size - 1)),
        0x0015,
    );
    const stale = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 32)),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x0015,
    };

    try std.testing.expect(abi.headerIsCanonical(canonical));
    try std.testing.expect(abi.headerIsCompatible(canonical));
    try std.testing.expect(!abi.extendsBoundary(canonical));

    try std.testing.expect(!abi.headerIsCanonical(extended));
    try std.testing.expect(abi.headerIsCompatible(extended));
    try std.testing.expect(abi.extendsBoundary(extended));

    try std.testing.expect(!abi.headerIsCanonical(undersized));
    try std.testing.expect(!abi.headerIsCompatible(undersized));
    try std.testing.expect(!abi.extendsBoundary(undersized));

    try std.testing.expect(!abi.headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!abi.headerIsCompatible(stale));
    try std.testing.expect(!abi.extendsBoundary(stale));
}

test "boundary header extra-byte accounting only opens for current compatible extensions" {
    const extension_sizes = [_]u32{ 1, 4, 16, 255 };

    for (extension_sizes) |extra| {
        const header = abi.compatibleHeader(
            @as(u32, @intCast(abi.boundary_header_size)) + extra,
            0x00A5,
        );

        try std.testing.expect(abi.extendsBoundary(header));
        try std.testing.expectEqual(extra, abi.requestedExtraBytes(header));
    }

    const canonical = abi.defaultHeader(0x00A5);
    const stale_extension = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 64)),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0x00A5,
    };
    const undersized_current = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size - 1)),
        .abi_version = abi.ABI_VERSION,
        .flags = 0x00A5,
    };

    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(canonical));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(stale_extension));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(undersized_current));
}

test "boundary header canonicalization preserves flags and closes extension bytes" {
    const extended = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 128)),
        .abi_version = abi.ABI_VERSION,
        .flags = 0x0F0F,
    };

    const canonical = abi.canonicalizeHeader(extended);

    try std.testing.expectEqual(@as(u32, @intCast(abi.boundary_header_size)), canonical.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonical.abi_version);
    try std.testing.expectEqual(extended.flags, canonical.flags);
    try std.testing.expect(abi.headerIsCanonical(canonical));
    try std.testing.expect(abi.headerIsCompatible(canonical));
    try std.testing.expect(!abi.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(canonical));
}

test "boundary header flags do not change compatibility or extra-byte decisions" {
    const flags = [_]u16{ 0, 1, 0x00FF, 0x8000, 0xFFFF };

    for (flags) |flag| {
        const header = abi.compatibleHeader(
            @as(u32, @intCast(abi.boundary_header_size + 8)),
            flag,
        );
        const canonical = abi.canonicalizeHeader(header);

        try std.testing.expect(abi.headerIsCompatible(header));
        try std.testing.expect(abi.extendsBoundary(header));
        try std.testing.expectEqual(@as(u32, 8), abi.requestedExtraBytes(header));
        try std.testing.expectEqual(flag, canonical.flags);
        try std.testing.expect(abi.headerIsCanonical(canonical));
    }
}
