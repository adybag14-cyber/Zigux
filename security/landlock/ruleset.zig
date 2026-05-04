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
    provides_rule_lookup_planning: bool,
    provides_rule_materialization_planning: bool,
    provides_rule_replacement_planning: bool,
    provides_rule_release_planning: bool,
    provides_rule_merge_tree_replay_planning: bool,
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

pub const RuleTreeLinkPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    mode: TreeLinkMode,
    parent_key_data: ?u64,
    performs_rb_link_node: bool,
    performs_rb_insert_color: bool,
    resulting_num_rules: u32,
};

pub const RuleLookupPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    search_depth: usize,
    search_steps: [max_tree_search_depth]TreeSearchStep,
    found_existing_rule: bool,
    matched_key_data: ?u64,
};

pub const TreeLinkMode = enum {
    initialize_root,
    attach_left,
    attach_right,
};

pub const RuleMaterializationMode = enum {
    copy_only,
    append_layer,
};

pub const RuleMaterializationPlan = struct {
    anchor: []const u8,
    key_type: KeyType,
    mode: RuleMaterializationMode,
    resulting_rule: RulePlan,
    initializes_rb_node: bool,
    would_acquire_object_reference: bool,
};

pub const RuleReplacementPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    key_type: KeyType,
    matched_key_data: u64,
    reuses_existing_rule_slot: bool,
    performs_rb_replace_node: bool,
    would_release_previous_rule: bool,
    would_release_previous_object_reference: bool,
    resulting_num_rules: u32,
};

pub const RuleReleasePlan = struct {
    anchor: []const u8,
    key_type: KeyType,
    rule_present: bool,
    may_sleep: bool,
    would_release_object_reference: bool,
    would_free_rule_allocation: bool,
};

pub const TreeMergeReplayPlan = struct {
    anchor: []const u8,
    root: TreeRoot,
    key_type: KeyType,
    destination_layer: Layer,
    source_rule_num_layers: usize,
    would_reuse_source_key: bool,
    would_call_insert_rule: bool,
};

pub const CapacityInvariantPlan = struct {
    anchor: []const u8,
    rule_num_layers_fits_max_layers: bool,
    creation_num_layers_fits_max_layers: bool,
    layer_level_fits_max_layers: bool,
    layer_access_carries_initially_denied_fs_access: bool,
    ruleset_num_rules_reaches_max: bool,
    rule_storage_slots_match_max_layers: bool,
};

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
            .provides_rule_lookup_planning = true,
            .provides_rule_materialization_planning = true,
            .provides_rule_replacement_planning = true,
            .provides_rule_release_planning = true,
            .provides_rule_merge_tree_replay_planning = true,
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

    fn validateOrderedLayers(rule_layers: []const Layer) !void {
        if (rule_layers.len == 0) {
            return error.MissingLayers;
        }

        var previous_level: u16 = 0;
        for (rule_layers) |layer| {
            if (layer.level == 0 or layer.level > max_num_layers) {
                return error.InvalidLayer;
            }
            if (layer.level <= previous_level) {
                return error.InvalidLayerShape;
            }
            previous_level = layer.level;
        }
    }

    pub fn unmaskLayers(rule_layers: []const Layer, masks: *[max_num_layers]u32) !bool {
        try validateOrderedLayers(rule_layers);

        for (rule_layers) |layer| {
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

    fn validateRuleLayers(rule_layers: []const Layer) !void {
        if (rule_layers.len == 0) {
            return error.MissingLayers;
        }

        if (rule_layers[0].level == 0) {
            if (rule_layers.len != 1) {
                return error.InvalidLayerShape;
            }
            return;
        }

        var previous_level: u16 = 0;
        for (rule_layers) |layer| {
            if (layer.level == 0 or layer.level > max_num_layers) {
                return error.InvalidLayer;
            }
            if (layer.level <= previous_level) {
                return error.InvalidLayerShape;
            }
            previous_level = layer.level;
        }
    }

    fn makeRulePlan(base_layers: []const Layer, appended_layer: ?Layer) !RulePlan {
        try validateRuleLayers(base_layers);
        const extra_layers: usize = if (appended_layer == null) 0 else 1;
        const resulting_num_layers = base_layers.len + extra_layers;
        if (resulting_num_layers > max_num_layers) {
            return error.TooManyLayers;
        }

        if (appended_layer) |layer| {
            if (base_layers[0].level == 0) {
                return error.InvalidLayerShape;
            }
            if (layer.level == 0 or layer.level > max_num_layers) {
                return error.InvalidLayer;
            }
            if (layer.level <= base_layers[base_layers.len - 1].level) {
                return error.InvalidLayerShape;
            }
        }

        var copied = RulePlan{
            .num_layers = resulting_num_layers,
            .layers = [_]Layer{.{ .level = 0, .access = 0 }} ** max_num_layers,
        };
        for (base_layers, 0..) |layer, i| {
            copied.layers[i] = layer;
        }
        if (appended_layer) |layer| {
            copied.layers[base_layers.len] = layer;
        }
        return copied;
    }

    pub fn planRuleMaterialization(key_type: KeyType, base_layers: []const Layer, appended_layer: ?Layer) !RuleMaterializationPlan {
        return .{
            .anchor = descriptor().anchor,
            .key_type = key_type,
            .mode = if (appended_layer == null) .copy_only else .append_layer,
            .resulting_rule = try makeRulePlan(base_layers, appended_layer),
            .initializes_rb_node = true,
            .would_acquire_object_reference = key_type == .inode,
        };
    }

    pub fn planRuleReplacement(search_plan: RuleTreeSearchPlan, materialization_plan: RuleMaterializationPlan) !RuleReplacementPlan {
        if (!search_plan.matched_existing_rule) {
            return error.MissingMatchingRule;
        }
        if (search_plan.parent_key_data == null) {
            return error.MissingMatchedRuleKey;
        }
        if (search_plan.insertion_site != null) {
            return error.UnexpectedInsertionSite;
        }
        if (materialization_plan.mode != .append_layer) {
            return error.InvalidReplacementMaterialization;
        }
        if (selectRoot(materialization_plan.key_type) != search_plan.root) {
            return error.KeyTypeRootMismatch;
        }
        if (search_plan.resulting_num_rules == 0) {
            return error.InvalidResultingCount;
        }

        return .{
            .anchor = descriptor().anchor,
            .root = search_plan.root,
            .key_type = materialization_plan.key_type,
            .matched_key_data = search_plan.parent_key_data.?,
            .reuses_existing_rule_slot = true,
            .performs_rb_replace_node = true,
            .would_release_previous_rule = true,
            .would_release_previous_object_reference = materialization_plan.key_type == .inode,
            .resulting_num_rules = search_plan.resulting_num_rules,
        };
    }

    pub fn planRuleRelease(key_type: KeyType, rule_present: bool) RuleReleasePlan {
        return .{
            .anchor = descriptor().anchor,
            .key_type = key_type,
            .rule_present = rule_present,
            .may_sleep = true,
            .would_release_object_reference = rule_present and key_type == .inode,
            .would_free_rule_allocation = rule_present,
        };
    }

    pub fn planMergeTreeRuleReplay(key_type: KeyType, dst_num_layers: u16, source_rule: RulePlan) !TreeMergeReplayPlan {
        if (dst_num_layers == 0 or dst_num_layers > max_num_layers) {
            return error.InvalidLayer;
        }
        if (source_rule.num_layers != 1) {
            return error.InvalidMergeSourceRule;
        }

        const source_layer = source_rule.layers[0];
        if (source_layer.level != 0) {
            return error.InvalidMergeSourceLayer;
        }

        return .{
            .anchor = descriptor().anchor,
            .root = selectRoot(key_type),
            .key_type = key_type,
            .destination_layer = .{
                .level = dst_num_layers,
                .access = source_layer.access,
            },
            .source_rule_num_layers = source_rule.num_layers,
            .would_reuse_source_key = true,
            .would_call_insert_rule = true,
        };
    }

    pub fn planCapacityInvariants() CapacityInvariantPlan {
        return .{
            .anchor = descriptor().anchor,
            .rule_num_layers_fits_max_layers = std.math.maxInt(usize) >= max_num_layers,
            .creation_num_layers_fits_max_layers = std.math.maxInt(u32) >= max_num_layers,
            .layer_level_fits_max_layers = std.math.maxInt(u16) >= max_num_layers,
            .layer_access_carries_initially_denied_fs_access = std.math.maxInt(u32) >= initially_denied_fs_access,
            .ruleset_num_rules_reaches_max = max_num_rules == std.math.maxInt(u32),
            .rule_storage_slots_match_max_layers = std.mem.zeroes([max_num_layers]Layer).len == max_num_layers,
        };
    }

    pub fn planRuleInsertion(existing_rule: ?RulePlan, incoming_layers: []const Layer, current_num_rules: u32) !RuleInsertionPlan {
        if (existing_rule) |rule| {
            if (incoming_layers.len != 1) {
                return error.MatchingRuleRequiresSingleLayer;
            }

            const incoming = incoming_layers[0];
            var updated = rule;

            if (incoming.level == 0) {
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

            updated = try makeRulePlan(rule.layers[0..rule.num_layers], incoming);
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
            .resulting_rule = try makeRulePlan(incoming_layers, null),
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

        if (insertion_site == .root and search_plan.parent_key_data != null) {
            return error.UnexpectedParentNode;
        }
        if (insertion_site != .root and search_plan.parent_key_data == null) {
            return error.MissingParentNode;
        }

        return .{
            .anchor = descriptor().anchor,
            .root = search_plan.root,
            .mode = mode,
            .parent_key_data = search_plan.parent_key_data,
            .performs_rb_link_node = true,
            .performs_rb_insert_color = true,
            .resulting_num_rules = search_plan.resulting_num_rules,
        };
    }

    pub fn planRuleLookup(key_type: KeyType, root_present: bool, search_key_data: u64, walker_keys: []const u64) !RuleLookupPlan {
        var plan = RuleLookupPlan{
            .anchor = descriptor().anchor,
            .root = selectRoot(key_type),
            .search_depth = 0,
            .search_steps = [_]TreeSearchStep{.{ .node_key_data = 0, .direction = .left }} ** max_tree_search_depth,
            .found_existing_rule = false,
            .matched_key_data = null,
        };

        if (!root_present) {
            if (walker_keys.len != 0) {
                return error.UnexpectedWalkerPath;
            }
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
                plan.found_existing_rule = true;
                plan.matched_key_data = walker_key;
                return plan;
            }
        }

        return plan;
    }
};

test "landlock ruleset merge tree replay planner stays data-only" {
    const source_rule = RulePlan{
        .num_layers = 1,
        .layers = [_]Layer{.{ .level = 0, .access = 0x5 }} ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 1)),
    };

    const plan = try RulesetHelperLab.planMergeTreeRuleReplay(.net_port, 2, source_rule);
    try std.testing.expectEqualStrings("security/landlock/ruleset.c", plan.anchor);
    try std.testing.expectEqual(TreeRoot.net_port, plan.root);
    try std.testing.expectEqual(KeyType.net_port, plan.key_type);
    try std.testing.expectEqual(@as(u16, 2), plan.destination_layer.level);
    try std.testing.expectEqual(@as(u32, 0x5), plan.destination_layer.access);
    try std.testing.expectEqual(@as(usize, 1), plan.source_rule_num_layers);
    try std.testing.expect(plan.would_reuse_source_key);
    try std.testing.expect(plan.would_call_insert_rule);
}

test "landlock ruleset merge tree replay planner rejects non-single-level sources" {
    const multi_layer_source = RulePlan{
        .num_layers = 2,
        .layers = [_]Layer{
            .{ .level = 0, .access = 0x1 },
            .{ .level = 1, .access = 0x2 },
        } ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 2)),
    };
    try std.testing.expectError(error.InvalidMergeSourceRule, RulesetHelperLab.planMergeTreeRuleReplay(.inode, 2, multi_layer_source));

    const leveled_source = RulePlan{
        .num_layers = 1,
        .layers = [_]Layer{.{ .level = 1, .access = 0x3 }} ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 1)),
    };
    try std.testing.expectError(error.InvalidMergeSourceLayer, RulesetHelperLab.planMergeTreeRuleReplay(.inode, 2, leveled_source));
    try std.testing.expectError(error.InvalidLayer, RulesetHelperLab.planMergeTreeRuleReplay(.inode, 0, source_ruleWithZeroLevel()));
}

fn source_ruleWithZeroLevel() RulePlan {
    return .{
        .num_layers = 1,
        .layers = [_]Layer{.{ .level = 0, .access = 0x3 }} ++ ([_]Layer{.{ .level = 0, .access = 0 }} ** (max_num_layers - 1)),
    };
}
