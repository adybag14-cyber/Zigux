const std = @import("std");
const policy = @import("toolchain_policy.zig");

test "archive search roots include repo and attached-runtime trusted archive locations" {
    const resolver = @import("toolchain_resolver.zig");
    const roots = try resolver.iterArchiveSearchRoots(std.testing.allocator, ".");
    defer resolver.freeSearchRoots(std.testing.allocator, roots);

    var has_third_party = false;
    var has_agent_files = false;
    var has_dot_toolchain = false;
    for (roots) |root| {
        if (std.mem.endsWith(u8, root, "/third_party")) has_third_party = true;
        if (std.mem.endsWith(u8, root, "/agent_files")) has_agent_files = true;
        if (std.mem.endsWith(u8, root, "/.zig-toolchain")) has_dot_toolchain = true;
    }
    try std.testing.expect(has_dot_toolchain);
    try std.testing.expect(has_third_party);
    try std.testing.expect(has_agent_files);
}

test "duplicate archive names are accepted only through the policy filename stem" {
    const expected = "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz";
    try std.testing.expect(policy.archiveNameMatchesPolicy(expected, expected));
    try std.testing.expect(policy.archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc (1).tar.xz",
        expected,
    ));
    try std.testing.expect(!policy.archiveNameMatchesPolicy(
        "zig-x86_64-linux-0.17.0-dev.877+a3ae499dc-copy.tar.xz",
        expected,
    ));
}

test "multiple visible pinned archive candidates fail closed instead of selecting one" {
    const resolver = @import("toolchain_resolver.zig");
    const json =
        \\{
        \\  "phase": "Phase 2",
        \\  "channel": "0.17.0-dev.758+selftest",
        \\  "minimum_version": "0.17.0-dev.758+selftest",
        \\  "archive_sha256": {
        \\    "x86_64-linux": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        \\  },
        \\  "upgrade_policy": {
        \\    "channel_minimum_lockstep": true,
        \\    "archive_target_scope": ["x86_64-linux"],
        \\    "required_make_routes": ["phase2-toolchain"]
        \\  }
        \\}
    ;
    var loaded = try policy.loadPolicyFromJson(std.testing.allocator, json);
    defer policy.freePolicy(std.testing.allocator, &loaded);

    const io = std.testing.io;
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const archive_name = "zig-x86_64-linux-0.17.0-dev.758+selftest.tar.xz";
    const duplicate_name = "zig-x86_64-linux-0.17.0-dev.758+selftest (1).tar.xz";
    const root_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(root_path);
    try tmp.dir.createDirPath(io, "third_party");
    try tmp.dir.writeFile(io, .{ .sub_path = "third_party/" ++ archive_name, .data = "zigux-archive" });
    try tmp.dir.writeFile(io, .{ .sub_path = "third_party/" ++ duplicate_name, .data = "zigux-archive" });

    const resolved = resolver.resolvePolicyArchive(
        io,
        std.testing.allocator,
        &loaded,
        root_path,
        null,
        null,
    );
    try std.testing.expectError(resolver.ResolverError.AmbiguousArchive, resolved);
}