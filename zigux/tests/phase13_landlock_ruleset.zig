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
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

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

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
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
    try std.testing.expect(!descriptor.touches_live_object_trees);
    try std.testing.expect(!descriptor.touches_live_hierarchy);
}

test "phase13 landlock ruleset creation and access-mask helpers stay bounded" {
    try std.testing.expectError(error.EmptyRuleset, ruleset.RulesetHelperLab.planRulesetCreation(.{}));

    const creation = try ruleset.RulesetHelperLab.planRulesetCreation(.{
        .fs_access_mask = 0x1,
        .net_access_mask = 0x2,
        .scope_mask = 0x4,
    });
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", creation.anchor);
    try std.testing.expectEqual(@as(u32, 1), creation.num_layers);
    try std.testing.expectEqual(@as(u32, 0x1), creation.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x2), creation.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x4), creation.access_masks.scope);

    const combined = ruleset.RulesetHelperLab.unionAccessMasks(&[_]ruleset.AccessMasks{
        .{ .fs = 0x1, .net = 0x2, .scope = 0x4 },
        .{ .fs = 0x8, .net = 0x10, .scope = 0x20 },
    });
    try std.testing.expectEqual(@as(u32, 0x9), combined.fs);
    try std.testing.expectEqual(@as(u32, 0x12), combined.net);
    try std.testing.expectEqual(@as(u32, 0x24), combined.scope);

    const mask_plan = ruleset.RulesetHelperLab.initLayerMasks(&[_]ruleset.AccessMasks{
        .{ .fs = 0x03 },
        .{ .fs = 0x30 },
    }, 0x33, .inode);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", mask_plan.anchor);
    try std.testing.expectEqual(@as(u32, 0x33), mask_plan.handled_accesses);
    try std.testing.expectEqual(@as(u32, 0x03), mask_plan.masks[0]);
    try std.testing.expectEqual(@as(u32, 0x30), mask_plan.masks[1]);
}

test "phase13 landlock ruleset capacity invariants stay reviewable" {
    const invariants = ruleset.RulesetHelperLab.planCapacityInvariants();

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", invariants.anchor);
    try std.testing.expect(invariants.rule_num_layers_fits_max_layers);
    try std.testing.expect(invariants.creation_num_layers_fits_max_layers);
    try std.testing.expect(invariants.layer_level_fits_max_layers);
    try std.testing.expect(invariants.layer_access_carries_initially_denied_fs_access);
    try std.testing.expect(invariants.ruleset_num_rules_reaches_max);
    try std.testing.expect(invariants.rule_storage_slots_match_max_layers);
}

test "phase13 landlock ruleset layer unmasking and insertion stay pure" {
    var masks = [_]u32{ 0x3, 0x4 } ++ ([_]u32{0} ** (ruleset.max_num_layers - 2));
    const cleared = try ruleset.RulesetHelperLab.unmaskLayers(&[_]ruleset.Layer{
        .{ .level = 1, .access = 0x3 },
        .{ .level = 2, .access = 0x4 },
    }, &masks);
    try std.testing.expect(cleared);

    const inserted = try ruleset.RulesetHelperLab.planRuleInsertion(null, &[_]ruleset.Layer{
        .{ .level = 1, .access = 0x1 },
    }, 4);
    try std.testing.expectEqual(ruleset.RuleInsertionMode.insert_new_rule, inserted.mode);
    try std.testing.expectEqual(@as(u32, 5), inserted.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 1), inserted.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 1), inserted.resulting_rule.layers[0].level);

    const matched_rule = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{.{ .level = 0, .access = 0x1 }} ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };
    const extended = try ruleset.RulesetHelperLab.planRuleInsertion(matched_rule, &[_]ruleset.Layer{
        .{ .level = 0, .access = 0x2 },
    }, 7);
    try std.testing.expectEqual(ruleset.RuleInsertionMode.extend_existing_access, extended.mode);
    try std.testing.expectEqual(@as(u32, 7), extended.resulting_num_rules);
    try std.testing.expectEqual(@as(u32, 0x3), extended.resulting_rule.layers[0].access);
}

test "phase13 landlock ruleset tree search and link planners stay data-only" {
    const search = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 20, &[_]u64{10}, 2);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", search.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.inode, search.root);
    try std.testing.expectEqual(@as(usize, 1), search.search_depth);
    try std.testing.expect(!search.matched_existing_rule);
    try std.testing.expectEqual(@as(?u64, 10), search.parent_key_data);
    try std.testing.expectEqual(ruleset.InsertionSite.right, search.insertion_site.?);
    try std.testing.expectEqual(@as(u32, 3), search.resulting_num_rules);

    const link = try ruleset.RulesetHelperLab.planRuleTreeLink(search);
    try std.testing.expectEqual(ruleset.TreeLinkMode.attach_right, link.mode);
    try std.testing.expect(link.performs_rb_link_node);
    try std.testing.expect(link.performs_rb_insert_color);
    try std.testing.expectEqual(@as(u32, 3), link.resulting_num_rules);
}

test "phase13 landlock ruleset lookup planner stays read-only" {
    const empty = try ruleset.RulesetHelperLab.planRuleLookup(.inode, false, 99, &.{});
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", empty.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.inode, empty.root);
    try std.testing.expectEqual(@as(usize, 0), empty.search_depth);
    try std.testing.expect(!empty.found_existing_rule);
    try std.testing.expectEqual(@as(?u64, null), empty.matched_key_data);

    const found = try ruleset.RulesetHelperLab.planRuleLookup(.net_port, true, 30, &[_]u64{ 40, 20, 30 });
    try std.testing.expectEqual(ruleset.TreeRoot.net_port, found.root);
    try std.testing.expectEqual(@as(usize, 3), found.search_depth);
    try std.testing.expectEqual(ruleset.SearchDirection.left, found.search_steps[0].direction);
    try std.testing.expectEqual(ruleset.SearchDirection.right, found.search_steps[1].direction);
    try std.testing.expectEqual(ruleset.SearchDirection.match, found.search_steps[2].direction);
    try std.testing.expect(found.found_existing_rule);
    try std.testing.expectEqual(@as(?u64, 30), found.matched_key_data);

    const miss = try ruleset.RulesetHelperLab.planRuleLookup(.inode, true, 25, &[_]u64{ 40, 20 });
    try std.testing.expectEqual(@as(usize, 2), miss.search_depth);
    try std.testing.expectEqual(ruleset.SearchDirection.left, miss.search_steps[0].direction);
    try std.testing.expectEqual(ruleset.SearchDirection.right, miss.search_steps[1].direction);
    try std.testing.expect(!miss.found_existing_rule);
    try std.testing.expectEqual(@as(?u64, null), miss.matched_key_data);

    try std.testing.expectError(error.MissingRootNode, ruleset.RulesetHelperLab.planRuleLookup(.inode, true, 1, &.{}));
    try std.testing.expectError(error.UnexpectedWalkerPath, ruleset.RulesetHelperLab.planRuleLookup(.inode, false, 1, &[_]u64{1}));
}

test "phase13 landlock ruleset materialization, replacement, and release planners stay data-only" {
    const materialized = try ruleset.RulesetHelperLab.planRuleMaterialization(.inode, &[_]ruleset.Layer{
        .{ .level = 1, .access = 0x1 },
    }, .{ .level = 2, .access = 0x2 });
    try std.testing.expectEqual(ruleset.RuleMaterializationMode.append_layer, materialized.mode);
    try std.testing.expect(materialized.initializes_rb_node);
    try std.testing.expect(materialized.would_acquire_object_reference);
    try std.testing.expectEqual(@as(usize, 2), materialized.resulting_rule.num_layers);

    const matched_search = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 30, &[_]u64{ 40, 30 }, 7);
    try std.testing.expect(matched_search.matched_existing_rule);
    try std.testing.expectEqual(@as(?u64, 30), matched_search.parent_key_data);
    try std.testing.expectEqual(@as(?ruleset.InsertionSite, null), matched_search.insertion_site);
    try std.testing.expectEqual(@as(u32, 7), matched_search.resulting_num_rules);

    const replacement = try ruleset.RulesetHelperLab.planRuleReplacement(matched_search, materialized);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", replacement.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.inode, replacement.root);
    try std.testing.expectEqual(ruleset.KeyType.inode, replacement.key_type);
    try std.testing.expectEqual(@as(u64, 30), replacement.matched_key_data);
    try std.testing.expect(replacement.reuses_existing_rule_slot);
    try std.testing.expect(replacement.performs_rb_replace_node);
    try std.testing.expect(replacement.would_release_previous_rule);
    try std.testing.expect(replacement.would_release_previous_object_reference);
    try std.testing.expectEqual(@as(u32, 7), replacement.resulting_num_rules);

    const copy_only = try ruleset.RulesetHelperLab.planRuleMaterialization(.net_port, &[_]ruleset.Layer{
        .{ .level = 1, .access = 0x7 },
    }, null);
    try std.testing.expectError(error.InvalidReplacementMaterialization, ruleset.RulesetHelperLab.planRuleReplacement(matched_search, copy_only));

    const unmatched_search = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 35, &[_]u64{30}, 7);
    try std.testing.expectError(error.MissingMatchingRule, ruleset.RulesetHelperLab.planRuleReplacement(unmatched_search, materialized));

    const release = ruleset.RulesetHelperLab.planRuleRelease(.inode, true);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", release.anchor);
    try std.testing.expect(release.may_sleep);
    try std.testing.expect(release.would_release_object_reference);
    try std.testing.expect(release.would_free_rule_allocation);
}
