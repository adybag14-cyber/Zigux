const std = @import("std");

const ruleset = @import("ruleset");

const manifest_text = @embedFile("phase13_landlock_ruleset_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock ruleset descriptor keeps the current bounded helper scope explicit" {
    const descriptor = ruleset.RulesetHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_ruleset_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ruleset_creation_planning);
    try std.testing.expect(descriptor.provides_rule_tree_search_planning);
    try std.testing.expect(descriptor.provides_rule_insertion_planning);
    try std.testing.expect(descriptor.validates_non_empty_access_masks);
    try std.testing.expect(descriptor.validates_layer_capacity);
    try std.testing.expect(descriptor.validates_rule_capacity);
}

test "phase13 landlock ruleset creation keeps handled access masks explicit" {
    const plan = try ruleset.RulesetHelperLab.planRulesetCreation(.{
        .fs = 0x6,
        .net = 0x10,
        .scope = 0x3,
    });

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0x6), plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x10), plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x3), plan.access_masks.scope);
    try std.testing.expect(plan.rejects_empty_masks);
    try std.testing.expect(plan.stores_access_masks_per_layer);
}

test "phase13 landlock ruleset tree search returns root insertion when tree is empty" {
    const plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, false, 64, &.{}, 0);

    try std.testing.expectEqual(ruleset.TreeRoot.inode, plan.root);
    try std.testing.expect(!plan.root_present);
    try std.testing.expectEqual(@as(?ruleset.InsertionSite, .root), plan.insertion_site);
    try std.testing.expect(!plan.matched_existing_rule);
    try std.testing.expectEqual(@as(usize, 0), plan.walker_steps);
}

test "phase13 landlock ruleset tree search reports matched existing rule when walker hits key" {
    const plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);

    try std.testing.expect(plan.root_present);
    try std.testing.expect(plan.matched_existing_rule);
    try std.testing.expectEqual(@as(?ruleset.InsertionSite, null), plan.insertion_site);
    try std.testing.expectEqual(@as(usize, 2), plan.walker_steps);
    try std.testing.expectEqual(@as(u32, 6), plan.current_num_rules);
}

test "phase13 landlock ruleset branch planning links fresh rules and bumps rule count" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, false, 64, &.{}, 0);
    const branch_plan = try ruleset.RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{.{ .level = 0, .access = 0x2 }});

    try std.testing.expectEqual(ruleset.InsertRuleBranchMode.insert_with_link, branch_plan.mode);
    try std.testing.expect(branch_plan.link_plan != null);
    try std.testing.expect(branch_plan.replacement_plan == null);
    try std.testing.expectEqual(@as(u32, 1), branch_plan.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 1), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 0), branch_plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x2), branch_plan.resulting_rule.layers[0].access);
}

test "phase13 landlock ruleset branch planning appends layers when replacing matched rules" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);
    const branch_plan = try ruleset.RulesetHelperLab.planInsertRuleBranch(
        search_plan,
        existing,
        &.{.{ .level = 5, .access = 0x10 }},
    );

    try std.testing.expectEqual(ruleset.InsertRuleBranchMode.replace_existing_rule, branch_plan.mode);
    try std.testing.expect(branch_plan.link_plan == null);
    try std.testing.expect(branch_plan.replacement_plan != null);
    try std.testing.expect(!branch_plan.replacement_plan.?.extends_existing_access);
    try std.testing.expectEqual(@as(usize, 3), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), branch_plan.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), branch_plan.resulting_rule.layers[2].access);
    try std.testing.expectEqual(@as(u32, 6), branch_plan.resulting_num_rules);
}

test "phase13 landlock ruleset branch planning extends access for matched level-zero rules" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{
            .{ .level = 0, .access = 0x1 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{99}, 2);
    const branch_plan = try ruleset.RulesetHelperLab.planInsertRuleBranch(
        search_plan,
        existing,
        &.{.{ .level = 0, .access = 0x4 }},
    );

    try std.testing.expectEqual(ruleset.InsertRuleBranchMode.replace_existing_rule, branch_plan.mode);
    try std.testing.expect(branch_plan.replacement_plan != null);
    try std.testing.expect(branch_plan.replacement_plan.?.extends_existing_access);
    try std.testing.expectEqual(@as(usize, 0), branch_plan.replacement_plan.?.appends_layer_count);
    try std.testing.expectEqual(@as(usize, 1), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 0), branch_plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x5), branch_plan.resulting_rule.layers[0].access);
    try std.testing.expectEqual(@as(u32, 2), branch_plan.resulting_num_rules);
}

test "phase13 landlock ruleset branch planning rejects missing layers and invalid matched-rule updates" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{99}, 2);

    try std.testing.expectError(error.MissingLayers, ruleset.RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{}));
    try std.testing.expectError(
        error.MissingExistingRule,
        ruleset.RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{.{ .level = 2, .access = 0x1 }}),
    );
    try std.testing.expectError(
        error.MatchedRuleRequiresSingleLayer,
        ruleset.RulesetHelperLab.planInsertRuleBranch(
            search_plan,
            ruleset.RulePlan{
                .num_layers = 2,
                .layers = [_]ruleset.Layer{
                    .{ .level = 1, .access = 0x1 },
                    .{ .level = 3, .access = 0x4 },
                } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
            },
            &.{
                .{ .level = 5, .access = 0x10 },
                .{ .level = 6, .access = 0x20 },
            },
        ),
    );
}

test "phase13 landlock ruleset manifest records the current bounded security helper packet" {
    try expectContains(manifest_text, "\"lane_key\": \"P13-L10\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-27\"");
    try expectContains(manifest_text, "\"anchor\": \"security/landlock/ruleset.c\"");
    try expectContains(manifest_text, "\"current_phase13_build_present\": false");
    try expectContains(manifest_text, "\"current_ruleset_zig_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_slice_present\": false");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_ownership_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_survey_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_test_present\": true");
    try expectContains(manifest_text, "\"current_landlock_ruleset_packet_checker_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_manifest_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-helper-starter\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-ownership-note\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-survey-note\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-direct-test-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-packet-checker\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-slice-note\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-tree-state\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-hierarchy-state\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_missing_shared_build_surface\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_missing_review_surface\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_tree_state\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_hierarchy_lifetime\"");
    try expectContains(manifest_text, "planRulesetCreation()");
    try expectContains(manifest_text, "planRuleTreeSearch()");
    try expectContains(manifest_text, "planInsertRuleBranch()");
    try expectContains(manifest_text, "matched level-zero access-extension planning");
    try expectContains(manifest_text, "phase13-landlock-ruleset-survey.md");
    try expectContains(manifest_text, "hierarchy allocation");
}
