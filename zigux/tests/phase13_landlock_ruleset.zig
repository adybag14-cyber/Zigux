const std = @import("std");
const ruleset = @import("landlock_ruleset");

const SurveySummary = struct {
    ruleset_c_lines: usize,
    landlock_security_file_count: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_ruleset_zig_present: bool,
    preexisting_phase13_landlock_test_present: bool,
    preexisting_phase13_landlock_slice_note_present: bool,
    preexisting_phase13_landlock_survey_note_present: bool,
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
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_lsm_state");
}

test "phase13 landlock ruleset manifest records the starter and remaining gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_landlock_ruleset_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", manifest.anchor);
    try std.testing.expectEqualStrings("ad8029fc68ac23b6c9c46dcf6ae8022cc92f814e", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.ruleset_c_lines >= 700);
    try std.testing.expect(manifest.survey_summary.landlock_security_file_count >= 20);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_ruleset_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_survey_note_present);
    try std.testing.expectEqual(@as(usize, 8), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_followup = false;
    var saw_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_live_lsm_state")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-make-target")) {
            saw_make_target = true;
            try std.testing.expectEqualStrings("zigux/Makefile", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-starter")) {
            saw_starter = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_create_ruleset()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_union_access_masks()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_ruleset.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-slice-note")) {
            saw_slice_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-landlock-ruleset-slice.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-landlock-ruleset-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-layer-merge-followup")) {
            saw_followup = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "insert_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "access extension") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-live-tree-and-hierarchy-state")) {
            saw_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_lsm_state", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb-tree") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hierarchy") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 6), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_followup);
    try std.testing.expect(saw_blocker);
}

test "phase13 landlock ruleset descriptor stays anchored to ruleset.c" {
    const descriptor = ruleset.RulesetHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_ruleset_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ruleset_creation_planning);
    try std.testing.expect(descriptor.provides_union_access_masks);
    try std.testing.expect(descriptor.provides_layer_mask_init);
    try std.testing.expect(descriptor.provides_rule_unmasking);
    try std.testing.expect(!descriptor.touches_live_object_trees);
    try std.testing.expect(!descriptor.touches_live_hierarchy);
}

test "phase13 landlock ruleset creation planning rejects empty masks and keeps one layer" {
    try std.testing.expectError(error.EmptyRuleset, ruleset.RulesetHelperLab.planRulesetCreation(.{}));

    const plan = try ruleset.RulesetHelperLab.planRulesetCreation(.{
        .fs_access_mask = 0b0011,
        .net_access_mask = 0b0100,
        .scope_mask = 0b1000,
    });

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0b0011), plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0b0100), plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0b1000), plan.access_masks.scope);
}

test "phase13 landlock union access masks combines all handled bits" {
    const combined = ruleset.RulesetHelperLab.unionAccessMasks(&.{
        .{ .fs = 0b0001, .net = 0b0010, .scope = 0 },
        .{ .fs = 0b0100, .net = 0, .scope = 0b1000 },
        .{ .fs = 0b0010, .net = 0b0100, .scope = 0b0001 },
    });

    try std.testing.expectEqual(@as(u32, 0b0111), combined.fs);
    try std.testing.expectEqual(@as(u32, 0b0110), combined.net);
    try std.testing.expectEqual(@as(u32, 0b1001), combined.scope);
}

test "phase13 landlock init layer masks upgrades inode handling and keeps net exact" {
    const inode_plan = ruleset.RulesetHelperLab.initLayerMasks(&.{
        .{ .fs = 0b0011 },
        .{ .fs = 0b0100 },
    }, ruleset.initially_denied_fs_access | 0b0100, .inode);

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", inode_plan.anchor);
    try std.testing.expectEqual(ruleset.initially_denied_fs_access | 0b0100, inode_plan.handled_accesses);
    try std.testing.expectEqual(ruleset.initially_denied_fs_access, inode_plan.masks[0]);
    try std.testing.expectEqual(ruleset.initially_denied_fs_access | 0b0100, inode_plan.masks[1]);
    try std.testing.expectEqual(@as(u32, 0), inode_plan.masks[2]);

    const net_plan = ruleset.RulesetHelperLab.initLayerMasks(&.{
        .{ .net = 0b0001 },
        .{ .net = 0b0100 },
    }, 0b0101, .net_port);
    try std.testing.expectEqual(@as(u32, 0b0101), net_plan.handled_accesses);
    try std.testing.expectEqual(@as(u32, 0b0001), net_plan.masks[0]);
    try std.testing.expectEqual(@as(u32, 0b0100), net_plan.masks[1]);
    try std.testing.expectEqual(@as(u32, 0), net_plan.masks[2]);
}

test "phase13 landlock unmask layers clears per-layer requests and rejects invalid layers" {
    var masks = [_]u32{0} ** ruleset.max_num_layers;
    masks[0] = 0b0011;
    masks[1] = 0b0100;

    try std.testing.expect(!(try ruleset.RulesetHelperLab.unmaskLayers(&.{
        .{ .level = 1, .access = 0b0001 },
    }, &masks)));
    try std.testing.expectEqual(@as(u32, 0b0010), masks[0]);
    try std.testing.expectEqual(@as(u32, 0b0100), masks[1]);

    try std.testing.expect(try ruleset.RulesetHelperLab.unmaskLayers(&.{
        .{ .level = 1, .access = 0b0010 },
        .{ .level = 2, .access = 0b0100 },
    }, &masks));
    try std.testing.expectEqual(@as(u32, 0), masks[0]);
    try std.testing.expectEqual(@as(u32, 0), masks[1]);

    try std.testing.expectError(error.InvalidLayer, ruleset.RulesetHelperLab.unmaskLayers(&.{
        .{ .level = 0, .access = 0b0001 },
    }, &masks));
}
