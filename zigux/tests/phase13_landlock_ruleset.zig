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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L12", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", manifest.anchor);
    try std.testing.expectEqualStrings("a4f70b77b2b4e5c03f5362644f7deda7964167bd", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.ruleset_c_lines >= 700);
    try std.testing.expectEqual(@as(usize, 33), manifest.survey_summary.landlock_security_file_count);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_make_target_present);
    try std.testing.expect(manifest.survey_summary.preexisting_ruleset_zig_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_slice_note_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_survey_note_present);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build_gate = false;
    var saw_make_target = false;
    var saw_starter = false;
    var saw_test_gate = false;
    var saw_slice_note = false;
    var saw_survey_note = false;
    var saw_merge_followup = false;
    var saw_search_followup = false;
    var saw_tree_link_followup = false;
    var saw_materialization_followup = false;
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
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-ruleset-test-gate")) {
            saw_test_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_landlock_ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "helper lab") != null);
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "current helper lab") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-layer-merge-followup")) {
            saw_merge_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "insert_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "access extension") != null);
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
        if (std.mem.eql(u8, gap.id, "phase13-landlock-rule-materialization-followup")) {
            saw_materialization_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "create_rule()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "RB_CLEAR_NODE") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-landlock-live-tree-state-blocker")) {
            saw_live_state_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_lsm_state", gap.status);
            try std.testing.expectEqualStrings("security/landlock/ruleset.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "rb_replace_node()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "object ownership") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 10), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_make_target);
    try std.testing.expect(saw_starter);
    try std.testing.expect(saw_test_gate);
    try std.testing.expect(saw_slice_note);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_merge_followup);
    try std.testing.expect(saw_search_followup);
    try std.testing.expect(saw_tree_link_followup);
    try std.testing.expect(saw_materialization_followup);
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
    try std.testing.expect(descriptor.provides_rule_materialization_planning);
    try std.testing.expect(!descriptor.touches_live_object_trees);
    try std.testing.expect(!descriptor.touches_live_hierarchy);
}

test "phase13 landlock ruleset creation planner rejects an empty ruleset" {
    try std.testing.expectError(
        error.EmptyRuleset,
        ruleset.RulesetHelperLab.planRulesetCreation(.{}),
    );
}

test "phase13 landlock ruleset creation planner keeps the requested masks in one layer" {
    const plan = try ruleset.RulesetHelperLab.planRulesetCreation(.{
        .fs_access_mask = 0x3,
        .net_access_mask = 0x11,
        .scope_mask = 0x20,
    });

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0x3), plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x11), plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x20), plan.access_masks.scope);
}

test "phase13 landlock ruleset access-mask union planner combines every layer family" {
    const combined = ruleset.RulesetHelperLab.unionAccessMasks(&.{
        .{ .fs = 0x1, .net = 0x4, .scope = 0x10 },
        .{ .fs = 0x8, .net = 0x2, .scope = 0x40 },
        .{ .fs = 0x20, .net = 0, .scope = 0x4 },
    });

    try std.testing.expectEqual(@as(u32, 0x29), combined.fs);
    try std.testing.expectEqual(@as(u32, 0x6), combined.net);
    try std.testing.expectEqual(@as(u32, 0x54), combined.scope);
}

test "phase13 landlock ruleset layer-mask planner adds the initially denied filesystem bit" {
    const plan = ruleset.RulesetHelperLab.initLayerMasks(
        &.{
            .{ .fs = 0x3, .net = 0, .scope = 0 },
            .{ .fs = 0x4, .net = 0, .scope = 0 },
            .{ .fs = 0, .net = 0, .scope = 0 },
        },
        0x2007,
        .inode,
    );

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 0x2007), plan.handled_accesses);
    try std.testing.expectEqual(@as(u32, 0x2003), plan.masks[0]);
    try std.testing.expectEqual(@as(u32, 0x2004), plan.masks[1]);
    try std.testing.expectEqual(@as(u32, 0), plan.masks[2]);
}

test "phase13 landlock ruleset unmask planner clears pending accesses across layers" {
    var masks = [_]u32{ 0x7, 0x18 } ++ ([_]u32{0} ** (ruleset.max_num_layers - 2));

    const fully_unmasked = try ruleset.RulesetHelperLab.unmaskLayers(
        &.{
            .{ .level = 1, .access = 0x7 },
            .{ .level = 2, .access = 0x18 },
        },
        &masks,
    );

    try std.testing.expect(fully_unmasked);
    try std.testing.expectEqual(@as(u32, 0), masks[0]);
    try std.testing.expectEqual(@as(u32, 0), masks[1]);
}

test "phase13 landlock ruleset unmask planner rejects invalid layer numbers" {
    var masks = [_]u32{0} ** ruleset.max_num_layers;

    try std.testing.expectError(
        error.InvalidLayer,
        ruleset.RulesetHelperLab.unmaskLayers(&.{.{ .level = 0, .access = 0x1 }}, &masks),
    );
}

test "phase13 landlock ruleset insertion planner extends matching access for level-zero requests" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{.{ .level = 0, .access = 0x3 }} ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };

    const plan = try ruleset.RulesetHelperLab.planRuleInsertion(
        existing,
        &.{.{ .level = 0, .access = 0x4 }},
        9,
    );

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(ruleset.RuleInsertionMode.extend_existing_access, plan.mode);
    try std.testing.expectEqual(@as(usize, 1), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u32, 0x7), plan.resulting_rule.layers[0].access);
    try std.testing.expectEqual(@as(u32, 9), plan.resulting_num_rules);
}

test "phase13 landlock ruleset insertion planner appends a merged layer for matching domain rules" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{ .{ .level = 1, .access = 0x1 }, .{ .level = 2, .access = 0x6 } } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const plan = try ruleset.RulesetHelperLab.planRuleInsertion(
        existing,
        &.{.{ .level = 3, .access = 0x8 }},
        5,
    );

    try std.testing.expectEqual(ruleset.RuleInsertionMode.append_merged_layer, plan.mode);
    try std.testing.expectEqual(@as(usize, 3), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 3), plan.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x8), plan.resulting_rule.layers[2].access);
    try std.testing.expectEqual(@as(u32, 5), plan.resulting_num_rules);
}

test "phase13 landlock ruleset insertion planner allocates a new rule for unmatched keys" {
    const plan = try ruleset.RulesetHelperLab.planRuleInsertion(
        null,
        &.{.{ .level = 0, .access = 0x12 }},
        4,
    );

    try std.testing.expectEqual(ruleset.RuleInsertionMode.insert_new_rule, plan.mode);
    try std.testing.expectEqual(@as(usize, 1), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u32, 0x12), plan.resulting_rule.layers[0].access);
    try std.testing.expectEqual(@as(u32, 5), plan.resulting_num_rules);
}

test "phase13 landlock ruleset insertion planner rejects multi-layer matches" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{.{ .level = 0, .access = 0x3 }} ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };

    try std.testing.expectError(
        error.MatchingRuleRequiresSingleLayer,
        ruleset.RulesetHelperLab.planRuleInsertion(
            existing,
            &.{ .{ .level = 1, .access = 0x4 }, .{ .level = 2, .access = 0x8 } },
            9,
        ),
    );
}

test "phase13 landlock ruleset materialization planner copies a new rule without object ownership for net ports" {
    const plan = try ruleset.RulesetHelperLab.planRuleMaterialization(.net_port, &.{.{ .level = 0, .access = 0x11 }}, null);

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(ruleset.KeyType.net_port, plan.key_type);
    try std.testing.expectEqual(ruleset.RuleMaterializationMode.copy_only, plan.mode);
    try std.testing.expectEqual(@as(usize, 1), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 0), plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x11), plan.resulting_rule.layers[0].access);
    try std.testing.expect(plan.initializes_rb_node);
    try std.testing.expect(!plan.would_acquire_object_reference);
}

test "phase13 landlock ruleset materialization planner appends a merged layer for inode keys" {
    const plan = try ruleset.RulesetHelperLab.planRuleMaterialization(
        .inode,
        &.{ .{ .level = 1, .access = 0x3 }, .{ .level = 2, .access = 0x7 } },
        .{ .level = 4, .access = 0x9 },
    );

    try std.testing.expectEqual(ruleset.RuleMaterializationMode.append_layer, plan.mode);
    try std.testing.expectEqual(@as(usize, 3), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 1), plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u16, 2), plan.resulting_rule.layers[1].level);
    try std.testing.expectEqual(@as(u16, 4), plan.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x9), plan.resulting_rule.layers[2].access);
    try std.testing.expect(plan.initializes_rb_node);
    try std.testing.expect(plan.would_acquire_object_reference);
}

test "phase13 landlock ruleset materialization planner rejects overflow when appending beyond max layers" {
    const base_layers = [_]ruleset.Layer{.{ .level = 1, .access = 1 }} ** ruleset.max_num_layers;

    try std.testing.expectError(
        error.TooManyLayers,
        ruleset.RulesetHelperLab.planRuleMaterialization(.inode, &base_layers, .{ .level = 7, .access = 3 }),
    );
}

test "phase13 landlock ruleset tree-search planner inserts at root when tree is empty" {
    const plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, false, 42, &.{}, 3);

    try std.testing.expectEqual(ruleset.TreeRoot.inode, plan.root);
    try std.testing.expectEqual(@as(usize, 0), plan.search_depth);
    try std.testing.expect(!plan.matched_existing_rule);
    try std.testing.expectEqual(@as(?u64, null), plan.parent_key_data);
    try std.testing.expectEqual(ruleset.InsertionSite.root, plan.insertion_site.?);
    try std.testing.expectEqual(@as(u32, 4), plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-search planner records walker descent for no match" {
    const plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.net_port, true, 25, &.{ 10, 40, 30 }, 7);

    try std.testing.expectEqual(ruleset.TreeRoot.net_port, plan.root);
    try std.testing.expectEqual(@as(usize, 3), plan.search_depth);
    try std.testing.expectEqual(@as(u64, 10), plan.search_steps[0].node_key_data);
    try std.testing.expectEqual(ruleset.SearchDirection.right, plan.search_steps[0].direction);
    try std.testing.expectEqual(@as(u64, 40), plan.search_steps[1].node_key_data);
    try std.testing.expectEqual(ruleset.SearchDirection.left, plan.search_steps[1].direction);
    try std.testing.expectEqual(@as(u64, 30), plan.search_steps[2].node_key_data);
    try std.testing.expectEqual(ruleset.SearchDirection.left, plan.search_steps[2].direction);
    try std.testing.expect(!plan.matched_existing_rule);
    try std.testing.expectEqual(@as(?u64, 30), plan.parent_key_data);
    try std.testing.expectEqual(ruleset.InsertionSite.left, plan.insertion_site.?);
    try std.testing.expectEqual(@as(u32, 8), plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-search planner keeps count on match" {
    const plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 40, &.{ 10, 40, 80 }, 9);

    try std.testing.expect(plan.matched_existing_rule);
    try std.testing.expectEqual(@as(usize, 2), plan.search_depth);
    try std.testing.expectEqual(ruleset.SearchDirection.match, plan.search_steps[1].direction);
    try std.testing.expectEqual(@as(?u64, 40), plan.parent_key_data);
    try std.testing.expectEqual(@as(?ruleset.InsertionSite, null), plan.insertion_site);
    try std.testing.expectEqual(@as(u32, 9), plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-link planner initializes root after empty search" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, false, 42, &.{}, 3);
    const link_plan = try ruleset.RulesetHelperLab.planRuleTreeLink(search_plan);

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", link_plan.anchor);
    try std.testing.expectEqual(ruleset.TreeLinkMode.initialize_root, link_plan.mode);
    try std.testing.expectEqual(@as(?u64, null), link_plan.parent_key_data);
    try std.testing.expect(link_plan.performs_rb_link_node);
    try std.testing.expect(link_plan.performs_rb_insert_color);
    try std.testing.expectEqual(@as(u32, 4), link_plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-link planner attaches on the chosen side" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.net_port, true, 25, &.{ 10, 40, 30 }, 7);
    const link_plan = try ruleset.RulesetHelperLab.planRuleTreeLink(search_plan);

    try std.testing.expectEqual(ruleset.TreeLinkMode.attach_left, link_plan.mode);
    try std.testing.expectEqual(@as(?u64, 30), link_plan.parent_key_data);
    try std.testing.expect(link_plan.performs_rb_link_node);
    try std.testing.expect(link_plan.performs_rb_insert_color);
    try std.testing.expectEqual(@as(u32, 8), link_plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-link planner rejects matching-rule search results" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 40, &.{ 10, 40, 80 }, 9);

    try std.testing.expectError(error.RuleAlreadyExists, ruleset.RulesetHelperLab.planRuleTreeLink(search_plan));
}
