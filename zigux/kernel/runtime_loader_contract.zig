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

pub const PreparedRequest = struct {
    plan: LoadPlan,
    prepared_plan: LoadPlan,
    state: RequestState,
};

pub const blocked_command_fields = [_][]const u8{
    "command",
    "command_name",
    "argv_policy",
    "exec_path",
};

pub const blocked_environment_fields = [_][]const u8{
    "environment",
    "activation_env",
    "perf_exec_path",
    "path_env",
    "lines_env",
    "columns_env",
};

pub const blocked_registration_summary_fields = [_][]const u8{
    "register_api",
    "unregister_api",
    "summary",
    "registration_snapshot",
};

pub const blocked_publication_fields = [_][]const u8{
    "modinfo",
    "module_alias",
    "module_aliases",
    "modules_alias_path",
    "module_install_root",
    "modules_order_path",
    "modules_builtin_path",
    "module_symvers_path",
};

pub const blocked_depmod_fields = [_][]const u8{
    "depmod_script",
    "depmod_manifest",
    "depmod_aliases",
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

fn typeDeclaresAnyField(comptime T: type, comptime field_names: []const []const u8) bool {
    inline for (field_names) |field_name| {
        if (@hasField(T, field_name)) return true;
    }
    return false;
}

fn requestBoundaryDeclaresAnyField(comptime field_names: []const []const u8) bool {
    return typeDeclaresAnyField(LoadPlan, field_names) or
        typeDeclaresAnyField(PreparedRequest, field_names);
}

pub fn keepsCommandBoundaryExplicit() bool {
    return !requestBoundaryDeclaresAnyField(&blocked_command_fields);
}

pub fn keepsEnvironmentBoundaryExplicit() bool {
    return !requestBoundaryDeclaresAnyField(&blocked_environment_fields);
}

pub fn keepsRegistrationSummaryBoundaryExplicit() bool {
    return !requestBoundaryDeclaresAnyField(&blocked_registration_summary_fields);
}

pub fn keepsPublicationBoundaryExplicit() bool {
    return !requestBoundaryDeclaresAnyField(&blocked_publication_fields);
}

pub fn keepsDepmodBoundaryExplicit() bool {
    return !requestBoundaryDeclaresAnyField(&blocked_depmod_fields);
}

pub fn keepsReviewOnlyControlBoundaryExplicit() bool {
    return keepsCommandBoundaryExplicit() and
        keepsEnvironmentBoundaryExplicit() and
        keepsRegistrationSummaryBoundaryExplicit() and
        keepsPublicationBoundaryExplicit() and
        keepsDepmodBoundaryExplicit();
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

test "shared runtime loader contract keeps command and environment surfaces outside the request contract" {
    try std.testing.expect(keepsCommandBoundaryExplicit());
    try std.testing.expect(keepsEnvironmentBoundaryExplicit());
    try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_command_fields));
    try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_command_fields));
    try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_environment_fields));
    try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_environment_fields));

    try std.testing.expectEqual(@as(usize, 4), blocked_command_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_command_fields[0], "command"));
    try std.testing.expect(std.mem.eql(u8, blocked_command_fields[1], "command_name"));
    try std.testing.expect(std.mem.eql(u8, blocked_command_fields[2], "argv_policy"));
    try std.testing.expect(std.mem.eql(u8, blocked_command_fields[3], "exec_path"));

    try std.testing.expectEqual(@as(usize, 6), blocked_environment_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[0], "environment"));
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[1], "activation_env"));
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[2], "perf_exec_path"));
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[3], "path_env"));
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[4], "lines_env"));
    try std.testing.expect(std.mem.eql(u8, blocked_environment_fields[5], "columns_env"));
}

test "shared runtime loader contract keeps registration-summary, publication, and depmod surfaces outside the request contract" {
    try std.testing.expect(keepsRegistrationSummaryBoundaryExplicit());
    try std.testing.expect(keepsPublicationBoundaryExplicit());
    try std.testing.expect(keepsDepmodBoundaryExplicit());
    try std.testing.expect(keepsReviewOnlyControlBoundaryExplicit());
    try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_registration_summary_fields));
    try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_registration_summary_fields));
    try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_publication_fields));
    try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_publication_fields));
    try std.testing.expect(!typeDeclaresAnyField(LoadPlan, &blocked_depmod_fields));
    try std.testing.expect(!typeDeclaresAnyField(PreparedRequest, &blocked_depmod_fields));

    try std.testing.expectEqual(@as(usize, 4), blocked_registration_summary_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_registration_summary_fields[0], "register_api"));
    try std.testing.expect(std.mem.eql(u8, blocked_registration_summary_fields[1], "unregister_api"));
    try std.testing.expect(std.mem.eql(u8, blocked_registration_summary_fields[2], "summary"));
    try std.testing.expect(std.mem.eql(u8, blocked_registration_summary_fields[3], "registration_snapshot"));

    try std.testing.expectEqual(@as(usize, 8), blocked_publication_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[0], "modinfo"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[1], "module_alias"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[2], "module_aliases"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[3], "modules_alias_path"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[4], "module_install_root"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[5], "modules_order_path"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[6], "modules_builtin_path"));
    try std.testing.expect(std.mem.eql(u8, blocked_publication_fields[7], "module_symvers_path"));

    try std.testing.expectEqual(@as(usize, 3), blocked_depmod_fields.len);
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_fields[0], "depmod_script"));
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_fields[1], "depmod_manifest"));
    try std.testing.expect(std.mem.eql(u8, blocked_depmod_fields[2], "depmod_aliases"));
}
