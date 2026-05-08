const std = @import("std");
const runtime_bitmap_sample = @import("runtime_bitmap_sample");
const runtime_bitmap_loader = @import("runtime_bitmap_loader");
const runtime_loader = @import("runtime_loader");

pub const PendingBindingStage = enum(u8) {
    idle,
    captured,
    released,
};

pub const PendingBindingSnapshot = struct {
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: runtime_loader.AllocatorHandoff,
    shared_handoff_stage: runtime_loader.HandoffStage,
    provides_selftest_hook: bool,
    selftest_runs: usize,
    first_set: u32,
    first_zero: u32,
    weight: u32,
    nbits: u32,
};

fn snapshotFrom(
    plan: runtime_bitmap_loader.RuntimeBitmapLoadPlan,
    shared_plan: runtime_loader.LoadPlan,
) PendingBindingSnapshot {
    return .{
        .module_name = plan.module_name,
        .anchor = plan.anchor,
        .entry_symbol = plan.entry_symbol,
        .exit_symbol = plan.exit_symbol,
        .allocator_handoff = shared_plan.allocator_handoff,
        .shared_handoff_stage = shared_plan.init_flow.handoff_stage,
        .provides_selftest_hook = shared_plan.provides_selftest_hook,
        .selftest_runs = shared_plan.init_flow.selftest_runs,
        .first_set = plan.summary.first_set,
        .first_zero = plan.summary.first_zero,
        .weight = plan.summary.weight,
        .nbits = plan.summary.nbits,
    };
}

pub const PendingRuntimeBitmapBinding = struct {
    const Self = @This();

    stage_state: PendingBindingStage = .idle,
    cached_plan: ?runtime_bitmap_loader.RuntimeBitmapLoadPlan = null,
    cached_shared_plan: ?runtime_loader.LoadPlan = null,

    pub fn stage(self: *const Self) PendingBindingStage {
        return self.stage_state;
    }

    pub fn captureWaitingRequest(
        self: *Self,
        loader: *const runtime_bitmap_loader.RuntimeBitmapLoader,
        shared_request: *const runtime_loader.PreparedRequest,
    ) !PendingBindingSnapshot {
        if (self.stage_state != .idle) return error.BindingAlreadyCaptured;
        if (loader.stage() != .waiting_on_runtime_substrate) return error.InvalidLoaderState;
        if (shared_request.state != .waiting_on_runtime_substrate) return error.InvalidLoaderState;

        const plan = loader.cached_plan orelse return error.MissingLoadPlan;
        if (!runtime_bitmap_loader.keepsSharedLoadPlanSnapshotExplicit(plan, shared_request.plan)) {
            return error.SharedLoadPlanDrift;
        }

        self.cached_plan = plan;
        self.cached_shared_plan = shared_request.plan;
        self.stage_state = .captured;
        return snapshotFrom(plan, shared_request.plan);
    }

    pub fn release(self: *Self) !PendingBindingSnapshot {
        if (self.stage_state != .captured) return error.InvalidBindingState;

        const plan = self.cached_plan orelse return error.MissingLoadPlan;
        const shared_plan = self.cached_shared_plan orelse return error.MissingLoadPlan;
        self.stage_state = .released;
        return snapshotFrom(plan, shared_plan);
    }
};

test "runtime bitmap pending binding captures the waiting shared request without claiming a live substrate" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = runtime_bitmap_loader.RuntimeBitmapLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    const pending_plan = try loader.requestSharedRuntimeLoad(&shared_request);

    var binding = PendingRuntimeBitmapBinding{};
    const captured = try binding.captureWaitingRequest(&loader, &shared_request);

    try std.testing.expectEqual(PendingBindingStage.captured, binding.stage());
    try std.testing.expectEqual(runtime_loader.RequestState.waiting_on_runtime_substrate, shared_request.state);
    try std.testing.expectEqualStrings("runtime_bitmap", captured.module_name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", captured.anchor);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_init", captured.entry_symbol);
    try std.testing.expectEqualStrings("zigux_runtime_bitmap_exit", captured.exit_symbol);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.arena, captured.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, captured.shared_handoff_stage);
    try std.testing.expect(captured.provides_selftest_hook);
    try std.testing.expectEqual(@as(usize, 1), captured.selftest_runs);
    try std.testing.expectEqual(@as(u32, 0), captured.first_set);
    try std.testing.expectEqual(@as(u32, 1), captured.first_zero);
    try std.testing.expectEqual(@as(u32, 4), captured.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, captured.nbits);
    try std.testing.expect(runtime_bitmap_loader.keepsSharedLoadPlanSnapshotExplicit(
        loader.cached_plan orelse unreachable,
        pending_plan,
    ));

    const released = try binding.release();
    try std.testing.expectEqual(PendingBindingStage.released, binding.stage());
    try std.testing.expectEqual(captured.first_set, released.first_set);
    try std.testing.expectEqual(captured.first_zero, released.first_zero);
    try std.testing.expectEqual(captured.weight, released.weight);

    try loader.releaseSharedWithoutSubstrate(&shared_request);
    try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);
}

test "runtime bitmap pending binding keeps initialized-stage handoff snapshots explicit" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    var loader = runtime_bitmap_loader.RuntimeBitmapLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);
    _ = try loader.requestSharedRuntimeLoad(&shared_request);

    var binding = PendingRuntimeBitmapBinding{};
    const captured = try binding.captureWaitingRequest(&loader, &shared_request);

    try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, captured.shared_handoff_stage);
    try std.testing.expectEqual(@as(usize, 0), captured.selftest_runs);
    try std.testing.expectEqual(@as(u32, 0), captured.first_set);
    try std.testing.expectEqual(@as(u32, 1), captured.first_zero);
    try std.testing.expectEqual(@as(u32, 4), captured.weight);
    try std.testing.expectEqual(runtime_bitmap_sample.RuntimeBitmapSample.bitmap_nbits, captured.nbits);
}

test "runtime bitmap pending binding rejects non-waiting or drifted shared requests" {
    var module = runtime_bitmap_sample.RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    var loader = runtime_bitmap_loader.RuntimeBitmapLoader{};
    var shared_request = try loader.prepareSharedRequest(&module);

    var premature = PendingRuntimeBitmapBinding{};
    try std.testing.expectError(
        error.InvalidLoaderState,
        premature.captureWaitingRequest(&loader, &shared_request),
    );
    try std.testing.expectEqual(PendingBindingStage.idle, premature.stage());

    _ = try loader.requestSharedRuntimeLoad(&shared_request);
    shared_request.plan.module_name = "runtime_bitmap_drift";

    var drifted = PendingRuntimeBitmapBinding{};
    try std.testing.expectError(
        error.SharedLoadPlanDrift,
        drifted.captureWaitingRequest(&loader, &shared_request),
    );
    try std.testing.expectEqual(PendingBindingStage.idle, drifted.stage());
}
