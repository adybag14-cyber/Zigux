const std = @import("std");
const runtime_loader = @import("runtime_loader_contract.zig");

pub fn requestStateFor(plan: runtime_loader.LoadPlan) runtime_loader.RequestState {
    if (!plan.requires_runtime_substrate) return .released_without_substrate;
    if (!plan.init_flow.readyForRuntimeLoad()) return .waiting_on_runtime_substrate;
    return .prepared;
}

fn basePlan() runtime_loader.LoadPlan {
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

test "requestStateFor derives prepared only after the runtime substrate is ready" {
    const initialized_ready = basePlan();
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, requestStateFor(initialized_ready));

    var selftest_ready = initialized_ready;
    selftest_ready.init_flow = .{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 1,
        .exit_runs = 0,
    };
    try std.testing.expectEqual(runtime_loader.RequestState.prepared, requestStateFor(selftest_ready));

    var missing_init = initialized_ready;
    missing_init.init_flow.init_runs = 0;
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        requestStateFor(missing_init),
    );

    var duplicate_selftest = initialized_ready;
    duplicate_selftest.init_flow = .{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 2,
        .exit_runs = 0,
    };
    try std.testing.expectEqual(
        runtime_loader.RequestState.waiting_on_runtime_substrate,
        requestStateFor(duplicate_selftest),
    );
}

test "requestStateFor releases plans that do not require the runtime substrate" {
    var plan = basePlan();
    plan.requires_runtime_substrate = false;
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, requestStateFor(plan));

    plan.init_flow = .{
        .handoff_stage = .selftest_complete,
        .init_runs = 0,
        .selftest_runs = 7,
        .exit_runs = 3,
    };
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, requestStateFor(plan));
}

test "request-state derivation stays outside the shared load-plan record" {
    try std.testing.expect(@hasField(runtime_loader.LoadPlan, "requires_runtime_substrate"));
    try std.testing.expect(@hasField(runtime_loader.LoadPlan, "init_flow"));
    try std.testing.expect(!@hasField(runtime_loader.LoadPlan, "request_state"));
}
