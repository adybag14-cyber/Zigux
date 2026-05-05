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
};
