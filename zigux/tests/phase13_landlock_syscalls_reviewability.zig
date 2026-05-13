const std = @import("std");
const syscalls = @import("syscalls");

const SurveySummary = struct {
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_syscalls_zig_present: bool,
    preexisting_phase13_landlock_syscalls_test_present: bool,
    preexisting_phase13_landlock_syscalls_slice_present: bool,
    preexisting_phase13_landlock_syscalls_reviewability_present: bool,
    preexisting_phase13_landlock_syscalls_survey_present: bool,
    preexisting_phase13_landlock_syscalls_manifest_present: bool,
};

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
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_missing_shared_build_surface") or
        std.mem.eql(u8, status, "blocked_on_live_fd_installation") or
        std.mem.eql(u8, status, "blocked_on_live_credential_state") or
        std.mem.eql(u8, status, "blocked_on_live_ruleset_state");
}

fn expectGap(
    manifest: Manifest,
    id: []const u8,
    status: []const u8,
    destination: []const u8,
    why_marker: []const u8,
) !void {
    for (manifest.gaps) |gap| {
        if (!std.mem.eql(u8, gap.id, id)) continue;
        try std.testing.expectEqualStrings(status, gap.status);
        try std.testing.expectEqualStrings(destination, gap.zigux_destination);
        try std.testing.expect(std.mem.indexOf(u8, gap.why_now, why_marker) != null);
        return;
    }
    return error.MissingGap;
}

test "phase13 landlock syscalls reviewability packet matches the current helper-local policy packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_landlock_syscalls_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const governance_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-governance.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(governance_note);

    const syscalls_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "security/landlock/syscalls.zig",
        std.testing.allocator,
        .limited(40 * 1024),
    );
    defer std.testing.allocator.free(syscalls_source);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("master-readback-2026-05-13", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("security/landlock/syscalls.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/tests/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("Documentation/zigux/", manifest.roadmap_destinations[2]);
    try std.testing.expect(!manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_syscalls_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_slice_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_survey_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_manifest_present);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    const descriptor = syscalls.SyscallsHelperLab.descriptor();
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_create_ruleset_planning);
    try std.testing.expect(descriptor.provides_restrict_self_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_ruleset_release_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(descriptor.validates_create_ruleset_flags);
    try std.testing.expect(descriptor.validates_create_ruleset_access_masks);
    try std.testing.expect(descriptor.validates_create_ruleset_scope);
    try std.testing.expect(descriptor.validates_ruleset_fd);
    try std.testing.expect(descriptor.validates_ruleset_write_access);
    try std.testing.expect(descriptor.validates_restrict_self_flags);
    try std.testing.expect(descriptor.validates_restrict_self_logging);
    try std.testing.expect(descriptor.validates_add_rule_flags);
    try std.testing.expect(descriptor.validates_credential_gate);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_rulesets);

    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, ".provides_create_ruleset_planning = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, ".validates_create_ruleset_flags = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "pub fn planCreateRuleset(") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "anon_inode") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, ".provides_ruleset_release_planning = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, ".provides_ruleset_fops_planning = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "pub fn planFopRulesetRelease(") != null);
    try std.testing.expect(std.mem.indexOf(u8, syscalls_source, "pub fn planRulesetFops(") != null);

    try std.testing.expect(std.mem.indexOf(u8, slice_note, "landlock_create_ruleset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "landlock_restrict_self()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "landlock_add_rule()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "fop_ruleset_release()") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "ruleset_fops") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase13_landlock_syscalls_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "phase13_build.zig") != null);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "master-readback-2026-05-13") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "planCreateRuleset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase13_landlock_syscalls_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase13_landlock_syscalls_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase13-build-gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared `phase13_build.zig` route still remains absent") != null);

    try std.testing.expect(std.mem.indexOf(u8, governance_note, "Current `master` materializes a small `security/landlock/syscalls.zig` helper starter.") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "landlock_create_ruleset()") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "phase13_landlock_syscalls_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "phase13_landlock_syscalls_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "phase13_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, governance_note, "live file-descriptor installation") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else {
            blocked_count += 1;
        }
    }

    try expectGap(
        manifest,
        "phase13-build-gate",
        "blocked_on_missing_shared_build_surface",
        "zigux/tests/phase13_build.zig",
        "missing wider replay route explicit",
    );
    try expectGap(
        manifest,
        "phase13-landlock-syscalls-helper-starter",
        "starter_landed",
        "security/landlock/syscalls.zig",
        "bounded Landlock syscalls helper lab",
    );
    try expectGap(
        manifest,
        "phase13-landlock-syscalls-direct-test-gate",
        "starter_landed",
        "zigux/tests/phase13_landlock_syscalls.zig",
        "direct syscall replay keeps the shipped create-ruleset boundary",
    );
    try expectGap(
        manifest,
        "phase13-landlock-syscalls-reviewability-gate",
        "starter_landed",
        "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
        "helper, slice, governance note, survey note, and manifest aligned",
    );
    try expectGap(
        manifest,
        "phase13-landlock-live-fd-installation",
        "blocked_on_live_fd_installation",
        "security/landlock/syscalls.zig",
        "pre-`anon_inode_getfd()` create-ruleset boundary",
    );
    try expectGap(
        manifest,
        "phase13-landlock-live-credential-state",
        "blocked_on_live_credential_state",
        "security/landlock/syscalls.zig",
        "does not mutate live credentials",
    );
    try expectGap(
        manifest,
        "phase13-landlock-live-ruleset-state",
        "blocked_on_live_ruleset_state",
        "security/landlock/syscalls.zig",
        "does not claim live ruleset ownership",
    );

    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 4), blocked_count);
}
