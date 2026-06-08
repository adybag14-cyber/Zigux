const std = @import("std");
const runtime_loader = @import("runtime_loader_contract");

const LoadPlan = runtime_loader.LoadPlan;

fn stablePlan() LoadPlan {
    return .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

test "runtime loader LoadPlan keeps the shared Phase 3 request fields explicit" {
    const required_fields = [_][]const u8{
        "module_name",
        "anchor",
        "entry_symbol",
        "exit_symbol",
        "requires_runtime_substrate",
        "provides_selftest_hook",
        "module_metadata",
        "allocator_handoff",
        "init_flow",
    };

    inline for (required_fields) |field| {
        try std.testing.expect(@hasField(LoadPlan, field));
    }

    const plan = stablePlan();
    try std.testing.expect(runtime_loader.keepsLoadPlanExplicit(plan, plan));
    try std.testing.expect(plan.init_flow.readyForRuntimeLoad());
}

test "runtime loader LoadPlan excludes Phase 8 command and environment controls" {
    const blocked_fields = [_][]const u8{
        "activation_env",
        "argv_policy",
        "command_env",
        "command_name",
        "exec_name",
        "exec_path",
        "exec_path_env",
    };

    inline for (blocked_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}

test "runtime loader LoadPlan excludes registration and initcall metadata surfaces" {
    const blocked_fields = [_][]const u8{
        "register_api",
        "unregister_api",
        "summary",
        "registration_snapshot",
        "module_init",
        "module_exit",
        "initcall",
        "exitcall",
    };

    inline for (blocked_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}

test "runtime loader LoadPlan excludes publication outputs and install-root paths" {
    const blocked_fields = [_][]const u8{
        "modinfo",
        "module_alias",
        "modules_alias_path",
        "module_install_root",
        "modules_order_path",
        "modules_builtin_path",
        "module_symvers_path",
        "depmod_script",
        "depmod_manifest",
    };

    inline for (blocked_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}
