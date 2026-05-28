const std = @import("std");

const ReminderEntry = struct {
    path: []const u8,
    role: []const u8,
};

const reminder_packet = [_]ReminderEntry{
    .{ .path = "Documentation/zigux/phase1-closure.md", .role = "closure note" },
    .{ .path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .role = "lane sequencing note" },
    .{ .path = "Documentation/zigux/README.md", .role = "docs-root reminder" },
    .{ .path = "Documentation/zigux/review-checklist.md", .role = "review checklist reminder" },
    .{ .path = "scripts/zigux/README.md", .role = "scripts-root reminder" },
    .{ .path = "scripts/zigux/check-phase1-string-review-packet.py", .role = "string review guard" },
    .{ .path = "scripts/zigux/check-phase1-direct-owner-markers.py", .role = "direct owner guard" },
    .{ .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py", .role = "direct anchor manifest gate" },
    .{ .path = "scripts/zigux/check-phase1-bench.py", .role = "bench guard" },
    .{ .path = "scripts/zigux/check-phase1-shared-reminder-packet.py", .role = "shared reminder guard" },
    .{ .path = "scripts/zigux/validate-phase1-closure.py", .role = "closure validator" },
    .{ .path = "zigux/tests/README.md", .role = "tests-root reminder" },
    .{ .path = "zigux/tests/build.zig", .role = "tests build route" },
    .{ .path = "zigux/tests/phase1_helpers.zig", .role = "shared helper replay" },
    .{ .path = "zigux/tests/phase1_helpers_build.zig", .role = "focused helper replay build route" },
    .{ .path = "zigux/tests/phase1_host_tools_smoke.zig", .role = "host tools smoke route" },
    .{ .path = ".github/workflows/zigux-bootstrap.yml", .role = "bootstrap workflow" },
    .{ .path = "zigux/tests/fixtures/phase1_helper_manifest.json", .role = "helper manifest" },
};

const expected_packet_csv =
    "Documentation/zigux/phase1-closure.md," ++
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md," ++
    "Documentation/zigux/README.md," ++
    "Documentation/zigux/review-checklist.md," ++
    "scripts/zigux/README.md," ++
    "scripts/zigux/check-phase1-string-review-packet.py," ++
    "scripts/zigux/check-phase1-direct-owner-markers.py," ++
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py," ++
    "scripts/zigux/check-phase1-bench.py," ++
    "scripts/zigux/check-phase1-shared-reminder-packet.py," ++
    "scripts/zigux/validate-phase1-closure.py," ++
    "zigux/tests/README.md," ++
    "zigux/tests/build.zig," ++
    "zigux/tests/phase1_helpers.zig," ++
    "zigux/tests/phase1_helpers_build.zig," ++
    "zigux/tests/phase1_host_tools_smoke.zig," ++
    ".github/workflows/zigux-bootstrap.yml," ++
    "zigux/tests/fixtures/phase1_helper_manifest.json";

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

test "phase 1 current reminder packet keeps the ordered closure roster" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);
    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    try std.testing.expectEqual(@as(usize, 18), reminder_packet.len);
    try std.testing.expectEqualStrings("Documentation/zigux/phase1-closure.md", reminder_packet[0].path);
    try std.testing.expectEqualStrings("zigux/tests/fixtures/phase1_helper_manifest.json", reminder_packet[reminder_packet.len - 1].path);

    for (reminder_packet) |entry| {
        const contents = try readRepoFile(std.testing.allocator, root, entry.path);
        defer std.testing.allocator.free(contents);
        try std.testing.expect(contents.len > 0);
    }

    const expected_marker = "`PHASE1_CURRENT_REMINDER_PACKET=" ++ expected_packet_csv ++ "`";
    try std.testing.expect(contains(closure_note, expected_marker));
}

test "phase 1 current reminder packet keeps every path visible in the note" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);
    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    for (reminder_packet) |entry| {
        var bullet: [160]u8 = undefined;
        const bullet_text = try std.fmt.bufPrint(&bullet, "- `{s}`", .{entry.path});
        try std.testing.expect(contains(closure_note, bullet_text));

        try std.testing.expect(entry.role.len > 0);
        try std.testing.expect(contains(expected_packet_csv, entry.path));
    }
}

test "phase 1 closure status stays parked on the helper manifest tranche" {
    var root = try openRepoRoot();
    defer root.close(std.testing.io);
    const closure_note = try readRepoFile(std.testing.allocator, root, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    try std.testing.expect(contains(closure_note, "`PHASE1_STATUS=parked`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`"));
    try std.testing.expect(contains(closure_note, "`PHASE1_HELPER_COUNT=13`"));
    try std.testing.expect(contains(closure_note, "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`"));
}
