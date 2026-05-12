const std = @import("std");

pub const max_num_layers: usize = 16;
pub const max_num_rules: u32 = std.math.maxInt(u32);
pub const max_tree_search_depth: usize = 16;
pub const initially_denied_fs_access: u32 = 1 << 13;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ruleset_creation_planning: bool,
    provides_union_access_masks: bool,
    provides_layer_mask_init: bool,
    provides_rule_unmasking: bool,
    provides_rule_insertion_planning: bool,
    provides_rule_tree_search_planning: bool,
    provides_rule_tree_link_planning: bool,
    provides_rule_tree_replacement_planning: bool,
    touches_live_object_trees: bool,
    touches_live_hierarchy: bool,
};

pub const AccessMasks = struct {
    fs: u32 = 0,
    net: u32 = 0,
    scope: u32 = 0,
};

pub const KeyType = enum {
    inode,
    net_port,
};

pub const CreationInput = struct {
    fs_access_mask: u32 = 0,
    net_access_mask: u32 = 0,
    scope_mask: u32 = 0,
};

pub const CreationPlan = struct {
    anchor: []const u8,
    num_layers: u32,
    access_masks: AccessMasks,
};

pub const Layer = struct {
    level: u16,
    access: u32,
};

pub const RulePlan = struct {
    num_layers: usize,
    layers: [max_num_layers]Layer,
};

pub const RuleInsertionMode = enum {
    insert_new_rule,
    extend_existing_access,
    append_merged_layer,
};

pub const RuleInsertionPlan = struct {
    anchor: []const u8,
    mode: RuleInsertionMode,
    resulting_rule: RulePlan,
    resulting_num_rules: u32,
};

pub const LayerMaskPlan = struct {
    anchor: []const u8,
    handled_accesses: u32,
    masks: [max_num_layers]u32,
};

pub const TreeRoot = enum {
    inode,
    net_port,
};

pub const SearchDirection = enum {
    left,
    right,
    match,
};

pub const InsertionSite = enum {
    root,
    left,
    right,
};

pub const TreeSearchStep = struct {
    node_key_data: u64,
    direction: SearchDirection,
};

pub const RuleTreeSearchPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    search_depth: usize,
    search_steps: [max_tree_search_depth]TreeSearchStep,
    matched_existing_rule: bool,
    parent_key_data: ?u64,
    insertion_site: ?InsertionSite,
    resulting_num_rules: u32,
};

pub const TreeLinkMode = enum {
    initialize_root,
    attach_left,
    attach_right,
};

pub const RuleTreeLinkPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    mode: TreeLinkMode,
    parent_key_data: ?u64,
    performs_rb_link_node: bool,
    performs_rb_insert_color: bool,
    resulting_num_rules: u32,
};

pub const RuleTreeReplacementPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    matched_key_data: u64,
    resulting_rule: RulePlan,
    performs_rb_replace_node: bool,
    resulting_num_rules: u32,
};

fn insertionSiteMatchesTerminalSearchStep(search_plan: RuleTreeSearchPlan, insertion_site: InsertionSite) bool {
    if (search_plan.search_depth == 0 or search_plan.search_depth > max_tree_search_depth) {
        return false;
    }

    const terminal_step = search_plan.search_steps[search_plan.search_depth - 1];
    return switch (terminal_step.direction) {
        .left => insertion_site == .left,
        .right => insertion_site == .right,
        .match => false,
    };
}

fn matchedRuleKeyFromSearchPlan(search_plan: RuleTreeSearchPlan) !u64 {
    if (!search_plan.matched_existing_rule) {
        return error.RuleNotMatched;
    }
    if (search_plan.search_depth == 0) {
        return error.MissingSearchPath;
    }
    if (search_plan.search_depth > max_tree_search_depth) {
        return error.TooDeepSearch;
    }
    if (search_plan.insertion_site != null) {
        return error.UnexpectedInsertionSite;
    }
    if (search_plan.resulting_num_rules == 0) {
        return error.InvalidResultingCount;
    }

    const matched_key_data = search_plan.parent_key_data orelse return error.MissingMatchedNode;
    for (search_plan.search_steps[0 .. search_plan.search_depth - 1]) |step| {
        if (step.direction == .match) {
            return error.InconsistentMatchState;
        }
    }
    const terminal_step = search_plan.search_steps[search_plan.search_depth - 1];
    if (terminal_step.direction != .match or terminal_step.node_key_data != matched_key_data) {
        return error.InconsistentMatchState;
    }

    return matched_key_data;
}

pub const RulesetHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_ruleset_helper_lab",
            .anchor = "security/landlock/ruleset.c",
            .provides_ruleset_creation_planning = true,
            .provides_union_access_masks = true,
            .provides_layer_mask_init = true,
            .provides_rule_unmasking = true,
            .provides_rule_insertion_planning = true,
            .provides_rule_tree_search_planning = true,
            .provides_rule_tree_link_planning = true,
            .provides_rule_tree_replacement_planning = true,
            .touches_live_object_trees = false,
            .touches_live_hierarchy = false,
        };
    }

    pub fn planRulesetCreation(input: CreationInput) !CreationPlan {
        if (input.fs_access_mask == 0 and input.net_access_mask == 0 and input.scope_mask == 0) {
            return error.EmptyRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .num_layers = 1,
            .access_masks = .{
                .fs = input.fs_access_mask,
                .net = input.net_access_mask,
                .scope = input.scope_mask,
            },
        };
    }

    pub fn unionAccessMasks(layers: []const AccessMasks) AccessMasks {
        var combined = AccessMasks{};

        for (layers) |layer| {
            combined.fs |= layer.fs;
            combined.net |= layer.net;
            combined.scope |= layer.scope;
        }

        return combined;
    }

    fn getHandledAccessMask(layer: AccessMasks, key_type: KeyType) u32 {
        return switch (key_type) {
            .inode => if (layer.fs == 0) 0 else layer.fs | initially_denied_fs_access,
            .net_port => layer.net,
        };
    }

    fn selectRoot(key_type: KeyType) TreeRoot {
        return switch (key_type) {
            .inode => .inode,
            .net_port => .net_port,
        };
    }

    pub fn initLayerMasks(domain_layers: []const AccessMasks, access_request: u32, key_type: KeyType) LayerMaskPlan {
        var plan = LayerMaskPlan{
            .anchor = descriptor().anchor,
            .handled_accesses = 0,
            .masks = [_]u32{0} ** max_num_layers,
        };

        if (access_request == 0) {
            return plan;
        }

        const bounded_len = @min(domain_layers.len, max_num_layers);
        for (domain_layers[0..bounded_len], 0..) |layer, i| {
            const handled = getHandledAccessMask(layer, key_type);
            plan.masks[i] = access_request & handled;
            plan.handled_accesses |= plan.masks[i];
        }

        return plan;
    }

    pub fn unmaskLayers(rule_layers: []const Layer, masks: *[max_num_layers]u32) !bool {
        if (rule_layers.len == 0) {
            return false;
        }

        for (rule_layers) |layer| {
            if (layer.level == 0 or layer.level > max_num_layers) {
                return error.InvalidLayer;
            }

            const layer_index = layer.level - 1;
            masks[layer_index] &= ~layer.access;
        }

        for (masks) |pending| {
            if (pending != 0) {
                return false;
            }
        }

        return true;
    }

    fn validateIncomingLayerAccess(layer: Layer) !void {
        if (layer.access == 0) {
            return error.EmptyAccess;
        }
    }

    fn validateIncomingLayers(layers: []const Layer) !void {
        var last_level: u16 = 0;
        var seen_levels = [_]bool{false} ** max_num_layers;

        for (layers, 0..) |layer, i| {
            try validateIncomingLayerAccess(layer);

            if (layer.level == 0) {
                if (layers.len != 1) {
                    return error.InvalidLayer;
                }
                continue;
            }
            if (layer.level > max_num_layers) {
                return error.InvalidLayer;
            }

            const layer_index = layer.level - 1;
            if (seen_levels[layer_index]) {
                return error.DuplicateLayer;
            }
            seen_levels[layer_index] = true;

            if (i != 0 and layer.level <= last_level) {
                return error.NonIncreasingLayers;
            }
            last_level = layer.level;
        }
    }

    fn validateMergedLayerAppend(rule: RulePlan, incoming: Layer) !void {
        try validateIncomingLayerAccess(incoming);

        if (incoming.level == 0 or incoming.level > max_num_layers) {
            return error.InvalidLayer;
        }

        const existing_layers = rule.layers[0..rule.num_layers];
        var last_level: u16 = 0;
        for (existing_layers, 0..) |existing, i| {
            if (existing.level == 0 or existing.level > max_num_layers) {
                return error.InvalidExistingRule;
            }
            if (i != 0 and existing.level <= last_level) {
                return error.InvalidExistingRule;
            }
            if (existing.level == incoming.level) {
                return error.DuplicateLayer;
            }
            last_level = existing.level;
        }

        if (incoming.level <= last_level) {
            return error.NonIncreasingLayers;
        }
    }

    fn copyRulePlan(layers: []const Layer) !RulePlan {
        if (layers.len == 0) {
            return error.MissingLayers;
        }
        if (layers.len > max_num_layers) {
            return error.TooManyLayers;
        }
        try validateIncomingLayers(layers);

        var copied = RulePlan{
            .num_layers = layers.len,
            .layers = [_]Layer{.{ .level = 0, .access = 0 }} ** max_num_layers,
        };
        for (layers, 0..) |layer, i| {
            copied.layers[i] = layer;
        }
        return copied;
    }

    pub fn planRuleInsertion(existing_rule: ?RulePlan, incoming_layers: []const Layer, current_num_rules: u32) !RuleInsertionPlan {
        if (existing_rule) |rule| {
            if (incoming_layers.len != 1) {
                return error.MatchingRuleRequiresSingleLayer;
            }

            const incoming = incoming_layers[0];
            var updated = rule;

            if (incoming.level == 0) {
                try validateIncomingLayerAccess(incoming);
                if (rule.num_layers != 1 or rule.layers[0].level != 0) {
                    return error.InvalidExistingRule;
                }

                updated.layers[0].access |= incoming.access;
                return .{
                    .anchor = descriptor().anchor,
                    .mode = .extend_existing_access,
                    .resulting_rule = updated,
                    .resulting_num_rules = current_num_rules,
                };
            }

            if (rule.num_layers == 0 or rule.num_layers >= max_num_layers) {
                return error.TooManyLayers;
            }
            if (rule.layers[0].level == 0) {
                return error.InvalidExistingRule;
            }
            try validateMergedLayerAppend(rule, incoming);

            updated.layers[rule.num_layers] = incoming;
            updated.num_layers += 1;
            return .{
                .anchor = descriptor().anchor,
                .mode = .append_merged_layer,
                .resulting_rule = updated,
                .resulting_num_rules = current_num_rules,
            };
        }

        if (current_num_rules >= max_num_rules) {
            return error.TooManyRules;
        }

        return .{
            .anchor = descriptor().anchor,
            .mode = .insert_new_rule,
            .resulting_rule = try copyRulePlan(incoming_layers),
            .resulting_num_rules = current_num_rules + 1,
        };
    }

    pub fn planRuleTreeSearch(key_type: KeyType, root_present: bool, search_key_data: u64, walker_keys: []const u64, current_num_rules: u32) !RuleTreeSearchPlan {
        var plan = RuleTreeSearchPlan{
            .anchor = descriptor().anchor,
            .root = selectRoot(key_type),
            .search_depth = 0,
            .search_steps = [_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** max_tree_search_depth,
            .matched_existing_rule = false,
            .parent_key_data = null,
            .insertion_site = null,
            .resulting_num_rules = current_num_rules,
        };

        if (!root_present) {
            if (walker_keys.len != 0) {
                return error.UnexpectedWalkerPath;
            }
            if (current_num_rules >= max_num_rules) {
                return error.TooManyRules;
            }
            plan.insertion_site = .root;
            plan.resulting_num_rules = current_num_rules + 1;
            return plan;
        }

        if (walker_keys.len == 0) {
            return error.MissingRootNode;
        }
        if (walker_keys.len > max_tree_search_depth) {
            return error.TooDeepSearch;
        }

        for (walker_keys, 0..) |walker_key, i| {
            const direction: SearchDirection = if (walker_key == search_key_data)
                .match
            else if (walker_key < search_key_data)
                .right
            else
                .left;

            plan.search_steps[i] = .{
                .node_key_data = walker_key,
                .direction = direction,
            };
            plan.search_depth += 1;

            if (direction == .match) {
                plan.matched_existing_rule = true;
                plan.parent_key_data = walker_key;
                plan.insertion_site = null;
                plan.resulting_num_rules = current_num_rules;
                return plan;
            }

            plan.parent_key_data = walker_key;
            plan.insertion_site = switch (direction) {
                .left => .left,
                .right => .right,
                .match => unreachable,
            };
        }

        if (current_num_rules >= max_num_rules) {
            return error.TooManyRules;
        }
        plan.resulting_num_rules = current_num_rules + 1;
        return plan;
    }

    pub fn planRuleTreeLink(search_plan: RuleTreeSearchPlan) !RuleTreeLinkPlan {
        if (search_plan.matched_existing_rule) {
            return error.RuleAlreadyExists;
        }
        if (search_plan.insertion_site == null) {
            return error.MissingInsertionSite;
        }
        if (search_plan.resulting_num_rules == 0) {
            return error.InvalidResultingCount;
        }

        const insertion_site = search_plan.insertion_site.?;
        const mode: TreeLinkMode = switch (insertion_site) {
            .root => .initialize_root,
            .left => .attach_left,
            .right => .attach_right,
        };

        if (insertion_site == .root and search_plan.search_depth != 0) {
            return error.UnexpectedSearchPath;
        }
        if (insertion_site != .root and search_plan.search_depth == 0) {
            return error.MissingSearchPath;
        }
        if (insertion_site == .root and search_plan.parent_key_data != null) {
            return error.UnexpectedParentNode;
        }
        if (insertion_site != .root and search_plan.parent_key_data == null) {
            return error.MissingParentNode;
        }
        if (insertion_site != .root and !insertionSiteMatchesTerminalSearchStep(search_plan, insertion_site)) {
            return error.InconsistentInsertionSite;
        }

        return .{
            .anchor = search_plan.anchor,
            .root = search_plan.root,
            .mode = mode,
            .parent_key_data = search_plan.parent_key_data,
            .performs_rb_link_node = true,
            .performs_rb_insert_color = true,
            .resulting_num_rules = search_plan.resulting_num_rules,
        };
    }

    pub fn planRuleTreeReplacement(search_plan: RuleTreeSearchPlan, existing_rule: RulePlan, incoming_layer: Layer) !RuleTreeReplacementPlan {
        const matched_key_data = try matchedRuleKeyFromSearchPlan(search_plan);
        const insertion_plan = try planRuleInsertion(existing_rule, &.{incoming_layer}, search_plan.resulting_num_rules);
        if (insertion_plan.mode != .append_merged_layer) {
            return error.RuleReplacementRequiresMergedLayer;
        }

        return .{
            .anchor = search_plan.anchor,
            .root = search_plan.root,
            .matched_key_data = matched_key_data,
            .resulting_rule = insertion_plan.resulting_rule,
            .performs_rb_replace_node = true,
            .resulting_num_rules = search_plan.resulting_num_rules,
        };
    }
};

test "landlock ruleset creation keeps the first-layer access mask packet explicit" {
    const plan = try RulesetHelperLab.planRulesetCreation(.{
        .fs_access_mask = 0x3,
        .net_access_mask = 0x8,
        .scope_mask = 0x10,
    });

    try std.testing.expectEqualStrings(RulesetHelperLab.descriptor().anchor, plan.anchor);
    try std.testing.expectEqual(@as(u32, 1), plan.num_layers);
    try std.testing.expectEqual(@as(u32, 0x3), plan.access_masks.fs);
    try std.testing.expectEqual(@as(u32, 0x8), plan.access_masks.net);
    try std.testing.expectEqual(@as(u32, 0x10), plan.access_masks.scope);
    try std.testing.expectError(error.EmptyRuleset, RulesetHelperLab.planRulesetCreation(.{}));
}

test "landlock ruleset mask helpers keep inode handling and union math explicit" {
    const combined = RulesetHelperLab.unionAccessMasks(&.{
        .{ .fs = 0x3, .net = 0x4, .scope = 0x8 },
        .{ .fs = 0x10, .net = 0x20, .scope = 0x40 },
    });
    try std.testing.expectEqual(@as(u32, 0x13), combined.fs);
    try std.testing.expectEqual(@as(u32, 0x24), combined.net);
    try std.testing.expectEqual(@as(u32, 0x48), combined.scope);

    const inode_masks = RulesetHelperLab.initLayerMasks(&.{
        .{ .fs = 0x3 },
        .{ .fs = 0x10 },
    }, 0x2013, .inode);
    try std.testing.expectEqualStrings(RulesetHelperLab.descriptor().anchor, inode_masks.anchor);
    try std.testing.expectEqual(@as(u32, 0x2003), inode_masks.masks[0]);
    try std.testing.expectEqual(@as(u32, 0x2010), inode_masks.masks[1]);
    try std.testing.expectEqual(@as(u32, 0x2013), inode_masks.handled_accesses);

    const net_masks = RulesetHelperLab.initLayerMasks(&.{
        .{ .net = 0x1 },
        .{ .net = 0x6 },
    }, 0x7, .net_port);
    try std.testing.expectEqual(@as(u32, 0x1), net_masks.masks[0]);
    try std.testing.expectEqual(@as(u32, 0x6), net_masks.masks[1]);
    try std.testing.expectEqual(@as(u32, 0x7), net_masks.handled_accesses);
}

test "landlock ruleset unmasking reports whether any layer access is still pending" {
    var masks = [_]u32{0} ** max_num_layers;
    masks[0] = 0x3;
    masks[1] = 0x4;
    try std.testing.expect(try RulesetHelperLab.unmaskLayers(&.{
        .{ .level = 1, .access = 0x3 },
        .{ .level = 2, .access = 0x4 },
    }, &masks));

    var partial_masks = [_]u32{0} ** max_num_layers;
    partial_masks[0] = 0x7;
    try std.testing.expect(!(try RulesetHelperLab.unmaskLayers(&.{
        .{ .level = 1, .access = 0x3 },
    }, &partial_masks)));
    try std.testing.expectEqual(@as(u32, 0x4), partial_masks[0]);
}

test "landlock ruleset insertion plans cover fresh rules and merged followups" {
    const created = try RulesetHelperLab.planRuleInsertion(null, &.{
        .{ .level = 1, .access = 0x3 },
        .{ .level = 3, .access = 0x8 },
    }, 2);
    try std.testing.expectEqual(RuleInsertionMode.insert_new_rule, created.mode);
    try std.testing.expectEqual(@as(u32, 3), created.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 2), created.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 1), created.resulting_rule.layers[0].level);
    try std.testing.expectEqual(@as(u32, 0x8), created.resulting_rule.layers[1].access);

    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };
    const merged = try RulesetHelperLab.planRuleInsertion(existing, &.{
        .{ .level = 5, .access = 0x10 },
    }, 6);
    try std.testing.expectEqual(RuleInsertionMode.append_merged_layer, merged.mode);
    try std.testing.expectEqual(@as(u32, 6), merged.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 3), merged.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), merged.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), merged.resulting_rule.layers[2].access);
}

test "landlock ruleset tree search and link keep root and attachment sites explicit" {
    const root_search = try RulesetHelperLab.planRuleTreeSearch(.inode, false, 40, &.{}, 4);
    try std.testing.expectEqual(TreeRoot.inode, root_search.root);
    try std.testing.expectEqual(@as(usize, 0), root_search.search_depth);
    try std.testing.expectEqual(@as(?InsertionSite, .root), root_search.insertion_site);
    try std.testing.expectEqual(@as(u32, 5), root_search.resulting_num_rules);

    const root_link = try RulesetHelperLab.planRuleTreeLink(root_search);
    try std.testing.expectEqual(TreeLinkMode.initialize_root, root_link.mode);
    try std.testing.expectEqual(@as(?u64, null), root_link.parent_key_data);
    try std.testing.expect(root_link.performs_rb_link_node);
    try std.testing.expect(root_link.performs_rb_insert_color);

    const attach_search = try RulesetHelperLab.planRuleTreeSearch(.net_port, true, 50, &.{ 10, 30, 40 }, 7);
    try std.testing.expectEqual(TreeRoot.net_port, attach_search.root);
    try std.testing.expectEqual(@as(usize, 3), attach_search.search_depth);
    try std.testing.expectEqual(@as(?u64, 40), attach_search.parent_key_data);
    try std.testing.expectEqual(@as(?InsertionSite, .right), attach_search.insertion_site);
    try std.testing.expectEqual(@as(u32, 8), attach_search.resulting_num_rules);

    const attach_link = try RulesetHelperLab.planRuleTreeLink(attach_search);
    try std.testing.expectEqual(TreeLinkMode.attach_right, attach_link.mode);
    try std.testing.expectEqual(@as(?u64, 40), attach_link.parent_key_data);
    try std.testing.expectEqual(@as(u32, 8), attach_link.resulting_num_rules);
}

test "landlock ruleset insertion rejects empty access when extending a level-zero rule" {
    const base_rule = RulePlan{
        .num_layers = 1,
        .layers = [_]Layer{.{ .level = 0, .access = 0x2 }} ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 1)),
    };

    try std.testing.expectError(error.EmptyAccess, RulesetHelperLab.planRuleInsertion(
        base_rule,
        &.{.{ .level = 0, .access = 0 }},
        1,
    ));
}

test "landlock ruleset insertion still rejects empty access for new rules" {
    try std.testing.expectError(error.EmptyAccess, RulesetHelperLab.planRuleInsertion(
        null,
        &.{.{ .level = 0, .access = 0 }},
        0,
    ));
}

test "landlock ruleset tree-link rejects root insertion plans with retained search state" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 1,
        .search_steps = [_]TreeSearchStep{.{ .node_key_data = 99, .direction = .left }} ++
            ([_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (max_tree_search_depth - 1)),
        .matched_existing_rule = false,
        .parent_key_data = null,
        .insertion_site = .root,
        .resulting_num_rules = 1,
    };

    try std.testing.expectError(error.UnexpectedSearchPath, RulesetHelperLab.planRuleTreeLink(malformed_search_plan));
}

test "landlock ruleset tree-link rejects attachment plans without a recorded search path" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .net_port,
        .search_depth = 0,
        .search_steps = [_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** max_tree_search_depth,
        .matched_existing_rule = false,
        .parent_key_data = 42,
        .insertion_site = .left,
        .resulting_num_rules = 3,
    };

    try std.testing.expectError(error.MissingSearchPath, RulesetHelperLab.planRuleTreeLink(malformed_search_plan));
}

test "landlock ruleset tree-link rejects attachment plans that disagree with the final search step" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 2,
        .search_steps = [_]TreeSearchStep{
            .{ .node_key_data = 10, .direction = .right },
            .{ .node_key_data = 40, .direction = .right },
        } ++ ([_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (max_tree_search_depth - 2)),
        .matched_existing_rule = false,
        .parent_key_data = 40,
        .insertion_site = .left,
        .resulting_num_rules = 5,
    };

    try std.testing.expectError(error.InconsistentInsertionSite, RulesetHelperLab.planRuleTreeLink(malformed_search_plan));
}

test "landlock ruleset tree-replacement rejects empty access in merged-layer followups" {
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    try std.testing.expectError(error.EmptyAccess, RulesetHelperLab.planRuleTreeReplacement(
        search_plan,
        existing,
        .{ .level = 5, .access = 0 },
    ));
}

test "landlock ruleset tree-replacement rejects search plans without a matched rule" {
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 25, &.{ 10, 40, 30 }, 6);
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    try std.testing.expectError(error.RuleNotMatched, RulesetHelperLab.planRuleTreeReplacement(
        search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    ));
}

test "landlock ruleset tree-replacement rejects matched plans that still carry an insertion site" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 2,
        .search_steps = [_]TreeSearchStep{
            .{ .node_key_data = 10, .direction = .right },
            .{ .node_key_data = 40, .direction = .match },
        } ++ ([_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (max_tree_search_depth - 2)),
        .matched_existing_rule = true,
        .parent_key_data = 40,
        .insertion_site = .left,
        .resulting_num_rules = 6,
    };
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    try std.testing.expectError(error.UnexpectedInsertionSite, RulesetHelperLab.planRuleTreeReplacement(
        malformed_search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    ));
}

test "landlock ruleset tree-replacement rejects matched plans with inconsistent terminal state" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 2,
        .search_steps = [_]TreeSearchStep{
            .{ .node_key_data = 10, .direction = .right },
            .{ .node_key_data = 40, .direction = .left },
        } ++ ([_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (max_tree_search_depth - 2)),
        .matched_existing_rule = true,
        .parent_key_data = 40,
        .insertion_site = null,
        .resulting_num_rules = 6,
    };
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    try std.testing.expectError(error.InconsistentMatchState, RulesetHelperLab.planRuleTreeReplacement(
        malformed_search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    ));
}

test "landlock ruleset tree-replacement rejects matched plans with earlier match steps" {
    const malformed_search_plan = RuleTreeSearchPlan{
        .anchor = RulesetHelperLab.descriptor().anchor,
        .root = .inode,
        .search_depth = 3,
        .search_steps = [_]TreeSearchStep{
            .{ .node_key_data = 10, .direction = .match },
            .{ .node_key_data = 30, .direction = .right },
            .{ .node_key_data = 40, .direction = .match },
        } ++ ([_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** (max_tree_search_depth - 3)),
        .matched_existing_rule = true,
        .parent_key_data = 40,
        .insertion_site = null,
        .resulting_num_rules = 6,
    };
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    try std.testing.expectError(error.InconsistentMatchState, RulesetHelperLab.planRuleTreeReplacement(
        malformed_search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    ));
}

test "landlock ruleset tree-replacement returns a merged-layer replacement plan for matched rules" {
    const search_plan = try RulesetHelperLab.planRuleTreeSearch(.inode, true, 99, &.{ 10, 99, 120 }, 6);
    const existing = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 1, .access = 0x1 },
            .{ .level = 3, .access = 0x4 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };

    const replacement = try RulesetHelperLab.planRuleTreeReplacement(
        search_plan,
        existing,
        .{ .level = 5, .access = 0x10 },
    );

    try std.testing.expectEqualStrings(RulesetHelperLab.descriptor().anchor, replacement.anchor);
    try std.testing.expectEqual(TreeRoot.inode, replacement.root);
    try std.testing.expectEqual(@as(u64, 99), replacement.matched_key_data);
    try std.testing.expect(replacement.performs_rb_replace_node);
    try std.testing.expectEqual(@as(u32, 6), replacement.resulting_num_rules);
    try std.testing.expectEqual(@as(usize, 3), replacement.resulting_rule.num_layers);
    try std.testing.expectEqual(@as(u16, 5), replacement.resulting_rule.layers[2].level);
    try std.testing.expectEqual(@as(u32, 0x10), replacement.resulting_rule.layers[2].access);
}
