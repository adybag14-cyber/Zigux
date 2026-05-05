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
    missed_summary,
    ownership_and_lifetime,
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

const sample_review_focus = [_]SampleFocus{
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
    "runtime module wiring",
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

pub const LifecycleGuardSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    stage_before_init: SampleStage,
    stage_after_init: SampleStage,
    pre_init_anchor_rejected: bool,
    pre_init_exit_rejected: bool,
    double_init_rejected: bool,
    post_init_retarget_rejected: bool,
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
            .maxactive = self.maxactive,
            .checked_focus = reviewContract().focus,
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

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .stage_before_init = .cold,
            .stage_after_init = self.stage(),
            .pre_init_anchor_rejected = pre_init_anchor_rejected,
            .pre_init_exit_rejected = pre_init_exit_rejected,
            .double_init_rejected = double_init_rejected,
            .post_init_retarget_rejected = post_init_retarget_rejected,
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

test "kretprobe sample review contract keeps focus and non-goals explicit" {
    const contract = KretprobeExampleSample.reviewContract();

    try std.testing.expectEqual(@as(usize, 6), contract.focus.len);
    try std.testing.expectEqual(SampleFocus.symbol_selection, contract.focus[0]);
    try std.testing.expectEqual(SampleFocus.entry_timestamp, contract.focus[1]);
    try std.testing.expectEqual(SampleFocus.private_data_shape, contract.focus[2]);
    try std.testing.expectEqual(SampleFocus.return_duration, contract.focus[3]);
    try std.testing.expectEqual(SampleFocus.missed_summary, contract.focus[4]);
    try std.testing.expectEqual(SampleFocus.ownership_and_lifetime, contract.focus[5]);

    try std.testing.expectEqual(@as(usize, 4), contract.non_goals.len);
    try std.testing.expectEqualStrings("register_kretprobe parity", contract.non_goals[0]);
    try std.testing.expectEqualStrings("unregister_kretprobe parity", contract.non_goals[1]);
    try std.testing.expectEqualStrings("pt_regs or regs_return_value parity", contract.non_goals[2]);
    try std.testing.expectEqualStrings("runtime module wiring", contract.non_goals[3]);
}

test "kretprobe sample replay keeps the anchor reviewable and non-runtime" {
    var sample = KretprobeExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings("kernel_clone", replay.symbol_name);
    try std.testing.expectEqual(SampleStage.initialized, replay.stage_before_replay);
    try std.testing.expectEqual(SampleStage.replay_complete, replay.stage_after_replay);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, @sizeOf(i64)), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(@as(usize, 20), replay.maxactive);
    try std.testing.expectEqual(@as(usize, 6), replay.checked_focus.len);
}
