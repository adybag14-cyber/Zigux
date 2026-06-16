const std = @import("std");
const install = @import("install_zig.zig");

test "explicit version channels are detected" {
    try std.testing.expect(install.isExplicitVersion("0.17.0-dev.877+a3ae499dc"));
    try std.testing.expect(!install.isExplicitVersion("master"));
}

test "explicit version index fallback returns empty map on network failure" {
    const allocator = std.testing.allocator;
    const io = std.testing.io;
    const original = install.test_hooks.read_index_fn;
    install.test_hooks.read_index_fn = struct {
        fn hook(_: std.mem.Allocator, _: std.Io) install.OpenUrlError!std.json.ObjectMap {
            return error.Network;
        }
    }.hook;
    defer install.test_hooks.read_index_fn = original;

    var index = try install.loadIndex(allocator, io, install.canonical_release_channel);
    defer index.deinit(allocator);
    try std.testing.expectEqual(@as(usize, 0), index.count());
}

test "explicit version resolves via inferred tarball when index lacks channel" {
    const allocator = std.testing.allocator;
    const environ = std.process.Environ.Map.init(std.testing.allocator);
    const release_repo = try install.canonicalReleaseRepo(allocator, environ);
    defer allocator.free(release_repo);
    const release_tag = try install.canonicalReleaseTag(allocator, environ);
    defer allocator.free(release_tag);

    var partial = std.json.ObjectMap{};
    defer partial.deinit(allocator);
    var resolved = try install.resolveTarget(allocator, partial, install.canonical_release_channel, "x86_64", "linux", release_repo, release_tag);
    defer install.freeResolveTarget(allocator, &resolved);
    try std.testing.expect(std.mem.startsWith(u8, resolved.tarball_url, "https://github.com/"));
}