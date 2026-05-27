const std = @import("std");

pub const linux_anchor = "samples/kprobes/kretprobe_example.c";

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    armed,
    replay_complete,
    exited,
};

pub const SampleFocus = enum {
    symbol_selection,
    entry_timestamp,
    private_data_shape,
    return_duration,
    missed_summary,
    ownership_and_lifetime,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const ProbeResult = struct {
    retval: usize,
    duration_ns: i64,
};

pub const ReplaySummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    stage_before_replay: SampleStage,
    stage_after_replay: SampleStage,
    skipped_kernel_thread_path_checked: bool,
    private_data_size_bytes: usize,
    return_value: usize,
    duration_ns: i64,
    nmissed: usize,
    maxactive: usize,
    checked_focus: []const SampleFocus,
};

pub const InstanceBudgetContract = struct {
    anchor: []const u8,
    symbol_param_name: []const u8,
    symbol_param_mode: u16,
    default_symbol_name: []const u8,
    private_data_word_bytes: usize,
    default_maxactive: usize,
    reports_return_value_and_duration: bool,
    skips_kernel_threads_without_mm: bool,
    nmissed_suggests_increasing_maxactive: bool,
};

pub const OwnershipSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    stage: SampleStage,
    maxactive: usize,
    active_instances: usize,
    skipped_kernel_threads: usize,
    nmissed: usize,
    init_runs: usize,
    replay_runs: usize,
    exit_runs: usize,
    entry_timestamp_armed: bool,
};

pub const OwnershipReplaySummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    stage_snapshots: [5]OwnershipSummary,
    skipped_kernel_thread_path_checked: bool,
    replay_return_value: usize,
    replay_duration_ns: i64,
};

pub const ContributorRoutePacket = struct {
    sample_selfcheck_route: []const u8,
    focused_replay_route: []const u8,
    survey_guard_route: []const u8,
    instance_budget_companion_route: []const u8,
    instance_budget_focused_route: []const u8,
    probe_spec_companion_route: []const u8,
    probe_spec_focused_route: []const u8,
    shared_build_route: []const u8,
};

pub const sample_selfcheck_route = "zig test samples/zigux/kretprobe_example.zig";
pub const focused_replay_route =
    "zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig";
pub const survey_guard_route = "zig test zigux/tests/phase5_kretprobe_example_survey.zig";
pub const instance_budget_companion_route =
    "zig test samples/zigux/kretprobe_example_instance_budget_contract.zig";
pub const instance_budget_focused_route =
    "zig test --dep kretprobe_example_instance_budget_contract -Mroot=zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig -Mkretprobe_example_instance_budget_contract=samples/zigux/kretprobe_example_instance_budget_contract.zig";
pub const probe_spec_companion_route =
    "zig test samples/zigux/kretprobe_example_probe_spec.zig";
pub const probe_spec_focused_route =
    "zig test --dep kretprobe_example_probe_spec -Mroot=zigux/tests/phase5_kretprobe_example_probe_spec.zig -Mkretprobe_example_probe_spec=samples/zigux/kretprobe_example_probe_spec.zig";
pub const shared_build_route = "zig build test --build-file zigux/tests/phase5_build.zig";

pub const KretprobeExampleSample = struct {
    const Self = @This();
    const InstanceData = struct {
        entry_stamp_ns: i64 = -1,
    };

    pub const symbol_param_name = "func";
    pub const symbol_param_mode: u16 = 0o644;
    pub const default_symbol_name = "kernel_clone";
    pub const default_maxactive: usize = 20;

    pub const sample_review_focus = [_]SampleFocus{
        .symbol_selection,
        .entry_timestamp,
        .private_data_shape,
        .return_duration,
        .missed_summary,
        .ownership_and_lifetime,
    };

    pub const sample_review_non_goals = [_][]const u8{
        "register_kretprobe parity",
        "unregister_kretprobe parity",
        "pt_regs or regs_return_value parity",
        "loadable module wiring",
    };

    stage_state: SampleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
    maxactive: usize = default_maxactive,
    active_instances: usize = 0,
    skipped_kernel_threads: usize = 0,
    nmissed: usize = 0,
    instance_data: InstanceData = .{},
    last_retval: usize = 0,
    last_duration_ns: i64 = 0,
    init_runs: usize = 0,
    replay_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "kretprobe_example",
            .anchor = linux_anchor,
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = sample_review_focus[0..],
            .non_goals = sample_review_non_goals[0..],
        };
    }

    pub fn contributorRoutePacket() ContributorRoutePacket {
        return .{
            .sample_selfcheck_route = sample_selfcheck_route,
            .focused_replay_route = focused_replay_route,
            .survey_guard_route = survey_guard_route,
            .instance_budget_companion_route = instance_budget_companion_route,
            .instance_budget_focused_route = instance_budget_focused_route,
            .probe_spec_companion_route = probe_spec_companion_route,
            .probe_spec_focused_route = probe_spec_focused_route,
            .shared_build_route = shared_build_route,
        };
    }

    pub fn instanceBudgetContract() InstanceBudgetContract {
        return .{
            .anchor = linux_anchor,
            .symbol_param_name = symbol_param_name,
            .symbol_param_mode = symbol_param_mode,
            .default_symbol_name = default_symbol_name,
            .private_data_word_bytes = @sizeOf(InstanceData),
            .default_maxactive = default_maxactive,
            .reports_return_value_and_duration = true,
            .skips_kernel_threads_without_mm = true,
            .nmissed_suggests_increasing_maxactive = true,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn privateDataSizeBytes(_: *const Self) usize {
        return @sizeOf(InstanceData);
    }

    pub fn ownershipSummary(self: *const Self) OwnershipSummary {
        return .{
            .anchor = linux_anchor,
            .symbol_name = self.symbol_name,
            .stage = self.stage(),
            .maxactive = self.maxactive,
            .active_instances = self.active_instances,
            .skipped_kernel_threads = self.skipped_kernel_threads,
            .nmissed = self.nmissed,
            .init_runs = self.init_runs,
            .replay_runs = self.replay_runs,
            .exit_runs = self.exit_runs,
            .entry_timestamp_armed = self.instance_data.entry_stamp_ns >= 0,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (self.symbol_name.len == 0) return error.InvalidSymbolName;

        self.active_instances = 0;
        self.skipped_kernel_threads = 0;
        self.nmissed = 0;
        self.instance_data = .{};
        self.last_retval = 0;
        self.last_duration_ns = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn retargetSymbol(self: *Self, symbol_name: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (symbol_name.len == 0) return error.InvalidSymbolName;
        self.symbol_name = symbol_name;
    }

    pub fn retargetMaxactive(self: *Self, maxactive: usize) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (maxactive == 0) return error.InvalidMaxactive;
        self.maxactive = maxactive;
    }

    pub fn entryHandler(self: *Self, has_mm: bool, stamp_ns: i64) !bool {
        switch (self.stage()) {
            .initialized, .replay_complete, .armed => {},
            else => return error.InvalidLifecycleTransition,
        }

        if (!has_mm) {
            self.skipped_kernel_threads += 1;
            return false;
        }
        if (self.active_instances >= 1) return error.OutstandingProbeInstance;

        self.active_instances = 1;
        self.instance_data.entry_stamp_ns = stamp_ns;
        self.stage_state = .armed;
        return true;
    }

    pub fn retHandler(self: *Self, retval: usize, now_ns: i64) !ProbeResult {
        if (self.stage() != .armed) return error.InvalidLifecycleTransition;
        if (self.instance_data.entry_stamp_ns < 0 or self.active_instances == 0) return error.MissingEntryTimestamp;
        if (now_ns < self.instance_data.entry_stamp_ns) return error.InvalidTimestampOrder;

        const duration_ns = now_ns - self.instance_data.entry_stamp_ns;
        self.active_instances = 0;
        self.instance_data = .{};
        self.last_retval = retval;
        self.last_duration_ns = duration_ns;
        self.stage_state = .initialized;
        return .{
            .retval = retval,
            .duration_ns = duration_ns,
        };
    }

    pub fn recordMissedInstance(self: *Self) !void {
        return switch (self.stage()) {
            .initialized, .replay_complete => self.nmissed += 1,
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn runOwnershipReplay(self: *Self) !OwnershipReplaySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const cold_summary = self.ownershipSummary();

        try self.init();
        const initialized_summary = self.ownershipSummary();

        const skipped = try self.entryHandler(false, 11);
        if (skipped) return error.UnexpectedEntryArming;

        const armed = try self.entryHandler(true, 100);
        if (!armed) return error.UnexpectedEntrySkip;
        const armed_summary = self.ownershipSummary();

        const result = try self.retHandler(42, 175);
        try self.recordMissedInstance();
        self.replay_runs += 1;
        self.stage_state = .replay_complete;
        const replay_complete_summary = self.ownershipSummary();

        try self.exit();
        const exited_summary = self.ownershipSummary();

        return .{
            .anchor = linux_anchor,
            .symbol_name = self.symbol_name,
            .stage_snapshots = .{
                cold_summary,
                initialized_summary,
                armed_summary,
                replay_complete_summary,
                exited_summary,
            },
            .skipped_kernel_thread_path_checked = replay_complete_summary.skipped_kernel_threads == 1,
            .replay_return_value = result.retval,
            .replay_duration_ns = result.duration_ns,
        };
    }

    pub fn runAnchorReplay(self: *Self) !ReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const skipped = try self.entryHandler(false, 10);
        if (skipped) return error.UnexpectedEntryArming;

        const armed = try self.entryHandler(true, 100);
        if (!armed) return error.UnexpectedEntrySkip;

        const result = try self.retHandler(42, 175);
        try self.recordMissedInstance();

        self.replay_runs += 1;
        self.stage_state = .replay_complete;
        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .stage_before_replay = .initialized,
            .stage_after_replay = .replay_complete,
            .skipped_kernel_thread_path_checked = self.skipped_kernel_threads == 1,
            .private_data_size_bytes = self.privateDataSizeBytes(),
            .return_value = result.retval,
            .duration_ns = result.duration_ns,
            .nmissed = self.nmissed,
            .maxactive = self.maxactive,
            .checked_focus = reviewContract().focus,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .replay_complete => {},
            .armed => return error.OutstandingProbeInstance,
            else => return error.InvalidLifecycleTransition,
        }

        self.active_instances = 0;
        self.instance_data = .{};
        self.last_retval = 0;
        self.last_duration_ns = 0;
        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "kretprobe sample replay keeps the anchor reviewable and non-runtime" {
    const contract = KretprobeExampleSample.reviewContract();
    var sample = KretprobeExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings(linux_anchor, replay.anchor);
    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(@as(usize, 20), replay.maxactive);
    try std.testing.expectEqual(@as(usize, contract.focus.len), replay.checked_focus.len);
    for (contract.focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(@as(usize, 4), contract.non_goals.len);
    try std.testing.expectEqualStrings("register_kretprobe parity", contract.non_goals[0]);
    try std.testing.expectEqualStrings("unregister_kretprobe parity", contract.non_goals[1]);
    try std.testing.expectEqualStrings("pt_regs or regs_return_value parity", contract.non_goals[2]);
    try std.testing.expectEqualStrings("loadable module wiring", contract.non_goals[3]);
}

test "kretprobe sample exports the live instance-budget contract" {
    const contract = KretprobeExampleSample.instanceBudgetContract();

    try std.testing.expectEqualStrings(linux_anchor, contract.anchor);
    try std.testing.expectEqualStrings("func", contract.symbol_param_name);
    try std.testing.expectEqual(@as(u16, 0o644), contract.symbol_param_mode);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, contract.default_symbol_name);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), contract.private_data_word_bytes);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, contract.default_maxactive);
    try std.testing.expect(contract.reports_return_value_and_duration);
    try std.testing.expect(contract.skips_kernel_threads_without_mm);
    try std.testing.expect(contract.nmissed_suggests_increasing_maxactive);
}

test "kretprobe sample keeps contributor review routes explicit" {
    const routes = KretprobeExampleSample.contributorRoutePacket();

    try std.testing.expectEqualStrings(sample_selfcheck_route, routes.sample_selfcheck_route);
    try std.testing.expectEqualStrings(focused_replay_route, routes.focused_replay_route);
    try std.testing.expectEqualStrings(survey_guard_route, routes.survey_guard_route);
    try std.testing.expectEqualStrings(instance_budget_companion_route, routes.instance_budget_companion_route);
    try std.testing.expectEqualStrings(instance_budget_focused_route, routes.instance_budget_focused_route);
    try std.testing.expectEqualStrings(probe_spec_companion_route, routes.probe_spec_companion_route);
    try std.testing.expectEqualStrings(probe_spec_focused_route, routes.probe_spec_focused_route);
    try std.testing.expectEqualStrings(shared_build_route, routes.shared_build_route);
}

test "kretprobe sample keeps maxactive tuning pre-init and reviewable" {
    var sample = KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidMaxactive, sample.retargetMaxactive(0));
    try sample.retargetMaxactive(3);
    try sample.init();

    const replay = try sample.runAnchorReplay();
    try std.testing.expectEqual(@as(usize, 3), sample.maxactive);
    try std.testing.expectEqual(@as(usize, 3), replay.maxactive);
    try std.testing.expectEqual(@as(usize, 1), sample.replay_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.retargetMaxactive(4));
}

test "kretprobe sample ownership replay keeps lifecycle snapshots explicit" {
    var sample = KretprobeExampleSample{};
    const replay = try sample.runOwnershipReplay();

    try std.testing.expectEqualStrings(linux_anchor, replay.anchor);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expectEqual(SampleStage.cold, replay.stage_snapshots[0].stage);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_snapshots[1].stage);
    try std.testing.expectEqual(SampleStage.armed, replay.stage_snapshots[2].stage);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_snapshots[3].stage);
    try std.testing.expectEqual(SampleStage.exited, replay.stage_snapshots[4].stage);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].active_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[2].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[3].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[4].active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[0].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), replay.stage_snapshots[1].skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].skipped_kernel_threads);
    try std.testing.expect(replay.stage_snapshots[2].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[3].entry_timestamp_armed);
    try std.testing.expect(!replay.stage_snapshots[4].entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[1].init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].replay_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[4].exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.stage_snapshots[3].nmissed);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, 42), replay.replay_return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.replay_duration_ns);
    try std.testing.expectEqual(SampleStage.exited, sample.stage());
}
