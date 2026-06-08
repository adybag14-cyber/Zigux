const std = @import("std");
const abi = @import("abi_bindings");

test "boundary header default constructor pins canonical layout bytes" {
    const header = abi.defaultHeader(0x2A5A);

    try std.testing.expectEqual(@as(u32, @intCast(abi.boundary_header_size)), header.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try std.testing.expectEqual(@as(u16, 0x2A5A), header.flags);

    try std.testing.expect(abi.headerHasCurrentAbiVersion(header.abi_version));
    try std.testing.expect(abi.headerIsCanonical(header));
    try std.testing.expect(abi.headerIsCompatible(header));
    try std.testing.expect(!abi.extendsBoundary(header));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(header));
}

test "boundary header compatibility accepts only current abi and minimum size" {
    const too_small = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size - 1)),
        .abi_version = abi.ABI_VERSION,
        .flags = 0,
    };
    const stale = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 16)),
        .abi_version = abi.ABI_VERSION + 1,
        .flags = 0,
    };
    const compatible = abi.compatibleHeader(
        @as(u32, @intCast(abi.boundary_header_size + 24)),
        0x11,
    );

    try std.testing.expect(!abi.headerIsCanonical(too_small));
    try std.testing.expect(!abi.headerIsCompatible(too_small));
    try std.testing.expect(!abi.extendsBoundary(too_small));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(too_small));

    try std.testing.expect(!abi.headerHasCurrentAbiVersion(stale.abi_version));
    try std.testing.expect(!abi.headerIsCompatible(stale));
    try std.testing.expect(!abi.extendsBoundary(stale));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(stale));

    try std.testing.expect(!abi.headerIsCanonical(compatible));
    try std.testing.expect(abi.headerIsCompatible(compatible));
    try std.testing.expect(abi.extendsBoundary(compatible));
    try std.testing.expectEqual(@as(u32, 24), abi.requestedExtraBytes(compatible));
}

test "boundary header canonicalization preserves caller flags" {
    const expanded = abi.BoundaryHeader{
        .size = @as(u32, @intCast(abi.boundary_header_size + 64)),
        .abi_version = abi.ABI_VERSION,
        .flags = 0xBEEF,
    };

    const canonical = abi.canonicalizeHeader(expanded);

    try std.testing.expectEqual(@as(u32, @intCast(abi.boundary_header_size)), canonical.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonical.abi_version);
    try std.testing.expectEqual(expanded.flags, canonical.flags);
    try std.testing.expect(abi.headerIsCanonical(canonical));
    try std.testing.expect(abi.headerIsCompatible(canonical));
    try std.testing.expect(!abi.extendsBoundary(canonical));
    try std.testing.expectEqual(@as(u32, 0), abi.requestedExtraBytes(canonical));
}

test "boundary header canonicalization repairs stale version and undersized request" {
    const invalid = abi.BoundaryHeader{
        .size = 1,
        .abi_version = abi.ABI_VERSION + 9,
        .flags = 0x77,
    };

    try std.testing.expect(!abi.headerIsCompatible(invalid));

    const canonical = abi.canonicalizeHeader(invalid);

    try std.testing.expectEqual(@as(u32, @intCast(abi.boundary_header_size)), canonical.size);
    try std.testing.expectEqual(@as(u16, abi.ABI_VERSION), canonical.abi_version);
    try std.testing.expectEqual(invalid.flags, canonical.flags);
    try std.testing.expect(abi.headerIsCanonical(canonical));
    try std.testing.expect(abi.headerIsCompatible(canonical));
}
