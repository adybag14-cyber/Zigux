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
    drifted.allocator_handoff = .caller_provided;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));
    drifted = stable;
    drifted.init_flow.selftest_runs = 1;
    try std.testing.expect(!keepsLoadPlanExplicit(drifted, stable));
}
