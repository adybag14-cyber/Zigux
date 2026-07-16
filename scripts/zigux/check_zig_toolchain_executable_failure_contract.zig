const std = @import("std");
const resolver = @import("toolchain_resolver.zig");

test "readZigVersion rejects missing executables" {
    const result = resolver.readZigVersion(std.testing.io, std.testing.allocator, "missing-zig-executable-path");
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, result);
}

test "readZigVersion rejects directory executable paths contractually" {
    const result = resolver.readZigVersion(std.testing.io, std.testing.allocator, ".");
    try std.testing.expectError(resolver.ResolverError.InvalidArgument, result);
}

test "resolver maps toolchain status names for invalid executable reporting" {
    const policy = @import("toolchain_policy.zig");
    try std.testing.expectEqualStrings("present", resolver.toolchainStatusName(.present));
    try std.testing.expectEqualStrings("too_old", resolver.toolchainStatusName(.too_old));
    try std.testing.expectEqualStrings("not_pinned", resolver.toolchainStatusName(.not_pinned));
    _ = policy.ToolchainStatus;
}
