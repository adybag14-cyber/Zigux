const std = @import("std");

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
    maxactive_budget,
    missed_summary,
    ownership_and_lifetime,
};

pub const sample_review_focus = [_]SampleFocus{
    .symbol_selection,
    .entry_timestamp,
    .private_data_shape,
    .return_duration,
    .maxactive_budget,
    .missed_summary,
    .ownership_and_lifetime,
};

pub const sample_review_non_goals = [_][]const u8{
    "register_kretprobe parity",
    "unregister_kretprobe parity",
    "pt_regs or regs_return_value parity",
    "loadable module wiring",
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
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

pub const RetargetRecoverySummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    skipped_kernel_thread_path_checked: bool,
    rejected_timestamp_ns: i64,
    return_value: usize,
    duration_ns: i64,
    private_data_size_bytes: usize,
    maxactive: usize,
    stage_after_recovery: SampleStage,
};

pub const MaxactiveBudgetSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    budget_before_init: usize,
    budget_after_init: usize,
    replay_budget: usize,
    budget_after_replay: usize,
    missed_instances: usize,
    replay_runs: usize,
    stage_after_replay: SampleStage,
};

pub const OwnershipBoundarySummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    armed_exit_rejected: bool,
    rejected_timestamp_ns: i64,
    recovered_duration_ns: i64,
    stage_after_exit: SampleStage,
    exit_runs: usize,
    post_exit_record_missed_rejected: bool,
    post_exit_entry_rejected: bool,
    post_exit_ret_rejected: bool,
};

pub const LifecycleGuardSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    stage_before_init: SampleStage,
    stage_after_init: SampleStage,
    pre_init_anchor_rejected: bool,
    pre_init_exit_rejected: bool,
    double_init_rejected: bool,
    post_init_retarget_rejected: bool,
    post_init_recovery_rejected: bool,
    init_runs: usize,
};

pub const KretprobeExampleSample = struct {
    const Self = @This();
    const InstanceData = struct {
        entry_stamp_ns: i64 = -1,
    };

    pub const default_symbol_name = "kernel_clone";
    pub const default_maxactive: usize = 20;

    stage_state: SampleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
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
            .anchor = "samples/kprobes/kretprobe_example.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn privateDataSizeBytes(_: *const Self) usize {
        return @sizeOf(InstanceData);
    }

    pub fn maxactiveBudget(_: *const Self) usize {
        return default_maxactive;
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
            .maxactive = self.maxactiveBudget(),
            .checked_focus = reviewContract().focus,
        };
    }

    pub fn runRetargetRecoveryReplay(self: *Self) !RetargetRecoverySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.retargetSymbol("do_sys_openat2");
        try self.init();

        const skipped = try self.entryHandler(false, 11);
        if (skipped) return error.UnexpectedEntryArming;

        const armed = try self.entryHandler(true, 200);
        if (!armed) return error.UnexpectedEntrySkip;

        _ = self.retHandler(9, 199) catch |err| switch (err) {
            error.InvalidTimestampOrder => {},
            else => return err,
        };
        const recovered = try self.retHandler(9, 260);

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .skipped_kernel_thread_path_checked = self.skipped_kernel_threads == 1,
            .rejected_timestamp_ns = 199,
            .return_value = recovered.retval,
            .duration_ns = recovered.duration_ns,
            .private_data_size_bytes = self.privateDataSizeBytes(),
            .maxactive = self.maxactiveBudget(),
            .stage_after_recovery = self.stage(),
        };
    }

    pub fn runMaxactiveBudgetReplay(self: *Self) !MaxactiveBudgetSummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const budget_before_init = self.maxactiveBudget();
        try self.init();
        const budget_after_init = self.maxactiveBudget();
        const replay = try self.runAnchorReplay();

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .budget_before_init = budget_before_init,
            .budget_after_init = budget_after_init,
            .replay_budget = replay.maxactive,
            .budget_after_replay = self.maxactiveBudget(),
            .missed_instances = self.nmissed,
            .replay_runs = self.replay_runs,
            .stage_after_replay = self.stage(),
        };
    }

    pub fn runOwnershipBoundaryReplay(self: *Self) !OwnershipBoundarySummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.init();
        const armed = try self.entryHandler(true, 200);
        if (!armed) return error.UnexpectedEntrySkip;

        var armed_exit_rejected = false;
        self.exit() catch |err| switch (err) {
            error.OutstandingProbeInstance => armed_exit_rejected = true,
            else => return err,
        };
        if (!armed_exit_rejected) return error.ExpectedOutstandingProbeInstance;

        _ = self.retHandler(9, 199) catch |err| switch (err) {
            error.InvalidTimestampOrder => {},
            else => return err,
        };
        const recovered = try self.retHandler(9, 260);
        try self.exit();

        var post_exit_record_missed_rejected = false;
        if (self.recordMissedInstance()) |_| {
            return error.ExpectedPostExitRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => post_exit_record_missed_rejected = true,
        }

        var post_exit_entry_rejected = false;
        if (self.entryHandler(true, 300)) |_| {
            return error.ExpectedPostExitRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => post_exit_entry_rejected = true,
            else => return err,
        }

        var post_exit_ret_rejected = false;
        if (self.retHandler(11, 360)) |_| {
            return error.ExpectedPostExitRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => post_exit_ret_rejected = true,
            else => return err,
        }

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .armed_exit_rejected = armed_exit_rejected,
            .rejected_timestamp_ns = 199,
            .recovered_duration_ns = recovered.duration_ns,
            .stage_after_exit = self.stage(),
            .exit_runs = self.exit_runs,
            .post_exit_record_missed_rejected = post_exit_record_missed_rejected,
            .post_exit_entry_rejected = post_exit_entry_rejected,
            .post_exit_ret_rejected = post_exit_ret_rejected,
        };
    }

    pub fn runLifecycleGuardReplay(self: *Self) !LifecycleGuardSummary {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var pre_init_anchor_rejected = false;
        if (self.runAnchorReplay()) |_| {
            return error.ExpectedLifecycleGuardRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_anchor_rejected = true,
            else => return err,
        }

        var pre_init_exit_rejected = false;
        if (self.exit()) |_| {
            return error.ExpectedLifecycleGuardRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_exit_rejected = true,
            else => return err,
        }

        try self.init();

        var double_init_rejected = false;
        if (self.init()) |_| {
            return error.ExpectedLifecycleGuardRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => double_init_rejected = true,
            else => return err,
        }

        var post_init_retarget_rejected = false;
        if (self.retargetSymbol("do_sys_openat2")) |_| {
            return error.ExpectedLifecycleGuardRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => post_init_retarget_rejected = true,
            else => return err,
        }

        var post_init_recovery_rejected = false;
        if (self.runRetargetRecoveryReplay()) |_| {
            return error.ExpectedLifecycleGuardRejection;
        } else |err| switch (err) {
            error.InvalidLifecycleTransition => post_init_recovery_rejected = true,
            else => return err,
        }

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .stage_before_init = .cold,
            .stage_after_init = self.stage(),
            .pre_init_anchor_rejected = pre_init_anchor_rejected,
            .pre_init_exit_rejected = pre_init_exit_rejected,
            .double_init_rejected = double_init_rejected,
            .post_init_retarget_rejected = post_init_retarget_rejected,
            .post_init_recovery_rejected = post_init_recovery_rejected,
            .init_runs = self.init_runs,
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

test "kretprobe sample descriptor and anchor replay stay reviewable" {
    const expected_focus = sample_review_focus;
    const expected_non_goals = sample_review_non_goals;
    const descriptor = KretprobeExampleSample.descriptor();
    const contract = KretprobeExampleSample.reviewContract();

    var sample = KretprobeExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("kretprobe_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);

    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(sample.maxactiveBudget(), replay.maxactive);
    try std.testing.expectEqual(@as(usize, expected_focus.len), replay.checked_focus.len);
    for (expected_focus, replay.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
}

test "kretprobe sample keeps retarget recovery and timestamp boundaries explicit" {
    var sample = KretprobeExampleSample{};

    try std.testing.expectError(error.InvalidLifecycleTransition, sample.entryHandler(true, 100));
    try std.testing.expectError(error.InvalidSymbolName, sample.retargetSymbol(""));

    const recovered = try sample.runRetargetRecoveryReplay();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", recovered.anchor);
    try std.testing.expectEqualStrings("do_sys_openat2", recovered.symbol_name);
    try std.testing.expect(recovered.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(i64, 199), recovered.rejected_timestamp_ns);
    try std.testing.expectEqual(@as(usize, 9), recovered.return_value);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), recovered.private_data_size_bytes);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, recovered.maxactive);
    try std.testing.expectEqual(SampleStage.initialized, recovered.stage_after_recovery);
    try std.testing.expectEqualStrings("do_sys_openat2", sample.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), sample.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 9), sample.last_retval);
    try std.testing.expectEqual(@as(i64, 60), sample.last_duration_ns);
    try std.testing.expectEqual(@as(i64, -1), sample.instance_data.entry_stamp_ns);

    try sample.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), sample.nmissed);
}

test "kretprobe sample keeps the maxactive budget fixed across replay" {
    var sample = KretprobeExampleSample{};
    const maxactive = try sample.runMaxactiveBudgetReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", maxactive.anchor);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, maxactive.symbol_name);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, maxactive.budget_before_init);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, maxactive.budget_after_init);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, maxactive.replay_budget);
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, maxactive.budget_after_replay);
    try std.testing.expectEqual(@as(usize, 1), maxactive.missed_instances);
    try std.testing.expectEqual(@as(usize, 1), maxactive.replay_runs);
    try std.testing.expectEqual(SampleStage.replay_complete, maxactive.stage_after_replay);
}

test "kretprobe sample keeps lifecycle guard transitions explicit" {
    var sample = KretprobeExampleSample{};
    const lifecycle_guards = try sample.runLifecycleGuardReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", lifecycle_guards.anchor);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, lifecycle_guards.symbol_name);
    try std.testing.expectEqual(SampleStage.cold, lifecycle_guards.stage_before_init);
    try std.testing.expectEqual(SampleStage.initialized, lifecycle_guards.stage_after_init);
    try std.testing.expect(lifecycle_guards.pre_init_anchor_rejected);
    try std.testing.expect(lifecycle_guards.pre_init_exit_rejected);
    try std.testing.expect(lifecycle_guards.double_init_rejected);
    try std.testing.expect(lifecycle_guards.post_init_retarget_rejected);
    try std.testing.expect(lifecycle_guards.post_init_recovery_rejected);
    try std.testing.expectEqual(@as(usize, 1), lifecycle_guards.init_runs);
}

test "kretprobe sample keeps ownership and post-exit boundaries explicit" {
    var sample = KretprobeExampleSample{};
    try std.testing.expectEqual(KretprobeExampleSample.default_maxactive, sample.maxactiveBudget());
    try std.testing.expectEqual(SampleStage.cold, sample.stage());

    const replay = try sample.runOwnershipBoundaryReplay();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expect(replay.armed_exit_rejected);
    try std.testing.expectEqual(@as(i64, 199), replay.rejected_timestamp_ns);
    try std.testing.expectEqual(@as(i64, 60), replay.recovered_duration_ns);
    try std.testing.expectEqual(SampleStage.exited, replay.stage_after_exit);
    try std.testing.expectEqual(@as(usize, 1), replay.exit_runs);
    try std.testing.expect(replay.post_exit_record_missed_rejected);
    try std.testing.expect(replay.post_exit_entry_rejected);
    try std.testing.expect(replay.post_exit_ret_rejected);

    try std.testing.expectEqual(SampleStage.exited, sample.stage());
    try std.testing.expectEqual(@as(usize, 1), sample.init_runs);
    try std.testing.expectEqual(@as(usize, 1), sample.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), sample.active_instances);
    try std.testing.expectEqual(@as(i64, -1), sample.instance_data.entry_stamp_ns);
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.recordMissedInstance());
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.entryHandler(true, 300));
    try std.testing.expectError(error.InvalidLifecycleTransition, sample.retHandler(11, 360));
}
