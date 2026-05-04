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

const expected_surveyed_commit = "8812ad875b0307da2cc0fa3588b9a24325b85e17";
const expected_slice_marker = "PHASE13_SLICE=landlock-ruleset-helper-lab";

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_live_lsm_state");
}

test "phase13 landlock ruleset manifest records the shipped helper lab and remaining blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_landlock_ruleset_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-ruleset-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", manifest.anchor);
    try std.testing.expectEqualStrings(expected_surveyed_commit, manifest.surveyed_commit);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_surveyed_commit) != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE13_SURVEYED_COMMIT=") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, expected_slice_marker) != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.ruleset_c_lines >= 700);
    try std.testing.expectEqual(@as(usize, 32), manifest.survey_summary.landlock_security_file_count);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_ruleset_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_survey_note_present);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_reviewability_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_merge_followup = false;
    var saw_search_followup = false;
    var saw_tree_link_followup = false;
    var saw_lookup_followup = false;
    var saw_materialization_followup = false;
    var saw_replacement_followup = false;
    var saw_release_followup = false;
    var saw_merge_tree_replay_followup = false;
    var saw_live_state_blocker = false;

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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_init_layer_masks()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_unmask_layers()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "build_check_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "build_check_layer()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "build_check_ruleset()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_ruleset.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_ruleset_reviewability.zig", gap.zigux_destination);
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
            saw_merge_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "insert_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "merged-layer intersection") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-tree-search-followup")) {
            saw_search_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "get_root()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "walker_node") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-tree-link-followup")) {
            saw_tree_link_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_link_node()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_insert_color()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-lookup-followup")) {
            saw_lookup_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_find_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "root->rb_node") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-materialization-followup")) {
            saw_materialization_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "create_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RB_CLEAR_NODE()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-replacement-followup")) {
            saw_replacement_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_replace_node()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "previous-rule release") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-release-followup")) {
            saw_release_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "free_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "might_sleep()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landlock_put_object()") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-merge-tree-replay-followup")) {
            saw_merge_tree_replay_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "merge_tree()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "insert_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "destination access-mask upgrades") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-live-tree-state-blocker")) {
            saw_live_state_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_lsm_state", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "actual rb-tree mutation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "workqueue-backed teardown") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 15), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_merge_followup);
    try std.testing.expect(saw_search_followup);
    try std.testing.expect(saw_tree_link_followup);
    try std.testing.expect(saw_lookup_followup);
    try std.testing.expect(saw_materialization_followup);
    try std.testing.expect(saw_replacement_followup);
    try std.testing.expect(saw_release_followup);
    try std.testing.expect(saw_merge_tree_replay_followup);
    try std.testing.expect(saw_live_state_blocker);
}

test "phase13 landlock ruleset descriptor stays anchored to ruleset.c" {
    const descriptor = ruleset.RulesetHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_ruleset_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ruleset_creation_planning);
    try std.testing.expect(descriptor.provides_union_access_masks);
    try std.testing.expect(descriptor.provides_layer_mask_init);
    try std.testing.expect(descriptor.provides_rule_unmasking);
    try std.testing.expect(descriptor.provides_rule_insertion_planning);
    try std.testing.expect(descriptor.provides_rule_tree_search_planning);
    try std.testing.expect(descriptor.provides_rule_tree_link_planning);
    try std.testing.expect(descriptor.provides_rule_lookup_planning);
    try std.testing.expect(descriptor.provides_rule_materialization_planning);
    try std.testing.expect(descriptor.provides_rule_replacement_planning);
    try std.testing.expect(descriptor.provides_rule_release_planning);
    try std.testing.expect(descriptor.provides_rule_merge_tree_replay_planning);
    try std.testing.expect(!descriptor.touches_live_object_trees);
    try std.testing.expect(!descriptor.touches_live_hierarchy);
}
