const std = @import("std");
const abi = @import("abi_bindings");

pub const Header = abi.BoundaryHeader;
pub const Compatibility = enum(u32) {
    canonical = 1,
    future_compatible = 2,
};
pub const AcceptedHeader = struct {
    compatibility: Compatibility,
    canonical: Header,
};
pub const HeaderEvaluation = struct {
    requested: Header,
    acceptance: ?AcceptedHeader,

    pub fn isAccepted(self: @This()) bool {
        return self.acceptance != null;
    }

    pub fn compatibility(self: @This()) ?Compatibility {
        return if (self.acceptance) |accepted| accepted.compatibility else null;
    }

    pub fn canonical(self: @This()) ?Header {
        return if (self.acceptance) |accepted| accepted.canonical else null;
    }

    pub fn sizeDelta(self: @This()) i64 {
        return @as(i64, self.requested.size) - @as(i64, header_size);
    }
};

pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = @sizeOf(Header);

pub fn versionedHeader(size: u32, version: u16, flags: u16) Header {
    return .{
        .size = size,
        .abi_version = version,
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

pub fn isCurrentAbiVersion(version: u16) bool {
    return version == abi_version;
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

pub fn compatibilityTag(header: Header) u32 {
    return if (compatibility(header)) |mode| @intFromEnum(mode) else 0;
}

pub fn isCompatible(header: Header) bool {
    return compatibility(header) != null;
}

pub fn isCanonical(header: Header) bool {
    return compatibility(header) == .canonical;
}

pub fn acceptHeader(header: Header) ?AcceptedHeader {
    const mode = compatibility(header) orelse return null;
    return .{
        .compatibility = mode,
        .canonical = canonicalHeader(header.flags),
    };
}

pub fn canonicalizeHeader(header: Header) ?Header {
    return (acceptHeader(header) orelse return null).canonical;
}

pub fn evaluateHeader(header: Header) HeaderEvaluation {
    return .{
        .requested = header,
        .acceptance = acceptHeader(header),
    };
}

test "phase3 uapi version follows abi version" {
    try std.testing.expectEqual(abi.ABI_VERSION, abi_version);
}

test "phase3 uapi exports explicit compatibility tags for the starter boundary" {
    const canonical = boundaryHeader(0x11);
    const future_compatible = compatibleHeader(header_size + 8, 0x11);
    const mismatched_version = versionedHeader(header_size, abi_version + 1, 0x11);

    try std.testing.expectEqual(@as(u32, 1), @intFromEnum(Compatibility.canonical));
    try std.testing.expectEqual(@as(u32, 2), @intFromEnum(Compatibility.future_compatible));
    try std.testing.expectEqual(@as(u32, 1), compatibilityTag(canonical));
    try std.testing.expectEqual(@as(u32, 2), compatibilityTag(future_compatible));
    try std.testing.expectEqual(@as(u32, 0), compatibilityTag(mismatched_version));
}
