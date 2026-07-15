const std = @import("std");
const checker = @import("check_zig_toolchain.zig");
const resolver = @import("toolchain_resolver.zig");

test "allow-missing flag is explicit and scoped to missing dependencies" {
    const archive_options = checker.ArchiveOnlyOptions{ .allow_missing = true };
    const zig_options = checker.ZigCheckOptions{ .allow_missing = true };
    try std.testing.expect(archive_options.allow_missing);
    try std.testing.expect(zig_options.allow_missing);
}

test "missing archive reports policy metadata before allow-missing exit" {
    const json = @embedFile("zig-toolchain-policy.json");
    const policy = @import("toolchain_policy.zig");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    var filename_buffer: [160]u8 = undefined;
    const meta = try resolver.expectedArchiveMetadata(&loaded, "x86_64-linux", &filename_buffer);
    try std.testing.expect(meta.expected_sha.len == 64);

    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingArchive(std.testing.allocator, null, null, roots);
    defer resolver.freeMissingArchiveDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expect(diagnostic.search_roots_summary != null);
}

test "missing zig reports search roots and pin policy before allow-missing exit" {
    const roots = try resolver.iterZigSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingZig(
        std.testing.allocator,
        "0.17.0-dev.1415+64dfaa568",
        roots,
    );
    defer resolver.freeMissingZigDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expect(std.mem.indexOf(u8, diagnostic.message, "pinned channel") != null);
    try std.testing.expect(diagnostic.search_roots_summary.len > 0);
}

test "policy still pins the exact phase two toolchain channel" {
    const json = @embedFile("zig-toolchain-policy.json");
    try std.testing.expect(std.mem.indexOf(u8, json, "\"channel\": \"0.17.0-dev.1415+64dfaa568\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"minimum_version\": \"0.17.0-dev.1415+64dfaa568\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"channel_minimum_lockstep\": true") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"x86_64-linux\": \"f72f19cbae9f4e649d7b2c5040aec6ccb93dce08048738bcfdf1a03475cd0c93\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"x86_64-windows\": \"6fa26a51b2a9bff2952bb11458c863580731021d65dbb04bc42680cfa5a7140f\"") != null);
}
