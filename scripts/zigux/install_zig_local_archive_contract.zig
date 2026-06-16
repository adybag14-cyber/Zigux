const std = @import("std");
const install = @import("install_zig.zig");

test "local archive staging rejects missing files" {
    const io = std.testing.io;
    const allocator = std.testing.allocator;
    try std.testing.expectError(error.LocalArchiveNotFound, install.stageArchive(io, ".zig-cache/tmp/missing-zigux-archive.tar.xz", "https://example.invalid/archive.tar.xz", ".zig-cache/tmp/staged.tar.xz", allocator));
}

test "local archive source marker is stable" {
    try std.testing.expectEqualStrings("local_archive", install.ArchiveSource.local_archive.name());
}