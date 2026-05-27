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

pub const AllocatorInitOwner = enum(u8) {
    caller_prepared,
    helper_owned,
    helper_owned_with_reset,
};

pub const AllocatorRuntimeInitPolicy = struct {
    init_owner: AllocatorInitOwner,
    requires_explicit_caller: bool,
    permits_global_fallback: bool,
    initializes_owned_state: bool,
    requires_reset_on_init: bool,
};

pub fn allocatorRuntimeInitPolicyFor(
    handoff: AllocatorHandoff,
) AllocatorRuntimeInitPolicy {
    return switch (handoff) {
        .caller_provided => .{
            .init_owner = .caller_prepared,
            .requires_explicit_caller = true,
            .permits_global_fallback = false,
            .initializes_owned_state = false,
            .requires_reset_on_init = false,
        },
        .arena => .{
            .init_owner = .helper_owned_with_reset,
            .requires_explicit_caller = false,
            .permits_global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset_on_init = true,
        },
        .kernel_heap => .{
            .init_owner = .helper_owned,
            .requires_explicit_caller = false,
            .permits_global_fallback = true,
            .initializes_owned_state = true,
            .requires_reset_on_init = false,
        },
    };
}

pub fn keepsAllocatorRuntimeInitPolicyExplicit(
    actual: AllocatorRuntimeInitPolicy,
    expected: AllocatorRuntimeInitPolicy,
) bool {
    return actual.init_owner == expected.init_owner and
        actual.requires_explicit_caller == expected.requires_explicit_caller and
        actual.permits_global_fallback == expected.permits_global_fallback and
        actual.initializes_owned_state == expected.initializes_owned_state and
        actual.requires_reset_on_init == expected.requires_reset_on_init;
}

pub fn keepsAllocatorRuntimeInitPolicyConsistent(
    handoff: AllocatorHandoff,
    expected: AllocatorRuntimeInitPolicy,
) bool {
    return keepsAllocatorRuntimeInitPolicyExplicit(
        allocatorRuntimeInitPolicyFor(handoff),
        expected,
    );
}

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

    const duplicate_init = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 2,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expect(!duplicate_init.readyForRuntimeLoad());

    const initialized_selftest_drift = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    };
    try std.testing.expect(!initialized_selftest_drift.readyForRuntimeLoad());

    const initialized_exit_drift = InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 1,
    };
    try std.testing.expect(!initialized_exit_drift.readyForRuntimeLoad());

    const selftest_missing_hook_evidence = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    try std.testing.expect(!selftest_missing_hook_evidence.readyForRuntimeLoad());

    const selftest_duplicate_hook_evidence = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 2,
        .exit_runs = 0,
    };
    try std.testing.expect(!selftest_duplicate_hook_evidence.readyForRuntimeLoad());

    const selftest_duplicate_init = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 2,
        .selftest_runs = 1,
        .exit_runs = 0,
    };
    try std.testing.expect(!selftest_duplicate_init.readyForRuntimeLoad());

    const selftest_exit_drift = InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 1,
    };
    try std.testing.expect(!selftest_exit_drift.readyForRuntimeLoad());
}

test "allocatorRuntimeInitPolicyFor keeps allocator ownership and reset semantics explicit" {
    const caller_policy = AllocatorRuntimeInitPolicy{
        .init_owner = .caller_prepared,
        .requires_explicit_caller = true,
        .permits_global_fallback = false,
        .initializes_owned_state = false,
        .requires_reset_on_init = false,
    };
    const arena_policy = AllocatorRuntimeInitPolicy{
        .init_owner = .helper_owned_with_reset,
        .requires_explicit_caller = false,
        .permits_global_fallback = true,
        .initializes_owned_state = true,
        .requires_reset_on_init = true,
    };
    const heap_policy = AllocatorRuntimeInitPolicy{
        .init_owner = .helper_owned,
        .requires_explicit_caller = false,
        .permits_global_fallback = true,
        .initializes_owned_state = true,
        .requires_reset_on_init = false,
    };

    try std.testing.expect(keepsAllocatorRuntimeInitPolicyExplicit(
        allocatorRuntimeInitPolicyFor(.caller_provided),
        caller_policy,
    ));
    try std.testing.expect(keepsAllocatorRuntimeInitPolicyConsistent(
        .caller_provided,
        caller_policy,
    ));

    try std.testing.expect(keepsAllocatorRuntimeInitPolicyExplicit(
        allocatorRuntimeInitPolicyFor(.arena),
        arena_policy,
    ));
    try std.testing.expect(keepsAllocatorRuntimeInitPolicyConsistent(
        .arena,
        arena_policy,
    ));

    try std.testing.expect(keepsAllocatorRuntimeInitPolicyExplicit(
        allocatorRuntimeInitPolicyFor(.kernel_heap),
        heap_policy,
    ));
    try std.testing.expect(keepsAllocatorRuntimeInitPolicyConsistent(
        .kernel_heap,
        heap_policy,
    ));
}

test "keepsAllocatorRuntimeInitPolicyExplicit compares every derived runtime-init field" {
    const stable = allocatorRuntimeInitPolicyFor(.arena);

    try std.testing.expect(keepsAllocatorRuntimeInitPolicyExplicit(stable, stable));

    var drifted = stable;
    drifted.init_owner = .helper_owned;
    try std.testing.expect(!keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.requires_explicit_caller = true;
    try std.testing.expect(!keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.permits_global_fallback = false;
    try std.testing.expect(!keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.initializes_owned_state = false;
    try std.testing.expect(!keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));

    drifted = stable;
    drifted.requires_reset_on_init = false;
    try std.testing.expect(!keepsAllocatorRuntimeInitPolicyExplicit(drifted, stable));
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
    drifted.init_flow.selftest_runs = 1;
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

test "LoadPlan keeps Phase 8 command and environment control fields out of the shared request contract" {
    const blocked_control_fields = [_][]const u8{
        "activation_env",
        "argv_policy",
        "command_env",
        "command_name",
        "exec_name",
        "exec_path",
        "exec_path_env",
    };

    inline for (blocked_control_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}

test "LoadPlan keeps blocked registration-summary surfaces out of the shared request contract" {
    const blocked_registration_summary_fields = [_][]const u8{
        "register_api",
        "unregister_api",
        "summary",
        "registration_snapshot",
    };

    inline for (blocked_registration_summary_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}

test "LoadPlan keeps blocked initcall metadata surfaces out of the shared request contract" {
    const blocked_initcall_fields = [_][]const u8{
        "module_init",
        "module_exit",
        "initcall",
        "exitcall",
    };

    inline for (blocked_initcall_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}

test "LoadPlan keeps blocked publication and depmod surfaces out of the shared request contract" {
    const blocked_publication_fields = [_][]const u8{
        "modinfo",
        "module_alias",
        "module_aliases",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
        "depmod_aliases",
    };

    inline for (blocked_publication_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}
