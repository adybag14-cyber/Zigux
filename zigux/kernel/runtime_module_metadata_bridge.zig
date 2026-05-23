const std = @import("std");

pub const PublicationState = enum(u8) {
    metadata_only,
    install_root_pending,
    depmod_pending,
};

pub const PilotModuleIdentity = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
};

pub const ModuleMetadata = struct {
    license: []const u8,
    description: []const u8,
    aliases: []const []const u8,
};

pub const DepmodPublicationPlan = struct {
    install_root: []const u8,
    modules_alias_path: []const u8,
    modules_dep_path: []const u8,
    modules_order_path: []const u8,
    module_symvers_path: []const u8,
    state: PublicationState,
};

pub const ModuleMetadataBridge = struct {
    identity: PilotModuleIdentity,
    metadata: ModuleMetadata,
    depmod: DepmodPublicationPlan,
};

const approved_pilot_families = [_]PilotModuleIdentity{
    .{
        .module_name = "runtime_atomic64",
        .anchor = "lib/atomic64_test.c",
        .entry_symbol = "zigux_runtime_atomic64_init",
        .exit_symbol = "zigux_runtime_atomic64_exit",
    },
    .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
    },
    .{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit",
    },
    .{
        .module_name = "runtime_kretprobe",
        .anchor = "samples/kprobes/kretprobe_example.c",
        .entry_symbol = "zigux_runtime_kretprobe_init",
        .exit_symbol = "zigux_runtime_kretprobe_exit",
    },
};

fn eqlStringSlices(actual: []const []const u8, expected: []const []const u8) bool {
    if (actual.len != expected.len) return false;

    for (actual, expected) |actual_entry, expected_entry| {
        if (!std.mem.eql(u8, actual_entry, expected_entry)) return false;
    }

    return true;
}

pub fn keepsApprovedPilotFamilyIdentity(identity: PilotModuleIdentity) bool {
    for (approved_pilot_families) |family| {
        if (std.mem.eql(u8, identity.module_name, family.module_name) and
            std.mem.eql(u8, identity.anchor, family.anchor) and
            std.mem.eql(u8, identity.entry_symbol, family.entry_symbol) and
            std.mem.eql(u8, identity.exit_symbol, family.exit_symbol))
        {
            return true;
        }
    }

    return false;
}

pub fn keepsModuleMetadataExplicit(bridge: ModuleMetadataBridge) bool {
    if (!keepsApprovedPilotFamilyIdentity(bridge.identity)) return false;
    if (bridge.metadata.license.len == 0) return false;
    if (bridge.metadata.description.len == 0) return false;
    if (bridge.metadata.aliases.len == 0) return false;

    for (bridge.metadata.aliases) |alias| {
        if (alias.len == 0) return false;
        if (!std.mem.startsWith(u8, alias, "zigux:")) return false;
    }

    return true;
}

pub fn keepsBlockedPublicationExplicit(bridge: ModuleMetadataBridge) bool {
    if (!keepsModuleMetadataExplicit(bridge)) return false;

    return switch (bridge.depmod.state) {
        .metadata_only => bridge.depmod.install_root.len == 0 and
            bridge.depmod.modules_alias_path.len == 0 and
            bridge.depmod.modules_dep_path.len == 0 and
            bridge.depmod.modules_order_path.len == 0 and
            bridge.depmod.module_symvers_path.len == 0,
        .install_root_pending => bridge.depmod.install_root.len != 0 and
            bridge.depmod.modules_alias_path.len == 0 and
            bridge.depmod.modules_dep_path.len == 0 and
            bridge.depmod.modules_order_path.len == 0 and
            bridge.depmod.module_symvers_path.len == 0,
        .depmod_pending => bridge.depmod.install_root.len != 0 and
            bridge.depmod.modules_alias_path.len != 0 and
            bridge.depmod.modules_dep_path.len != 0 and
            bridge.depmod.modules_order_path.len != 0 and
            bridge.depmod.module_symvers_path.len != 0,
    };
}

pub fn keepsBridgeExplicit(actual: ModuleMetadataBridge, expected: ModuleMetadataBridge) bool {
    return std.mem.eql(u8, actual.identity.module_name, expected.identity.module_name) and
        std.mem.eql(u8, actual.identity.anchor, expected.identity.anchor) and
        std.mem.eql(u8, actual.identity.entry_symbol, expected.identity.entry_symbol) and
        std.mem.eql(u8, actual.identity.exit_symbol, expected.identity.exit_symbol) and
        std.mem.eql(u8, actual.metadata.license, expected.metadata.license) and
        std.mem.eql(u8, actual.metadata.description, expected.metadata.description) and
        eqlStringSlices(actual.metadata.aliases, expected.metadata.aliases) and
        std.mem.eql(u8, actual.depmod.install_root, expected.depmod.install_root) and
        std.mem.eql(u8, actual.depmod.modules_alias_path, expected.depmod.modules_alias_path) and
        std.mem.eql(u8, actual.depmod.modules_dep_path, expected.depmod.modules_dep_path) and
        std.mem.eql(u8, actual.depmod.modules_order_path, expected.depmod.modules_order_path) and
        std.mem.eql(u8, actual.depmod.module_symvers_path, expected.depmod.module_symvers_path) and
        actual.depmod.state == expected.depmod.state;
}

test "approved pilot families stay bounded to the roadmap-backed Phase 9 anchors" {
    for (approved_pilot_families) |family| {
        try std.testing.expect(keepsApprovedPilotFamilyIdentity(family));
    }

    const drifted = PilotModuleIdentity{
        .module_name = "runtime_trace_events",
        .anchor = "samples/trace_events/trace-events-sample.c",
        .entry_symbol = "zigux_runtime_trace_events_init",
        .exit_symbol = "zigux_runtime_trace_events_exit_drift",
    };
    try std.testing.expect(!keepsApprovedPilotFamilyIdentity(drifted));
}

test "module metadata bridge keeps staged depmod publication explicit without claiming publication is complete" {
    const bridge = ModuleMetadataBridge{
        .identity = .{
            .module_name = "runtime_trace_events",
            .anchor = "samples/trace_events/trace-events-sample.c",
            .entry_symbol = "zigux_runtime_trace_events_init",
            .exit_symbol = "zigux_runtime_trace_events_exit",
        },
        .metadata = .{
            .license = "GPL-2.0",
            .description = "Phase 9 runtime pilot trace-events module metadata sidecar",
            .aliases = &.{
                "zigux:runtime:trace-events",
                "zigux:phase9:pilot",
            },
        },
        .depmod = .{
            .install_root = "lib/modules/zigux-phase9",
            .modules_alias_path = "lib/modules/zigux-phase9/modules.alias",
            .modules_dep_path = "lib/modules/zigux-phase9/modules.dep",
            .modules_order_path = "lib/modules/zigux-phase9/modules.order",
            .module_symvers_path = "lib/modules/zigux-phase9/Module.symvers",
            .state = .depmod_pending,
        },
    };

    try std.testing.expect(keepsModuleMetadataExplicit(bridge));
    try std.testing.expect(keepsBlockedPublicationExplicit(bridge));
    try std.testing.expect(keepsBridgeExplicit(bridge, bridge));
}

test "metadata and staged publication checks reject empty aliases and path drift" {
    var bridge = ModuleMetadataBridge{
        .identity = .{
            .module_name = "runtime_bitmap",
            .anchor = "lib/test_bitmap.c",
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
        },
        .metadata = .{
            .license = "GPL-2.0",
            .description = "Phase 9 runtime bitmap metadata sidecar",
            .aliases = &.{"zigux:runtime:bitmap"},
        },
        .depmod = .{
            .install_root = "lib/modules/zigux-phase9",
            .modules_alias_path = "lib/modules/zigux-phase9/modules.alias",
            .modules_dep_path = "lib/modules/zigux-phase9/modules.dep",
            .modules_order_path = "lib/modules/zigux-phase9/modules.order",
            .module_symvers_path = "lib/modules/zigux-phase9/Module.symvers",
            .state = .depmod_pending,
        },
    };

    try std.testing.expect(keepsBlockedPublicationExplicit(bridge));

    bridge.metadata.aliases = &.{""};
    try std.testing.expect(!keepsModuleMetadataExplicit(bridge));

    bridge.metadata.aliases = &.{"zigux:runtime:bitmap"};
    bridge.depmod.modules_dep_path = "";
    try std.testing.expect(!keepsBlockedPublicationExplicit(bridge));
}