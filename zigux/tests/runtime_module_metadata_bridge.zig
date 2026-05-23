const std = @import("std");
const bridge = @import("runtime_module_metadata_bridge");

fn runtimeTraceEventsBridge() bridge.ModuleMetadataBridge {
    return .{
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
}

fn runtimeBitmapBridge() bridge.ModuleMetadataBridge {
    return .{
        .identity = .{
            .module_name = "runtime_bitmap",
            .anchor = "lib/test_bitmap.c",
            .entry_symbol = "zigux_runtime_bitmap_init",
            .exit_symbol = "zigux_runtime_bitmap_exit",
        },
        .metadata = .{
            .license = "GPL-2.0",
            .description = "Phase 9 runtime bitmap module metadata sidecar",
            .aliases = &.{
                "zigux:runtime:bitmap",
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
}

test "Phase 9 bridge packets stay anchored to the current runtime pilot families" {
    const trace_events = runtimeTraceEventsBridge();
    const bitmap = runtimeBitmapBridge();

    try std.testing.expect(bridge.keepsApprovedPilotFamilyIdentity(trace_events.identity));
    try std.testing.expect(bridge.keepsApprovedPilotFamilyIdentity(bitmap.identity));
    try std.testing.expectEqualStrings(
        "samples/trace_events/trace-events-sample.c",
        trace_events.identity.anchor,
    );
    try std.testing.expectEqualStrings("lib/test_bitmap.c", bitmap.identity.anchor);
    try std.testing.expectEqualStrings(
        "zigux_runtime_trace_events_init",
        trace_events.identity.entry_symbol,
    );
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", bitmap.identity.exit_symbol);
}

test "Phase 9 bridge packets keep metadata and depmod staging explicit without claiming publication completion" {
    const trace_events = runtimeTraceEventsBridge();
    const bitmap = runtimeBitmapBridge();

    try std.testing.expect(bridge.keepsModuleMetadataExplicit(trace_events));
    try std.testing.expect(bridge.keepsModuleMetadataExplicit(bitmap));
    try std.testing.expect(bridge.keepsBlockedPublicationExplicit(trace_events));
    try std.testing.expect(bridge.keepsBlockedPublicationExplicit(bitmap));
    try std.testing.expectEqual(bridge.PublicationState.depmod_pending, trace_events.depmod.state);
    try std.testing.expectEqual(bridge.PublicationState.depmod_pending, bitmap.depmod.state);
}

test "Phase 9 bridge packets preserve exact staged metadata snapshots" {
    const trace_events = runtimeTraceEventsBridge();
    var drifted = runtimeTraceEventsBridge();

    try std.testing.expect(bridge.keepsBridgeExplicit(trace_events, trace_events));

    drifted.depmod.modules_alias_path = "lib/modules/zigux-phase9/modules.alias.drift";
    try std.testing.expect(!bridge.keepsBridgeExplicit(drifted, trace_events));
}