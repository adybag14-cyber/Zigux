const std = @import("std");

pub const max_num_layers: usize = 16;
pub const max_num_rules: u32 = 65535;

pub const KeyType = enum {
    inode,
    net_port,
};

pub const TreeRoot = enum {
    inode,
    net_port,
};

pub const InsertionSite = enum {
    root,
    left,
    right,
};

pub const InsertRuleBranchMode = enum {
    insert_with_link,
    replace_existing_rule,
};

pub const AccessMasks = struct {
    fs: u32 = 0,
    net: u32 = 0,
    scope: u32 = 0,
};

pub const Layer = struct {
    level: u16,
    access: u32,
};

pub const RulePlan = struct {
    num_layers: usize,
    layers: [max_num_layers]Layer,
};

pub const CreationPlan = struct {
    anchor: []const u8,
    num_layers: u32,
    access_masks: AccessMasks,
    rejects_empty_masks: bool,
    stores_access_masks_per_layer: bool,
};

pub const MergePlan = struct {
    anchor: []const u8,
    parent_present: bool,
    inherited_parent_layers: usize,
    appended_source_layer_index: usize,
    resulting_num_layers: u32,
    resulting_access_masks: [max_num_layers]AccessMasks,
    allocates_new_domain: bool,
    copies_parent_rules: bool,
    merges_source_rules: bool,
    upgrades_handled_access_masks_for_source_layer: bool,
};

pub const RuleTreeSearchPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    root_present: bool,
    search_key_data: u64,
    walker_steps: usize,
    matched_existing_rule: bool,
    insertion_site: ?InsertionSite,
    current_num_rules: u32,
};

pub const InsertLinkPlan = struct {
    insertion_site: InsertionSite,
    inserts_new_rule: bool,
    bumps_rule_count: bool,
};

pub const ReplaceRulePlan = struct {
    appends_layer_count: usize,
    preserves_rule_count: bool,
    extends_existing_access: bool,
};

pub const InsertRuleBranchPlan = struct {
    anchor: []const u8,
    mode: InsertRuleBranchMode,
    link_plan: ?InsertLinkPlan,
    replacement_plan: ?ReplaceRulePlan,
    resulting_rule: RulePlan,
    resulting_num_rules: u32,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ruleset_creation_planning: bool,
    provides_ruleset_merge_planning: bool,
    provides_rule_tree_search_planning: bool,
    provides_rule_insertion_planning: bool,
    validates_non_empty_access_masks: bool,
    validates_layer_capacity: bool,
    validates_rule_capacity: bool,
    validates_matched_layer_order: bool,
};

pub const RulesetHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_ruleset_helper_lab",
            .anchor = "security/landlock/ruleset.c",
            .provides_ruleset_creation_planning = true,
            .provides_ruleset_merge_planning = true,
            .provides_rule_tree_search_planning = true,
            .provides_rule_insertion_planning = true,
            .validates_non_empty_access_masks = true,
            .validates_layer_capacity = true,
            .validates_rule_capacity = true,
            .validates_matched_layer_order = true,
        };
    }

    pub fn planRulesetCreation(input: AccessMasks) !CreationPlan {
        if (isEmptyAccessMasks(input)) {
            return error.EmptyRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .num_layers = 1,
            .access_masks = input,
            .rejects_empty_masks = true,
            .stores_access_masks_per_layer = true,
        };
    }

    pub fn planRulesetMerge(
        parent_layers: []const AccessMasks,
        source_masks: AccessMasks,
    ) !MergePlan {
        if (isEmptyAccessMasks(source_masks)) {
            return error.EmptyRuleset;
        }
        if (parent_layers.len >= max_num_layers) {
            return error.TooManyLayers;
        }

        var resulting_access_masks = zeroAccessMasks();
        for (parent_layers, 0..) |mask, index| {
            resulting_access_masks[index] = mask;
        }

        const appended_source_layer_index = parent_layers.len;
        resulting_access_masks[appended_source_layer_index] = source_masks;

        return .{
            .anchor = descriptor().anchor,
            .parent_present = parent_layers.len != 0,
            .inherited_parent_layers = parent_layers.len,
            .appended_source_layer_index = appended_source_layer_index,
            .resulting_num_layers = @intCast(appended_source_layer_index + 1),
            .resulting_access_masks = resulting_access_masks,
            .allocates_new_domain = true,
            .copies_parent_rules = parent_layers.len != 0,
            .merges_source_rules = true,
            .upgrades_handled_access_masks_for_source_layer = parent_layers.len != 0,
        };
    }

    pub fn planRuleTreeSearch(
        key_type: KeyType,
        root_present: bool,
        search_key_data: u64,
        walker_keys: []const u64,
        current_num_rules: u32,
    ) !RuleTreeSearchPlan {
        const root = switch (key_type) {
            .inode => TreeRoot.inode,
            .net_port => TreeRoot.net_port,
        };

        if (!root_present) {
            return .{
                .anchor = descriptor().anchor,
                .root = root,
                .root_present = false,
                .search_key_data = search_key_data,
                .walker_steps = 0,
                .matched_existing_rule = false,
                .insertion_site = .root,
                .current_num_rules = current_num_rules,
            };
        }

        var site: ?InsertionSite = null;
        for (walker_keys, 0..) |walker_key, index| {
            if (walker_key == search_key_data) {
                return .{
                    .anchor = descriptor().anchor,
                    .root = root,
                    .root_present = true,
                    .search_key_data = search_key_data,
                    .walker_steps = index + 1,
                    .matched_existing_rule = true,
                    .insertion_site = null,
                    .current_num_rules = current_num_rules,
                };
            }
            site = if (walker_key < search_key_data) .right else .left;
        }

        return .{
            .anchor = descriptor().anchor,
            .root = root,
            .root_present = true,
            .search_key_data = search_key_data,
            .walker_steps = walker_keys.len,
            .matched_existing_rule = false,
            .insertion_site = site orelse .root,
            .current_num_rules = current_num_rules,
        };
    }

    pub fn planInsertRuleBranch(
        search_plan: RuleTreeSearchPlan,
        existing_rule: ?RulePlan,
        incoming_layers: []const Layer,
    ) !InsertRuleBranchPlan {
        if (incoming_layers.len == 0) {
            return error.MissingLayers;
        }
        if (incoming_layers.len > max_num_layers) {
            return error.TooManyLayers;
        }

        if (search_plan.matched_existing_rule) {
            const current_rule = existing_rule orelse return error.MissingExistingRule;
            if (current_rule.num_layers == 0 or current_rule.num_layers > max_num_layers) {
                return error.InvalidExistingRule;
            }
            if (incoming_layers.len != 1) {
                return error.MatchedRuleRequiresSingleLayer;
            }

            if (incoming_layers[0].level == 0) {
                if (current_rule.num_layers != 1 or current_rule.layers[0].level != 0) {
                    return error.InvalidExistingRule;
                }

                const resulting_rule = copyRuleWithExtendedAccess(current_rule, incoming_layers[0].access);
                return .{
                    .anchor = descriptor().anchor,
                    .mode = .replace_existing_rule,
                    .link_plan = null,
                    .replacement_plan = .{
                        .appends_layer_count = 0,
                        .preserves_rule_count = true,
                        .extends_existing_access = true,
                    },
                    .resulting_rule = resulting_rule,
                    .resulting_num_rules = search_plan.current_num_rules,
                };
            }

            try validateMatchedLayerAppend(current_rule, incoming_layers[0].level);
            if (current_rule.num_layers + incoming_layers.len > max_num_layers) {
                return error.TooManyLayers;
            }

            const resulting_rule = copyRuleWithAppendedLayers(current_rule, incoming_layers);
            return .{
                .anchor = descriptor().anchor,
                .mode = .replace_existing_rule,
                .link_plan = null,
                .replacement_plan = .{
                    .appends_layer_count = incoming_layers.len,
                    .preserves_rule_count = true,
                    .extends_existing_access = false,
                },
                .resulting_rule = resulting_rule,
                .resulting_num_rules = search_plan.current_num_rules,
            };
        }

        if (search_plan.current_num_rules >= max_num_rules) {
            return error.TooManyRules;
        }

        const resulting_rule = makeRuleFromLayers(incoming_layers);
        return .{
            .anchor = descriptor().anchor,
            .mode = .insert_with_link,
            .link_plan = .{
                .insertion_site = search_plan.insertion_site orelse .root,
                .inserts_new_rule = true,
                .bumps_rule_count = true,
            },
            .replacement_plan = null,
            .resulting_rule = resulting_rule,
            .resulting_num_rules = search_plan.current_num_rules + 1,
        };
    }

    fn isEmptyAccessMasks(input: AccessMasks) bool {
        return input.fs == 0 and input.net == 0 and input.scope == 0;
    }

    fn validateMatchedLayerAppend(rule: RulePlan, incoming_level: u16) !void {
        if (rule.layers[0].level == 0) {
            return error.InvalidExistingRule;
        }

        var previous_level = rule.layers[0].level;
        var index: usize = 1;
        while (index < rule.num_layers) : (index += 1) {
            const current_level = rule.layers[index].level;
            if (current_level == 0 or current_level <= previous_level) {
                return error.InvalidExistingRule;
            }
            previous_level = current_level;
        }

        if (incoming_level <= previous_level) {
            return error.InvalidLayerOrder;
        }
    }

    fn zeroAccessMasks() [max_num_layers]AccessMasks {
        return [_]AccessMasks{.{}} ** max_num_layers;
    }

    fn makeRuleFromLayers(layers: []const Layer) RulePlan {
        var result = zeroRule();
        result.num_layers = layers.len;
        for (layers, 0..) |layer, index| {
            result.layers[index] = layer;
        }
        return result;
    }

    fn copyRuleWithAppendedLayers(rule: RulePlan, extra_layers: []const Layer) RulePlan {
        var result = rule;
        for (extra_layers, 0..) |layer, index| {
            result.layers[rule.num_layers + index] = layer;
        }
        result.num_layers = rule.num_layers + extra_layers.len;
        return result;
    }

    fn copyRuleWithExtendedAccess(rule: RulePlan, extra_access: u32) RulePlan {
        var result = rule;
        result.layers[0].access |= extra_access;
        return result;
    }

    fn zeroRule() RulePlan {
        return .{
            .num_layers = 0,
            .layers = [_]Layer{.{ .level = 0, .access = 0 }} ** max_num_layers,
        };
    }
};

test "landlock ruleset descriptor stays inside bounded helper scope" {
    const descriptor = RulesetHelperLab.descriptor();

    try std.testing.expectEqualStrings("landlock_ruleset_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_ruleset_creation_planning);
    try std.testing.expect(descriptor.provides_ruleset_merge_planning);
    try std.testing.expect(descriptor.provides_rule_tree_search_planning);
    try std.testing.expect(descriptor.provides_rule_insertion_planning);
    try std.testing.expect(descriptor.validates_non_empty_access_masks);
    try std.testing.expect(descriptor.validates_layer_capacity);
    try std.testing.expect(descriptor.validates_rule_capacity);
    try std.testing.expect(descriptor.validates_matched_layer_order);
}

test "landlock ruleset creation keeps handled access masks explicit" {
    const plan = try RulesetHelperLab.planRulesetCreation(.{
        .fs = 0x6,
        .net = 0x10,
        .scope = 0x3,
    });

    try std.testing.expectEqualStrings(RulesetHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0x6), plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x10), plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x3), plan.access_masks.scope);
    try std.testing.expect(plan.rejects_empty_masks);
    try std.testing.expect(plan.stores_access_masks_per_layer);
}

test "landlock ruleset creation rejects empty masks" {
    try std.testing.expectError(error.EmptyRuleset, RulesetHelperLab.planRulesetCreation(.{}));
}

test "landlock ruleset merge appends source layer after inherited parent layers" {
    const plan = try RulesetHelperLab.planRulesetMerge(
        &.{
            .{ .fs = 0x1, .net = 0x2, .scope = 0x4 },
            .{ .fs = 0x8, .net = 0x10, .scope = 0x20 },
        },
        .{ .fs = 0x40, .net = 0x80, .scope = 0x100 },
    );

    try std.testing.expectEqualStrings(RulesetHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expect(plan.parent_present);
    try std.testing.expectEqual(@as(usize, 2), plan.inherited_parent_layers);
    try std.testing.expectEqual(@as(usize, 2), plan.appended_source_layer_index);
    try std.testing.expectEqual(@as(u32, 3), plan.resulting_num_layers);
    try std.testing.expectEqual(@as(u32, 0x1), plan.resulting_access_masks[0].fs);
    try std.testing.expectEqual(@as(u32, 0x10), plan.resulting_access_masks[1].net);
    try std.testing.expectEqual(@as(u32, 0x100), plan.resulting_access_masks[2].scope);
    try std.testing.expect(plan.allocates_new_domain);
    try std.testing.expect(plan.copies_parent_rules);
    try std.testing.expect(plan.merges_source_rules);
    try std.testing.expect(plan.upgrades_handled_access_masks_for_source_layer);
}

test "landlock ruleset merge creates a one-layer domain without a parent" {
    const plan = try RulesetHelperLab.planRulesetMerge(&.{}, .{
        .fs = 0x6,
        .net = 0x10,
        .scope = 0x3,
    });

    try std.testing.expect(!plan.parent_present);
    try std.testing.expectEqual(@as(usize, 0), plan.inherited_parent_layers);
    try std.testing.expectEqual(@as(usize, 0), plan.appended_source_layer_index);
    try std.testing.expectEqual(@as(u32, 1), plan.resulting_num_layers);
    try std.testing.expectEqual(@as(u32, 0x6), plan.resulting_access_masks[0].fs);
    try std.testing.expectEqual(@as(u32, 0x10), plan.resulting_access_masks[0].net);
    try std.testing.expectEqual(@as(u32, 0x3), plan.resulting_access_masks[0].scope);
    try std.testing.expect(!plan.copies_parent_rules);
    try std.testing.expect(!plan.upgrades_handled_access_masks_for_source_layer);
}

test "landlock ruleset merge rejects empty source masks and layer overflow" {
    try std.testing.expectError(error.EmptyRuleset, RulesetHelperLab.planRulesetMerge(
        &.{.{ .fs = 1 }},
        .{},
    ));

    const full_parent = [_]AccessMasks{.{ .fs = 1 }} ** max_num_layers;
    try std.testing.expectError(error.TooManyLayers, RulesetHelperLab.planRulesetMerge(
        &full_parent,
        .{ .fs = 1 },
    ));
}

test "landlock ruleset tree search returns root insertion when tree is empty" {
    const plan = try RulesetHelperLab.planRuleTreeSearch(.inode, false, 64, &.{}, 0);

    try std.testing.expectEqual(TreeRoot.inode, plan.root);
    try std.testing.expect(!plan.root_present);
    try std.testing.expectEqual(@as(?InsertionSite, .root), plan.insertion_site);
    try std.testing.expect(!plan.matched_existing_rule);
    try std.testing.expectEqual(@as(usize, 0), plan.walker_steps);
}

test "landlock ruleset tree search reports matched existing rule when walker hits key" {
    const plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);

    try std.testing.expect(plan.root_present);
    try std.testing.expect(plan.matched_existing_rule);
    try std.testing.expectEqual(@as(?InsertionSite, null), plan.insertion_site);
    try std.testing.expectEqual(@as(usize, 2), plan.walker_steps);
    try std.testing.expectEqual(@as(u32, 6), plan.current_num_rules);
}

test "landlock ruleset branch planning links fresh rules and bumps rule count" {
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, false, 64, &.{}, 0);
    const branch_plan = try RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{.{ .level = 0, .access = 0x2 }});

    try std.testing.expectEqual(InsertRuleBranchMode.insert_with_link, branch_plan.mode);
    try std.testing.expect(branch_plan.link_plan != null);
    try std.testing.expect(branch_plan.replacement_plan == null);
    try std.testing.expectEqual(@as(u32, 1), branch_plan.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 1), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 0), branch_plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x2), branch_plan.resulting_rule.layers[0].access);
}

test "landlock ruleset branch planning appends layers when replacing matched rules" {
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);
    const branch_plan = try RulesetHelperLab.planInsertRuleBranch(
        search_plan,
        existing,
        &.{.{ .level = 5, .access = 0x10 }},
    );

    try std.testing.expectEqual(InsertRuleBranchMode.replace_existing_rule, branch_plan.mode);
    try std.testing.expect(branch_plan.link_plan == null);
    try std.testing.expect(branch_plan.replacement_plan != null);
    try std.testing.expect(!branch_plan.replacement_plan.?.extends_existing_access);
    try std.testing.expectEqual(@as(usize, 3), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), branch_plan.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), branch_plan.resulting_rule.layers[2].access);
    try std.testing.expectEqual(@as(u32, 6), branch_plan.resulting_num_rules);
}

test "landlock ruleset branch planning extends access for matched level-zero rules" {
    const existing = RulePlan{
        .num_layers = 1,
        .layers = [_]Layer{
            .{ .level = 0, .access = 0x1 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 1)),
    };
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{99}, 2);
    const branch_plan = try RulesetHelperLab.planInsertRuleBranch(
        search_plan,
        existing,
        &.{.{ .level = 0, .access = 0x4 }},
    );

    try std.testing.expectEqual(InsertRuleBranchMode.replace_existing_rule, branch_plan.mode);
    try std.testing.expect(branch_plan.replacement_plan != null);
    try std.testing.expect(branch_plan.replacement_plan.?.extends_existing_access);
    try std.testing.expectEqual(@as(usize, 0), branch_plan.replacement_plan.?.appends_layer_count);
    try std.testing.expectEqual(@as(usize, 1), branch_plan.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 0), branch_plan.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x5), branch_plan.resulting_rule.layers[0].access);
    try std.testing.expectEqual(@as(u32, 2), branch_plan.resulting_num_rules);
}

test "landlock ruleset branch planning rejects missing layers invalid matched-rule updates and non-increasing layer order" {
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{99}, 2);

    try std.testing.expectError(error.MissingLayers, RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{}));
    try std.testing.expectError(
        error.MissingExistingRule,
        RulesetHelperLab.planInsertRuleBranch(search_plan, null, &.{.{ .level = 2, .access = 0x1 }}),
    );
    try std.testing.expectError(
        error.MatchedRuleRequiresSingleLayer,
        RulesetHelperLab.planInsertRuleBranch(
            search_plan,
            RulePlan{
                .num_layers = 2,
                .layers = [_]Layer{
                    .{ .level = 1, .access = 0x1 },
                    .{ .level = 3, .access = 0x4 },
                } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
            },
            &.{
                .{ .level = 5, .access = 0x10 },
                .{ .level = 6, .access = 0x20 },
            },
        ),
    );
    try std.testing.expectError(
        error.InvalidLayerOrder,
        RulesetHelperLab.planInsertRuleBranch(
            search_plan,
            RulePlan{
                .num_layers = 2,
                .layers = [_]Layer{
                    .{ .level = 1, .access = 0x1 },
                    .{ .level = 3, .access = 0x4 },
                } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
            },
            &.{.{ .level = 3, .access = 0x20 }},
        ),
    );
    try std.testing.expectError(
        error.InvalidExistingRule,
        RulesetHelperLab.planInsertRuleBranch(
            search_plan,
            RulePlan{
                .num_layers = 2,
                .layers = [_]Layer{
                    .{ .level = 3, .access = 0x1 },
                    .{ .level = 2, .access = 0x4 },
                } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
            },
            &.{.{ .level = 5, .access = 0x20 }},
        ),
    );
}
