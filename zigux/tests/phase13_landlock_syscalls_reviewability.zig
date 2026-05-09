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

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings("599ee1519c5464bb86a0ffdcab52dfe958c40571", manifest.surveyed_commit);

    const descriptor = syscalls.SyscallsHelperLab.descriptor();
    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);

    try expectContains(survey_note, "landed `phase13-landlock-syscalls-governance-note`");
    try expectContains(survey_note, "landed `phase13-landlock-ruleset-release-followup`");
    try expectContains(survey_note, "landed `phase13-landlock-ruleset-fops-followup`");
    try expectContains(survey_note, "the new in-memory `ruleset_fops` planner");
    try expectContains(survey_note, "Keep this packet parked unless a future same-lane step can add another equally bounded planner");

    try expectContains(release_note, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(release_note, "it stays outside that eight-test replay count");
    try expectContains(release_note, "does not quietly grow a ninth shared step");

    try expectContains(traceability_note, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(traceability_note, "the bounded `fop_ruleset_release()` release-side handoff reviewable");
    try expectContains(traceability_note, "Keep this packet parked unless a future same-lane step can add another equally bounded planner");

    try expectContains(contributor_guide, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(contributor_guide, "it does not add a ninth shared replay step");

    try expectContains(governance_note, "`SyscallsHelperLab.descriptor()`");
    try expectContains(governance_note, "`touches_live_fd_table`");
    try expectContains(governance_note, "`ruleset_fops` planning");
    try expectContains(governance_note, "live syscall enforcement");
    try expectContains(governance_note, "Keep this packet parked unless a future lane can add another equally bounded planner");
    try expectContains(governance_note, "`zigux/tests/phase13_landlock_syscalls_manifest.json`");
    try expectContains(governance_note, "source of truth for packet metadata");
    try expectContains(governance_note, "`zigux/tests/phase13_build.zig`");
    try expectContains(governance_note, "adjacent Phase 13 replay infrastructure");
    try expectContains(governance_note, "does not own that shared build surface");
    try expectContains(governance_note, "update the survey note and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` in the same patch");

    try std.testing.expect(std.mem.indexOf(u8, phase13_build, "phase13_landlock_syscalls_reviewability") == null);

    var saw_governance_note = false;
    var saw_ruleset_release_followup = false;
    var saw_ruleset_fops_followup = false;
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
        } else if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-fops-followup")) {
            saw_ruleset_fops_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/syscalls.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "FMODE_CAN_READ") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "FMODE_CAN_WRITE") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "-EINVAL") != null);
        }
    }

    try std.testing.expect(saw_governance_note);
    try std.testing.expect(saw_ruleset_release_followup);
    try std.testing.expect(saw_ruleset_fops_followup);
}

test "phase13 landlock syscalls reviewability shard keeps ruleset fops behavior explicit" {
    const release_plan = try syscalls.SyscallsHelperLab.planRulesetRelease(.{});
    const release_fops = syscalls.SyscallsHelperLab.planRulesetFops(.release);
    try std.testing.expectEqualStrings(release_plan.anchor, release_fops.anchor);
    try std.testing.expectEqual(release_plan.requires_private_data_ruleset, release_fops.requires_private_data_ruleset);
    try std.testing.expectEqual(release_plan.releases_retained_ruleset_reference, release_fops.releases_retained_ruleset_reference);
    try std.testing.expectEqual(release_plan.returns_zero, release_fops.returns_zero);
    try std.testing.expect(!release_fops.returns_einval);
    try std.testing.expectEqual(@as(u32, 0), release_fops.enables_mode);

    const read_fops = syscalls.SyscallsHelperLab.planRulesetFops(.read);
    try std.testing.expectEqual(syscalls.RulesetFopsOperation.read, read_fops.operation);
    try std.testing.expectEqual(syscalls.fmode_can_read, read_fops.enables_mode);
    try std.testing.expect(read_fops.returns_einval);
    try std.testing.expect(!read_fops.returns_zero);
    try std.testing.expect(!read_fops.requires_private_data_ruleset);

    const write_fops = syscalls.SyscallsHelperLab.planRulesetFops(.write);
    try std.testing.expectEqual(syscalls.RulesetFopsOperation.write, write_fops.operation);
    try std.testing.expectEqual(syscalls.fmode_can_write, write_fops.enables_mode);
    try std.testing.expect(write_fops.returns_einval);
    try std.testing.expect(!write_fops.returns_zero);
    try std.testing.expect(!write_fops.requires_private_data_ruleset);
}
