const std = @import("std");
const install = @import("install_zig.zig");

test "resolve target exposes channel metadata" {
    const allocator = std.testing.allocator;
    const environ = std.process.Environ.Map.init(allocator);
    const release_repo = try install.canonicalReleaseRepo(allocator, environ);
    defer allocator.free(release_repo);
    const release_tag = try install.canonicalReleaseTag(allocator, environ);
    defer allocator.free(release_tag);

    var resolved = try install.resolveTarget(allocator, .{}, install.canonical_release_channel, "x86_64", "linux", release_repo, release_tag);
    defer install.freeResolveTarget(allocator, &resolved);
    try std.testing.expectEqualStrings(resolved.target_key, "x86_64-linux");
    try std.testing.expect(std.mem.startsWith(u8, resolved.tarball_url, "https://github.com/"));
}