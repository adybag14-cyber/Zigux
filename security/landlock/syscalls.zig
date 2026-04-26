const std = @import("std");

pub const page_size_limit: usize = 4096;
pub const abi_version: u32 = 9;

pub const create_ruleset_version_flag: u32 = 1 << 0;
pub const create_ruleset_errata_flag: u32 = 1 << 1;

pub const restrict_self_log_same_exec_off: u32 = 1 << 0;
pub const restrict_self_log_new_exec_on: u32 = 1 << 1;
pub const restrict_self_log_subdomains_off: u32 = 1 << 2;
pub const restrict_self_tsync: u32 = 1 << 3;

pub const rule_type_path_beneath: u32 = 1;
pub const rule_type_net_port: u32 = 2;

pub const fmode_can_read: u32 = 1 << 0;
pub const fmode_can_write: u32 = 1 << 1;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_abi_shape_reporting: bool,
    provides_create_ruleset_query_planning: bool,
    provides_restrict_self_flag_planning: bool,
    provides_add_rule_planning: bool,
    provides_ruleset_fd_planning: bool,
    touches_live_fd_table: bool,
    touches_live_paths: bool,
    touches_live_credentials: bool,
    touches_live_domains: bool,
};

pub const RulesetAttr = struct {
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    scoped: u64 = 0,
};

pub const PathBeneathAttr = struct {
    allowed_access: u64 = 0,
    parent_fd: i32 = -1,
};

pub const NetPortAttr = struct {
    allowed_access: u64 = 0,
    port: u64 = 0,
};

pub const AbiShapeReport = struct {
    anchor: []const u8,
    ruleset_attr_size: usize,
    min_ruleset_attr_size: usize,
    path_beneath_attr_size: usize,
    net_port_attr_size: usize,
    page_size_limit: usize,
};

pub const CreateRulesetAction = enum {
    create,
    abi_version_query,
    errata_query,
};

pub const CreateRulesetRequest = struct {
    attr_present: bool = true,
    size: usize = @sizeOf(RulesetAttr),
    flags: u32 = 0,
    attr: RulesetAttr = .{},
    allowed_fs_mask: u64,
    allowed_net_mask: u64,
    allowed_scope_mask: u64,
    errata_value: u32 = 0,
};

pub const CreateRulesetPlan = struct {
    anchor: []const u8,
    action: CreateRulesetAction,
    returned_value: u32 = 0,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    scoped: u64 = 0,
};

pub const RestrictSelfPlan = struct {
    anchor: []const u8,
    requires_ruleset: bool,
    log_same_exec: bool,
    log_new_exec: bool,
    log_subdomains: bool,
    propagates_to_siblings: bool,
};

pub const AddRuleAction = enum {
    path_beneath,
    net_port,
};

pub const AddRuleRequest = struct {
    flags: u32 = 0,
    rule_type: u32,
    handled_access_fs: u64 = 0,
    handled_access_net: u64 = 0,
    path_beneath_attr: PathBeneathAttr = .{},
    net_port_attr: NetPortAttr = .{},
};

pub const AddRulePlan = struct {
    anchor: []const u8,
    action: AddRuleAction,
    allowed_access: u64,
    requires_ruleset_write_access: bool,
    requires_path_lookup: bool,
    parent_fd: i32 = -1,
    port: ?u16 = null,
};

pub const RulesetFdAccess = enum {
    read,
    write,
};

pub const RulesetFdRequest = struct {
    fd_present: bool = true,
    file_is_ruleset: bool = true,
    file_mode: u32 = fmode_can_read | fmode_can_write,
    required_access: RulesetFdAccess,
    num_layers: u32 = 1,
};

pub const RulesetFdPlan = struct {
    anchor: []const u8,
    required_access: RulesetFdAccess,
    validates_ruleset_type: bool,
    validates_single_layer_ruleset: bool,
    requires_owned_ruleset_ref: bool,
};

pub const SyscallsHelperLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "landlock_syscalls_helper_lab",
            .anchor = "security/landlock/syscalls.c",
            .provides_abi_shape_reporting = true,
            .provides_create_ruleset_query_planning = true,
            .provides_restrict_self_flag_planning = true,
            .provides_add_rule_planning = true,
            .provides_ruleset_fd_planning = true,
            .touches_live_fd_table = false,
            .touches_live_paths = false,
            .touches_live_credentials = false,
            .touches_live_domains = false,
        };
    }

    pub fn reportAbiShapes() AbiShapeReport {
        comptime {
            if (@sizeOf(RulesetAttr) != 24) {
                @compileError("landlock_ruleset_attr size drift");
            }
            if (@sizeOf(NetPortAttr) != 16) {
                @compileError("landlock_net_port_attr size drift");
            }
        }

        return .{
            .anchor = descriptor().anchor,
            .ruleset_attr_size = @sizeOf(RulesetAttr),
            .min_ruleset_attr_size = @offsetOf(RulesetAttr, "handled_access_fs") + @sizeOf(u64),
            .path_beneath_attr_size = 12,
            .net_port_attr_size = @sizeOf(NetPortAttr),
            .page_size_limit = page_size_limit,
        };
    }

    pub fn planCreateRuleset(request: CreateRulesetRequest) !CreateRulesetPlan {
        if (request.flags != 0) {
            if (request.attr_present or request.size != 0) {
                return error.InvalidQueryArguments;
            }

            if (request.flags == create_ruleset_version_flag) {
                return .{
                    .anchor = descriptor().anchor,
                    .action = .abi_version_query,
                    .returned_value = abi_version,
                };
            }

            if (request.flags == create_ruleset_errata_flag) {
                return .{
                    .anchor = descriptor().anchor,
                    .action = .errata_query,
                    .returned_value = request.errata_value,
                };
            }

            return error.UnsupportedFlags;
        }

        if (!request.attr_present) {
            return error.MissingAttr;
        }

        const abi_shapes = reportAbiShapes();
        if (request.size < abi_shapes.min_ruleset_attr_size) {
            return error.StructTooSmall;
        }
        if (request.size > abi_shapes.page_size_limit) {
            return error.StructTooLarge;
        }

        if ((request.attr.handled_access_fs | request.allowed_fs_mask) != request.allowed_fs_mask) {
            return error.InvalidFsAccessMask;
        }
        if ((request.attr.handled_access_net | request.allowed_net_mask) != request.allowed_net_mask) {
            return error.InvalidNetAccessMask;
        }
        if ((request.attr.scoped | request.allowed_scope_mask) != request.allowed_scope_mask) {
            return error.InvalidScopeMask;
        }
        if (request.attr.handled_access_fs == 0 and request.attr.handled_access_net == 0 and request.attr.scoped == 0) {
            return error.EmptyRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .action = .create,
            .handled_access_fs = request.attr.handled_access_fs,
            .handled_access_net = request.attr.handled_access_net,
            .scoped = request.attr.scoped,
        };
    }

    pub fn planRestrictSelf(ruleset_fd: i32, flags: u32) !RestrictSelfPlan {
        const allowed_flags = restrict_self_log_same_exec_off |
            restrict_self_log_new_exec_on |
            restrict_self_log_subdomains_off |
            restrict_self_tsync;
        if ((flags | allowed_flags) != allowed_flags) {
            return error.InvalidFlags;
        }

        const mute_subdomains_only = ruleset_fd == -1 and
            (flags & ~restrict_self_tsync) == restrict_self_log_subdomains_off;
        if (ruleset_fd == -1 and !mute_subdomains_only) {
            return error.MissingRuleset;
        }

        return .{
            .anchor = descriptor().anchor,
            .requires_ruleset = !mute_subdomains_only,
            .log_same_exec = (flags & restrict_self_log_same_exec_off) == 0,
            .log_new_exec = (flags & restrict_self_log_new_exec_on) != 0,
            .log_subdomains = (flags & restrict_self_log_subdomains_off) == 0,
            .propagates_to_siblings = (flags & restrict_self_tsync) != 0,
        };
    }

    pub fn planAddRule(request: AddRuleRequest) !AddRulePlan {
        if (request.flags != 0) {
            return error.InvalidFlags;
        }

        switch (request.rule_type) {
            rule_type_path_beneath => {
                if (request.path_beneath_attr.allowed_access == 0) {
                    return error.EmptyAccess;
                }
                if ((request.path_beneath_attr.allowed_access | request.handled_access_fs) != request.handled_access_fs) {
                    return error.InvalidPathAccessMask;
                }

                return .{
                    .anchor = descriptor().anchor,
                    .action = .path_beneath,
                    .allowed_access = request.path_beneath_attr.allowed_access,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = true,
                    .parent_fd = request.path_beneath_attr.parent_fd,
                };
            },
            rule_type_net_port => {
                if (request.net_port_attr.allowed_access == 0) {
                    return error.EmptyAccess;
                }
                if ((request.net_port_attr.allowed_access | request.handled_access_net) != request.handled_access_net) {
                    return error.InvalidNetAccessMask;
                }
                if (request.net_port_attr.port > std.math.maxInt(u16)) {
                    return error.PortTooLarge;
                }

                return .{
                    .anchor = descriptor().anchor,
                    .action = .net_port,
                    .allowed_access = request.net_port_attr.allowed_access,
                    .requires_ruleset_write_access = true,
                    .requires_path_lookup = false,
                    .port = @intCast(request.net_port_attr.port),
                };
            },
            else => return error.InvalidRuleType,
        }
    }

    pub fn planGetRulesetFromFd(request: RulesetFdRequest) !RulesetFdPlan {
        const required_mode = switch (request.required_access) {
            .read => fmode_can_read,
            .write => fmode_can_write,
        };

        if (!request.fd_present) {
            return error.MissingFd;
        }
        if (!request.file_is_ruleset) {
            return error.InvalidRulesetFd;
        }
        if ((request.file_mode & required_mode) == 0) {
            return error.InsufficientAccessMode;
        }
        if (request.num_layers != 1) {
            return error.InvalidRulesetLayers;
        }

        return .{
            .anchor = descriptor().anchor,
            .required_access = request.required_access,
            .validates_ruleset_type = true,
            .validates_single_layer_ruleset = true,
            .requires_owned_ruleset_ref = true,
        };
    }
};