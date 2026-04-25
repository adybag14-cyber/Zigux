const std = @import("std");

pub const max_num_layers: usize = 16;
pub const initially_denied_fs_access: u32 = 1 << 13;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_ruleset_creation_planning: bool,
    provides_union_access_masks: bool,
    provides_layer_mask_init: bool,
    provides_rule_unmasking: bool,
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

pub const LayerMaskPlan = struct {
    anchor: []const u8,
    handled_accesses: u32,
    masks: [max_num_layers]u32,
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
};
