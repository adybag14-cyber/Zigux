const std = @import("std");

pub const AllocatorHandoff = enum(u8) {
    caller_provided,
    arena,
    kernel_heap,
};

pub const HandoffStage = enum(u8) {
    initialized,
    selftest_complete,
};

pub const InitFlow = struct {
    handoff_stage: HandoffStage,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,

    pub fn readyForRuntimeLoad(self: InitFlow) bool {
        if (self.init_runs != 1) return false;
        if (self.exit_runs != 0) return false;

        return switch (self.handoff_stage) {
            .initialized => self.selftest_runs == 0,
            .selftest_complete => self.selftest_runs == 1,
        };
    }
};

pub const LoadPlan = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
    allocator_handoff: AllocatorHandoff,
    init_flow: InitFlow,
};

pub const RequestState = enum(u8) {
    prepared,
    waiting_on_runtime_substrate,
    released_without_substrate,
};

pub fn keepsLoadPlanExplicit(actual: LoadPlan, expected: LoadPlan) bool {
    return std.mem.eql(u8, actual.module_name, expected.module_name) and
        std.mem.eql(u8, actual.anchor, expected.anchor) and
        std.mem.eql(u8, actual.entry_symbol, expected.entry_symbol) and
        std.mem.eql(u8, actual.exit_symbol, expected.exit_symbol) and
        actual.requires_runtime_substrate == expected.requires_runtime_substrate and
        actual.provides_selftest_hook == expected.provides_selftest_hook and
        actual.allocator_handoff == expected.allocator_handoff and
        actual.init_flow.handoff_stage == expected.init_flow.handoff_stage and
        actual.init_flow.init_runs == expected.init_flow.init_runs and
        actual.init_flow.selftest_runs == expected.init_flow.selftest_runs and
        actual.init_flow.exit_runs == expected.init_flow.exit_runs;
}

fn keepsRequestContractBoundaryExplicit() bool {
    const blocked_request_control_fields = [_][]const u8{
        "command",
        "environment",
        "register_api",
        "unregister_api",
        "summary",
        "modinfo",
        "module_alias",
        "module_aliases",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "depmod_script",
        "depmod_manifest",
        "depmod_aliases",
    };

    inline for (blocked_request_control_fields) |field_name| {
        if (@hasField(LoadPlan, field_name)) return false;
    }

    return true;
}

test "InitFlow.readyForRuntimeLoad keeps the staged handoff rules explicit" {
    const initialized_ready = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expect(initialized_ready.readyForRuntimeLoad());

    const selftest_ready = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    };
    try std.testing.expect(selftest_ready.readyForRuntimeLoad());

    const missing_init = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 0,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expect(!missing_init.readyForRuntimeLoad());

    const initialized_selftest_drift = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    };
    try std.testing.expect(!initialized_selftest_drift.readyForRuntimeLoad());

    const selftest_missing_hook_evidence = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expect(!selftest_missing_hook_evidence.readyForRuntimeLoad());
}

test "keepsLoadPlanExplicit compares every shared handoff field" {
    const stable = LoadPlan{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };

    try std.testing.expect(keepsLoadPlanExplicit(stable, stable));

    var drifted = stable;
    drifted.module_name = "runtime_bitmap_drift";
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.anchor = "lib/test_bitmap_drift.c";
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.entry_symbol = "zigux_runtime_bitmap_init_drift";
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.exit_symbol = "zigux_runtime_bitmap_exit_drift";
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.requires_runtime_substrate = false;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.provides_selftest_hook = false;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.allocator_handoff = .caller_provided;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.init_flow.handoff_stage = .selftest_complete;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.init_flow.init_runs = 2;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));

    drifted = stable;
    drifted.init_flow.exit_runs = 1;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));
}

test "shared runtime loader contract keeps command, environment, registration-summary, depmod-facing, and study-only core-boundary control surfaces outside the request contract" {
    try std.testing.expect(keepsRequestContractBoundaryExplicit());

    const blocked_publication_markers = [_][]const u8{
        ".modinfo",
        "MODULE_ALIAS()",
        "modules.alias",
        "modules.order",
        "modules.builtin",
    };
    try std.testing.expectEqual(@as(usize, 5), blocked_publication_markers.len);
    try std.testing.expect(std.mem.eql(u8, blocked_publication_markers[0], ".modinfo"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_markers[1], "MODULE_ALIAS()"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_markers[2], "modules.alias"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_markers[3], "modules.order"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_markers[4], "modules.builtin"));

    const blocked_depmod_boundary_fields = [_][]const u8{
        "depmod_script",
        "depmod_manifest",
        "depmod_aliases",
    };
    try std.testing.expectEqual(@as(usize, 3), blocked_depmod_boundary_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_boundary_fields[0], "depmod_script"));
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_boundary_fields[1], "depmod_manifest"));
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_boundary_fields[2], "depmod_aliases"));
}
