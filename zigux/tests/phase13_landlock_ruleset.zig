const std = @import("std");
const ruleset = @import("landlock_ruleset");

test "phase13 landlock ruleset tree-replacement planner records merged-layer replacement" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);

    const plan = try ruleset.RulesetHelperLab.planRuleTreeReplacement(
        search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    );

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.inode, plan.root);
    try std.testing.expectEqual(@as(u64, 99), plan.matched_key_data);
    try std.testing.expectEqual(@as(usize, 3), plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), plan.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), plan.resulting_rule.layers[2].access);
    try std.testing.expect(plan.performs_rb_replace_node);
    try std.testing.expectEqual(@as(u32, 6), plan.resulting_num_rules);
}

test "phase13 landlock ruleset tree-replacement planner rejects access-extension branch" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{.{ .level = 0, .access = 0x1 }} ++
            ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };

    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 7, &.{ 5, 7, 11 }, 3);

    try std.testing.expectError(
        error.RuleReplacementRequiresMergedLayer,
        ruleset.RulesetHelperLab.planRuleTreeReplacement(
            search_plan,
            existing,
            .{ .level = 0, .access = 0x2 },
        ),
    );
}

test "phase13 landlock ruleset tree-replacement planner rejects empty matched-rule count" {
    const existing = ruleset.RulePlan{
        .num_layers = 1,
        .layers = [_]ruleset.Layer{.{ .level = 1, .access = 0x1 }} ++
            ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 1)),
    };

    const malformed_search_plan = ruleset.RuleTreeSearchPlan{
        .anchor = ruleset.RulesetHelperLab.descriptor().anchor,
        .root = .net_port,
        .search_depth = 1,
        .search_steps = [_]ruleset.TreeSearchStep{.{ .node_key_data = 12, .direction = .match }} ++
            ([_]ruleset.TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (ruleset.max_tree_search_depth - 1)),
        .matched_existing_rule = true,
        .parent_key_data = 12,
        .insertion_site = null,
        .resulting_num_rules = 0,
    };

    try std.testing.expectError(
        error.InvalidResultingCount,
        ruleset.RulesetHelperLab.planRuleTreeReplacement(
            malformed_search_plan,
            existing,
            .{ .level = 2, .access = 0x4 },
        ),
    );
}

test "phase13 landlock ruleset tree-replacement planner rejects search plans without a matched rule" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 25, &.{ 10, 40, 30 }, 6);

    try std.testing.expectError(
        error.RuleNotMatched,
        ruleset.RulesetHelperLab.planRuleTreeReplacement(
            search_plan,
            existing,
            .{ .level = 5, .access = 0x10 },
        ),
    );
}

test "phase13 landlock ruleset tree-replacement planner rejects matched plans that still carry an insertion site" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const malformed_search_plan = ruleset.RuleTreeSearchPlan{
        .anchor = ruleset.RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 2,
        .search_steps = [_]ruleset.TreeSearchStep{
            .{ .node_key_data = 10, .direction = .right },
            .{ .node_key_data = 40, .direction = .match },
        } ++ ([_]ruleset.TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (ruleset.max_tree_search_depth - 2)),
        .matched_existing_rule = true,
        .parent_key_data = 40,
        .insertion_site = .left,
        .resulting_num_rules = 6,
    };

    try std.testing.expectError(
        error.UnexpectedInsertionSite,
        ruleset.RulesetHelperLab.planRuleTreeReplacement(
            malformed_search_plan,
            existing,
            .{ .level = 5, .access = 0x10 },
        ),
    );
}

test "phase13 landlock ruleset tree-replacement planner rejects inconsistent matched search state" {
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const malformed_search_plan = ruleset.RuleTreeSearchPlan{
        .anchor = ruleset.RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 2,
        .search_steps = [_]ruleset.TreeSearchStep{
            .{ .node_key_data = 10, .direction = .right },
            .{ .node_key_data = 40, .direction = .left },
        } ++ ([_]ruleset.TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (ruleset.max_tree_search_depth - 2)),
        .matched_existing_rule = true,
        .parent_key_data = 40,
        .insertion_site = null,
        .resulting_num_rules = 6,
    };

    try std.testing.expectError(
        error.InconsistentMatchState,
        ruleset.RulesetHelperLab.planRuleTreeReplacement(
            malformed_search_plan,
            existing,
            .{ .level = 5, .access = 0x10 },
        ),
    );
}
