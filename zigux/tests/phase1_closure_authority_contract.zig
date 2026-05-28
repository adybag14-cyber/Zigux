const std = @import("std");

const AuthoritySource = struct {
    path: []const u8,
    role: []const u8,
};

const authority_sources = [_]AuthoritySource{
    .{ .path = "Documentation/zigux/phase1-closure.md", .role = "closure note" },
    .{ .path = "zigux/tests/fixtures/phase1_helper_manifest.json", .role = "committed helper manifest" },
    .{ .path = "scripts/zigux/validate-phase1-closure.py", .role = "narrow closure validator" },
    .{ .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py", .role = "direct-anchor manifest gate" },
    .{ .path = "scripts/zigux/check-phase1-bench.py", .role = "bench checker" },
    .{ .path = "scripts/zigux/check-phase1-shared-reminder-packet.py", .role = "shared reminder checker" },
    .{ .path = "scripts/zigux/check-phase1-direct-owner-markers.py", .role = "owner-map reminders" },
    .{ .path = "zigux/tests/phase1_host_tools_smoke.zig", .role = "shared tests-root smoke route" },
};

const adjacent_guards = [_][]const u8{
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "zigux/tests/build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn openRepoRoot() !std.Io.Dir {
    const candidates = [_][]const u8{ ".", "..", "../.." };
    for (candidates) |candidate| {
        var dir = std.Io.Dir.cwd().openDir(std.testing.io, candidate, .{}) catch continue;
        if (dir.access(std.testing.io, "Documentation/zigux/phase1-closure.md", .{})) |_| {
            return dir;
        } else |_| {
            dir.close(std.testing.io);
        }
    }
    return error.RepositoryRootNotFound;
}

fn readRepoFile(allocator: std.mem.Allocator, root: std.Io.Dir, path: []const u8) ![]u8 {
    return root.readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

test "phase 1 closure authority keeps the current source roster materialized" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);

    try std.testing.expectEqual(@as(usize, 8), authority_sources.len);
    try std.testing.expectEqualStrings("Documentation/zigux/phase1-closure.md", authority_sources[0].path);
    try std.testing.expectEqualStrings("zigux/tests/phase1_host_tools_smoke.zig", authority_sources[authority_sources.len - 1].path);

    for (authority_sources) |source| {
        const contents = try readRepoFile(std.testing.allocator, root, source.path);
        defer std.testing.allocator.free(contents);
        try std.testing.expect(contents.len > 0);
        try std.testing.expect(source.role.len > 0);
    }
}

test "phase 1 closure note names every current authority source" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);
    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    try std.testing.expect(contains(closure_note, "current authority: the committed helper manifest, this closure note, the narrow closure validator"));

    for (authority_sources) |source| {
        try std.testing.expect(contains(closure_note, source.path));
    }
}

test "phase 1 closure authority keeps adjacent guards separate" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);
    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    try std.testing.expect(contains(closure_note, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"));

    for (adjacent_guards) |guard| {
        try std.testing.expect(contains(closure_note, guard));
    }
}
