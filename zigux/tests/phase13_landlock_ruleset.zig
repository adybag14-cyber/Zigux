const std = @import("std");
const ruleset = @import("ruleset");
const manifest_text = @embedFile("phase13_landlock_ruleset_manifest.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 landlock ruleset descriptor keeps the bounded helper scope explicit" {
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
    try std.testing.expect(descriptor.provides_rule_tree_replacement_planning);
    try std.testing.expect(!descriptor.touches_live_object_trees);
    try std.testing.expect(!descriptor.touches_live_hierarchy);
}

test "phase13 landlock ruleset keeps no-match tree-link planning explicit" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.net_port, true, 50, &.{ 10, 30, 40 }, 7);
    const link_plan = try ruleset.RulesetHelperLab.planRuleTreeLink(search_plan);

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", link_plan.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.net_port, link_plan.root);
    try std.testing.expectEqual(ruleset.TreeLinkMode.attach_right, link_plan.mode);
    try std.testing.expectEqual(@as(?u64, 40), link_plan.parent_key_data);
    try std.testing.expect(link_plan.performs_rb_link_node);
    try std.testing.expect(link_plan.performs_rb_insert_color);
    try std.testing.expectEqual(@as(u32, 8), link_plan.resulting_num_rules);
}

test "phase13 landlock ruleset keeps matched-rule replacement planning pre-rb_replace_node" {
    const search_plan = try ruleset.RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);
    const existing = ruleset.RulePlan{
        .num_layers = 2,
        .layers = [_]ruleset.Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]ruleset.Layer{.{ .level = 0, .access = 0 }} ** (ruleset.max_num_layers - 2)),
    };

    const replacement = try ruleset.RulesetHelperLab.planRuleTreeReplacement(
        search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    );

    try std.testing.expectEqualStrings("security/landlock/ruleset.c", replacement.anchor);
    try std.testing.expectEqual(ruleset.TreeRoot.inode, replacement.root);
    try std.testing.expectEqual(@as(u64, 99), replacement.matched_key_data);
    try std.testing.expect(replacement.performs_rb_replace_node);
    try std.testing.expectEqual(@as(u32, 6), replacement.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 3), replacement.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), replacement.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), replacement.resulting_rule.layers[2].access);
}

test "phase13 landlock ruleset manifest records the bounded security helper packet" {
    try expectContains(manifest_text, "\"lane_key\": \"P13-L09\"");
    try expectContains(manifest_text, "\"surveyed_commit\": \"master-readback-2026-05-12\"");
    try expectContains(manifest_text, "\"anchor\": \"security/landlock/ruleset.c\"");
    try expectContains(manifest_text, "\"current_phase13_build_present\": false");
    try expectContains(manifest_text, "\"current_ruleset_zig_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_test_present\": true");
    try expectContains(manifest_text, "\"current_landlock_ruleset_packet_checker_present\": true");
    try expectContains(manifest_text, "\"current_phase13_landlock_ruleset_manifest_present\": true");
    try expectContains(manifest_text, "\"id\": \"phase13-build-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-helper-starter\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-direct-test-gate\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-ruleset-packet-checker\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-tree-state\"");
    try expectContains(manifest_text, "\"id\": \"phase13-landlock-live-hierarchy-state\"");
    try expectContains(manifest_text, "\"status\": \"starter_landed\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_missing_shared_build_surface\"");
    try expectContains(manifest_text, "\"status\": \"blocked_on_live_tree_state\"");
    try expectContains(manifest_text, "rb_replace_node()");
    try expectContains(manifest_text, "hierarchy allocation");
}
