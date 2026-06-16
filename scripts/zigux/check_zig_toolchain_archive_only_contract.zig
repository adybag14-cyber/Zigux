const std = @import("std");
const checker = @import("check_zig_toolchain.zig");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

test "archive-only path resolves policy metadata before validation" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    var filename_buffer: [160]u8 = undefined;
    const meta = try resolver.expectedArchiveMetadata(&loaded, "x86_64-linux", &filename_buffer);
    try std.testing.expect(std.mem.endsWith(u8, meta.expected_filename, ".tar.xz"));
    try std.testing.expectEqual(@as(usize, 64), meta.expected_sha.len);
}

test "archive-only options keep archive flags separate from zig probing" {
    const options = checker.ArchiveOnlyOptions{
        .explicit_archive = "third_party/missing.tar.xz",
        .explicit_target = "x86_64-linux",
        .allow_missing = true,
    };
    try std.testing.expect(options.explicit_archive != null);
    try std.testing.expect(options.explicit_target != null);
    try std.testing.expect(options.allow_missing);
}

test "archive-only missing diagnostics include search roots and allow-missing exit" {
    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);
    const diagnostic = try resolver.describeMissingArchive(
        std.testing.allocator,
        null,
        null,
        roots,
    );
    defer resolver.freeMissingArchiveDiagnostic(std.testing.allocator, diagnostic);
    try std.testing.expectEqualStrings(
        "pinned Zig archive not found in archive search roots",
        diagnostic.message,
    );
    try std.testing.expect(diagnostic.search_roots_summary != null);
}