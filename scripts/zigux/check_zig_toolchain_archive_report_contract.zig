const std = @import("std");
const policy = @import("toolchain_policy.zig");
const resolver = @import("toolchain_resolver.zig");

test "expected archive metadata is derived from policy target and channel" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    var filename_buffer: [160]u8 = undefined;
    const meta = try resolver.expectedArchiveMetadata(&loaded, "x86_64-linux", &filename_buffer);
    try std.testing.expect(std.mem.startsWith(u8, meta.expected_filename, "zig-x86_64-linux-"));
    try std.testing.expectEqualStrings(
        "4620f31b3889dcdcb257e6a0da6a4bc9a0b2b8e3db04219c1c160798e2cdc5a9",
        meta.expected_sha,
    );
}

test "invalid explicit archive paths are classified before missing handling" {
    const io = std.testing.io;
    const note = try resolver.describeInvalidExplicitArchivePath(io, std.testing.allocator, ".");
    defer if (note) |text| std.testing.allocator.free(text);
    try std.testing.expect(note != null);
    try std.testing.expect(std.mem.indexOf(u8, note.?, "directory") != null);
}

test "archive validation reports mismatch filename before digest drift" {
    const json = @embedFile("zig-toolchain-policy.json");
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const io = std.testing.io;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();
    const archive_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/renamed-zig.tar.xz",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(archive_path);
    try tmp.dir.writeFile(io, .{ .sub_path = "renamed-zig.tar.xz", .data = "zigux-archive" });

    const validation = try resolver.validatePolicyArchive(
        io,
        std.testing.allocator,
        &loaded,
        archive_path,
        "x86_64-linux",
        "renamed-zig.tar.xz",
    );
    defer resolver.freeArchiveValidation(std.testing.allocator, validation);
    try std.testing.expectEqualStrings("mismatch", validation.status);
    try std.testing.expect(validation.note != null);
    try std.testing.expect(std.mem.indexOf(u8, validation.note.?, "expected archive filename") != null);
}
