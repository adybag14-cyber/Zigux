const std = @import("std");
const syscalls = @import("landlock_syscalls");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    gaps: []const Gap,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1 << 20),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock syscalls reviewability shard records the shipped direct evidence without inflating shared replay" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase13_landlock_syscalls_manifest.json");
    const survey_note = try readRepoFile(allocator, "Documentation/zigux/phase13-landlock-syscalls-survey.md");
    const release_note = try readRepoFile(allocator, "Documentation/zigux/phase13-release-notes-survey.md");
    const traceability_note = try readRepoFile(allocator, "Documentation/zigux/phase13-roadmap-traceability.md");
    const contributor_guide = try readRepoFile(allocator, "Documentation/zigux/phase13-contributor-workflow-guide.md");
    const governance_note = try readRepoFile(allocator, "Documentation/zigux/phase13-landlock-syscalls-governance.md");
    const phase13_build = try readRepoFile(allocator, "zigux/tests/phase13_build.zig");
    const phase13_release_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase13-release.py");

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-Y04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings("02f3325b2e289b7d492e022db0dbe7b61f2e22c3", manifest.surveyed_commit);

    const descriptor = syscalls.SyscallsHelperLab.descriptor();
    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);

    try expectContains(survey_note, "landed `phase13-landlock-syscalls-governance-note`");
    try expectContains(survey_note, "landed `phase13-landlock-ruleset-release-followup`");
    try expectContains(survey_note, "Do not treat this landed release planner as permission to imply anonymous inode creation, FD ownership, or live enforcement.");

    try expectContains(release_note, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(release_note, "it stays outside that seven-test replay count");
    try expectContains(traceability_note, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(traceability_note, "the bounded `fop_ruleset_release()` release-side handoff reviewable");
    try expectContains(traceability_note, "Keep this packet parked unless a future same-lane step can add another equally bounded planner");
    try expectContains(contributor_guide, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(contributor_guide, "it does not add an eighth shared replay step");
    try expectContains(governance_note, "SyscallsHelperLab.descriptor()");
    try expectContains(governance_note, "touches_live_fd_table");
    try expectContains(governance_note, "live syscall enforcement");
    try expectContains(governance_note, "Keep this packet parked unless a future lane can add another equally bounded planner");
    try expectContains(phase13_release_validator, "\"zigux/tests/phase13_landlock_syscalls_reviewability.zig\"");

    try std.testing.expect(std.mem.indexOf(u8, phase13_build, "phase13_landlock_syscalls_reviewability") == null);

    var saw_governance_note = false;
    var saw_ruleset_release_followup = false;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase13-landlock-syscalls-governance-note")) {
            saw_governance_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-landlock-syscalls-governance.md", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-release-followup")) {
            saw_ruleset_release_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "fop_ruleset_release()") != null);
        }
    }

    try std.testing.expect(saw_governance_note);
    try std.testing.expect(saw_ruleset_release_followup);
}
