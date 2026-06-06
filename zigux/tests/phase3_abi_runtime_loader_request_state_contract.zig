const std = @import("std");
const runtime_loader_contract = @import("runtime_loader_contract");

const LoadPlan = runtime_loader_contract.LoadPlan;
const RequestState = runtime_loader_contract.RequestState;

fn runtimeBitmapPlan(requires_runtime_substrate: bool, init_flow: runtime_loader_contract.InitFlow) LoadPlan {
    return .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = requires_runtime_substrate,
        .provides_selftest_hook = true,
        .module_metadata = .{
            .license = "GPL",
            .aliases = &.{"zigux:runtime-pilot:runtime_bitmap"},
        },
        .allocator_handoff = .arena,
        .init_flow = init_flow,
    };
}

fn requestStateFor(plan: LoadPlan, runtime_substrate_ready: bool) RequestState {
    if (!plan.init_flow.readyForRuntimeLoad()) return .prepared;
    if (!plan.requires_runtime_substrate) return .released_without_substrate;
    if (!runtime_substrate_ready) return .waiting_on_runtime_substrate;
    return .prepared;
}

test "RequestState keeps stable ABI byte tags" {
    try std.testing.expectEqual(@as(u8, 0), @intFromEnum(RequestState.prepared));
    try std.testing.expectEqual(@as(u8, 1), @intFromEnum(RequestState.waiting_on_runtime_substrate));
    try std.testing.expectEqual(@as(u8, 2), @intFromEnum(RequestState.released_without_substrate));
}

test "runtime substrate requirement routes request state before release" {
    const ready_flow = runtime_loader_contract.InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 1,
        .selftest_runs = 0,
        .exit_runs = 0,
    };

    const substrate_plan = runtimeBitmapPlan(true, ready_flow);
    try std.testing.expectEqual(
        RequestState.waiting_on_runtime_substrate,
        requestStateFor(substrate_plan, false),
    );
    try std.testing.expectEqual(
        RequestState.prepared,
        requestStateFor(substrate_plan, true),
    );

    const no_substrate_plan = runtimeBitmapPlan(false, ready_flow);
    try std.testing.expectEqual(
        RequestState.released_without_substrate,
        requestStateFor(no_substrate_plan, false),
    );
    try std.testing.expectEqual(
        RequestState.released_without_substrate,
        requestStateFor(no_substrate_plan, true),
    );
}

test "unready init flow keeps request prepared instead of widening release" {
    const missing_init = runtime_loader_contract.InitFlow{
        .handoff_stage = .initialized,
        .init_runs = 0,
        .selftest_runs = 0,
        .exit_runs = 0,
    };
    const duplicate_selftest = runtime_loader_contract.InitFlow{
        .handoff_stage = .selftest_complete,
        .init_runs = 1,
        .selftest_runs = 2,
        .exit_runs = 0,
    };

    try std.testing.expectEqual(
        RequestState.prepared,
        requestStateFor(runtimeBitmapPlan(true, missing_init), false),
    );
    try std.testing.expectEqual(
        RequestState.prepared,
        requestStateFor(runtimeBitmapPlan(false, duplicate_selftest), true),
    );
}

test "LoadPlan keeps request state out of the shared handoff body" {
    const blocked_request_fields = [_][]const u8{
        "request_state",
        "runtime_substrate_ready",
        "prepared",
        "waiting_on_runtime_substrate",
        "released_without_substrate",
    };

    inline for (blocked_request_fields) |field| {
        try std.testing.expect(!@hasField(LoadPlan, field));
    }
}
