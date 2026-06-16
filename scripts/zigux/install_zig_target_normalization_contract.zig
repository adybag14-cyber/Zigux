const std = @import("std");
const install = @import("install_zig.zig");

test "installer normalizes supported OS spellings before target resolution" {
    try std.testing.expectEqualStrings(try install.normalizeOs("Linux"), "linux");
    try std.testing.expectEqualStrings(try install.normalizeOs("Darwin"), "macos");
    try std.testing.expectEqualStrings(try install.normalizeOs("Windows"), "windows");
    try std.testing.expectError(error.UnsupportedOs, install.normalizeOs("plan9"));
}

test "installer normalizes supported CPU aliases and rejects unknown architectures" {
    try std.testing.expectEqualStrings(try install.normalizeArch("amd64"), "x86_64");
    try std.testing.expectEqualStrings(try install.normalizeArch("aarch64"), "aarch64");
    try std.testing.expectEqualStrings(try install.normalizeArch("i686"), "x86");
    try std.testing.expectError(error.UnsupportedArch, install.normalizeArch("sparc"));
}

test "target key and archive suffix are derived from normalized arch and system" {
    const allocator = std.testing.allocator;
    const environ = std.process.Environ.Map.init(std.testing.allocator);
    const release_repo = try install.canonicalReleaseRepo(allocator, environ);
    defer allocator.free(release_repo);
    const release_tag = try install.canonicalReleaseTag(allocator, environ);
    defer allocator.free(release_tag);

    var resolved = try install.resolveTarget(allocator, .{}, "0.17.0-dev.100+test", "x86_64", "windows", release_repo, release_tag);
    defer install.freeResolveTarget(allocator, &resolved);
    try std.testing.expectEqualStrings(resolved.target_key, "x86_64-windows");
    try std.testing.expect(std.mem.endsWith(u8, resolved.tarball_url, ".zip"));
}

test "CLI target overrides feed the same normalized resolution path" {
    try std.testing.expectEqualStrings(try install.normalizeOs("linux"), "linux");
    try std.testing.expectEqualStrings(try install.normalizeArch("x86_64"), "x86_64");
    var scratch = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer scratch.deinit();
    const allocator = scratch.allocator();
    var index = std.json.ObjectMap{};
    defer index.deinit(allocator);
    var master = std.json.ObjectMap{};
    try master.put(allocator, "version", .{ .string = install.canonical_release_channel });
    try index.put(allocator, "master", .{ .object = master });
    try std.testing.expectError(error.UnknownTarget, install.resolveTarget(std.testing.allocator, index, "master", "loongarch64", "linux", install.default_canonical_release_repo, install.default_canonical_release_tag));
}