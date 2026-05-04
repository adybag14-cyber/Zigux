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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock ruleset reviewability ties helper, slice, survey, and manifest together" {
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

    try std.testing.expectEqualStrings("P13-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", manifest.anchor);
    try std.testing.expectEqualStrings("8812ad875b0307da2cc0fa3588b9a24325b85e17", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.ruleset_c_lines >= 700);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_slice_note_present);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);

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

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-ruleset-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "# Phase 13 Landlock Ruleset Slice");
    try expectContains(slice_note, "`security/landlock/ruleset.zig`");
    try expectContains(slice_note, "adds one bounded `landlock_find_rule()` lookup planner");
    try expectContains(slice_note, "`root->rb_node` descent");
    try expectContains(slice_note, "match-versus-null outcomes stay reviewable as data");
    try expectContains(slice_note, "adds one bounded `merge_tree()` replay planner");
    try expectContains(slice_note, "`insert_rule()` as pure data");
    try expectContains(slice_note, "The next honest bounded step in this same lane is blocked");

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-ruleset-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "# Phase 13 Landlock Ruleset Survey");
    try expectContains(survey_note, "PHASE13_SLICE=landlock-ruleset-helper-lab");
    try expectContains(survey_note, "PHASE13_SURVEYED_COMMIT=8812ad875b0307da2cc0fa3588b9a24325b85e17");
    try expectContains(survey_note, "`zigux/tests/phase13_landlock_ruleset_reviewability.zig`");
    try expectContains(survey_note, "dedicated reviewability gate now ties the helper descriptor, manifest, and survey note together");
    try expectContains(survey_note, "landed `phase13-landlock-ruleset-reviewability-gate`");
    try expectContains(survey_note, "helper-only replacement planning");
    try expectContains(survey_note, "landed `phase13-landlock-rule-merge-tree-replay-followup`");
    try expectContains(survey_note, "one bounded `merge_tree()` replay planner");
    try expectContains(survey_note, "actual `rb_replace_node()` mutation");
}
