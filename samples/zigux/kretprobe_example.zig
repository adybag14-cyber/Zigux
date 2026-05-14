const std = @import("std");

pub const SampleStage = enum(u8) {
    cold,
    initialized,
    armed,
    replay_complete,
    exited,
};

pub const SampleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selfcheck: bool,
};

pub const Snapshot = struct {
    stage: SampleStage,
    symbol_name: []const u8,
    active_instances: usize,
    entry_timestamp_armed: bool,
    init_runs: usize,
    replay_runs: usize,
    exit_runs: usize,
    last_duration_ns: i64,
};

pub const RetargetReplaySummary = struct {
    rejected_empty_symbol: bool,
    rejected_post_init_retarget: bool,
    symbol_name: []const u8,
    stage_after_init: SampleStage,
};

pub const AnchorReplaySummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    skipped_kernel_thread_path_checked: bool,
    private_data_size_bytes: usize,
    return_value: usize,
    duration_ns: i64,
    nmissed: usize,
    maxactive: usize,
};

pub const LifecycleGuardReplaySummary = struct {
    pre_init_anchor_rejected: bool,
    pre_init_exit_rejected: bool,
    double_init_rejected: bool,
    post_init_retarget_rejected: bool,
    stage_after_checks: SampleStage,
};

pub const OwnershipReplaySummary = struct {
    cold: Snapshot,
    initialized: Snapshot,
    armed: Snapshot,
    replay_complete: Snapshot,
    exited: Snapshot,
};

pub const RecoveryReplaySummary = struct {
    outstanding_instance_exit_rejected: bool,
    invalid_timestamp_order_rejected: bool,
    recovered_duration_ns: i64,
    post_exit_entry_rejected: bool,
    post_exit_ret_rejected: bool,
};

pub const KretprobeExampleSample = struct {
    const Self = @This();

    pub const default_symbol_name = "kernel_clone";
    pub const private_data_size_bytes: usize = 8;
    pub const maxactive_budget: usize = 20;

    stage_state: SampleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
    init_runs: usize = 0,
    replay_runs: usize = 0,
    exit_runs: usize = 0,
    active_instances: usize = 0,
    nmissed: usize = 0,
    skipped_kernel_threads: usize = 0,
    entry_timestamp_ns: i64 = 0,
    last_return_value: usize = 0,
    last_duration_ns: i64 = 0,

    pub fn descriptor() SampleDescriptor {
        return .{
            .name = "kretprobe_example",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .requires_runtime_substrate = false,
            .provides_selfcheck = true,
        };
    }

    pub fn stage(self: *const Self) SampleStage {
        return self.stage_state;
    }

    pub fn maxactiveBudget(_: *const Self) usize {
        return maxactive_budget;
    }

    pub fn snapshot(self: *const Self) Snapshot {
        return .{
            .stage = self.stage(),
            .symbol_name = self.symbol_name,
            .active_instances = self.active_instances,
            .entry_timestamp_armed = self.active_instances != 0,
            .init_runs = self.init_runs,
            .replay_runs = self.replay_runs,
            .exit_runs = self.exit_runs,
            .last_duration_ns = self.last_duration_ns,
        };
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        self.active_instances = 0;
        self.nmissed = 0;
        self.skipped_kernel_threads = 0;
        self.entry_timestamp_ns = 0;
        self.last_return_value = 0;
        self.last_duration_ns = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn retargetSymbol(self: *Self, symbol_name: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (symbol_name.len == 0) return error.InvalidSymbolName;
        self.symbol_name = symbol_name;
    }

    pub fn entryHandler(self: *Self, is_kernel_thread: bool, timestamp_ns: i64) !bool {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;
        if (is_kernel_thread) {
            self.skipped_kernel_threads += 1;
            return false;
        }
        self.active_instances = 1;
        self.entry_timestamp_ns = timestamp_ns;
        self.stage_state = .armed;
        return true;
    }

    pub fn recordMissedInstance(self: *Self) !void {
        return switch (self.stage()) {
            .initialized, .armed => self.nmissed += 1,
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn retHandler(self: *Self, return_value: usize, timestamp_ns: i64) !i64 {
        if (self.stage() != .armed) return error.InvalidLifecycleTransition;
        if (timestamp_ns < self.entry_timestamp_ns) return error.InvalidTimestampOrder;

        self.last_return_value = return_value;
        self.last_duration_ns = timestamp_ns - self.entry_timestamp_ns;
        self.active_instances = 0;
        self.entry_timestamp_ns = 0;
        self.replay_runs += 1;
        self.stage_state = .replay_complete;
        return self.last_duration_ns;
    }

    pub fn exit(self: *Self) !void {
        return switch (self.stage()) {
            .initialized, .replay_complete => {
                self.exit_runs += 1;
                self.stage_state = .exited;
            },
            .armed => error.OutstandingProbeInstance,
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn runRetargetReplay(self: *Self, symbol_name: []const u8) !RetargetReplaySummary {
        var rejected_empty_symbol = false;
        self.retargetSymbol("") catch |err| switch (err) {
            error.InvalidSymbolName => rejected_empty_symbol = true,
            else => return err,
        };

        try self.retargetSymbol(symbol_name);
        try self.init();

        var rejected_post_init_retarget = false;
        self.retargetSymbol("vfs_read") catch |err| switch (err) {
            error.InvalidLifecycleTransition => rejected_post_init_retarget = true,
            else => return err,
        };

        return .{
            .rejected_empty_symbol = rejected_empty_symbol,
            .rejected_post_init_retarget = rejected_post_init_retarget,
            .symbol_name = self.symbol_name,
            .stage_after_init = self.stage(),
        };
    }

    pub fn runAnchorReplay(self: *Self) !AnchorReplaySummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        _ = try self.entryHandler(true, 40);
        _ = try self.entryHandler(false, 100);
        try self.recordMissedInstance();
        const duration_ns = try self.retHandler(42, 175);

        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .skipped_kernel_thread_path_checked = self.skipped_kernel_threads == 1,
            .private_data_size_bytes = private_data_size_bytes,
            .return_value = self.last_return_value,
            .duration_ns = duration_ns,
            .nmissed = self.nmissed,
            .maxactive = self.maxactiveBudget(),
        };
    }

    pub fn runLifecycleGuardReplay(self: *Self) !LifecycleGuardReplaySummary {
        var pre_init_anchor_rejected = false;
        _ = self.runAnchorReplay() catch |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_anchor_rejected = true,
            else => return err,
        };

        var pre_init_exit_rejected = false;
        self.exit() catch |err| switch (err) {
            error.InvalidLifecycleTransition => pre_init_exit_rejected = true,
            else => return err,
        };

        try self.init();

        var double_init_rejected = false;
        self.init() catch |err| switch (err) {
            error.InvalidLifecycleTransition => double_init_rejected = true,
            else => return err,
        };

        var post_init_retarget_rejected = false;
        self.retargetSymbol("do_exit") catch |err| switch (err) {
            error.InvalidLifecycleTransition => post_init_retarget_rejected = true,
            else => return err,
        };

        return .{
            .pre_init_anchor_rejected = pre_init_anchor_rejected,
            .pre_init_exit_rejected = pre_init_exit_rejected,
            .double_init_rejected = double_init_rejected,
            .post_init_retarget_rejected = post_init_retarget_rejected,
            .stage_after_checks = self.stage(),
        };
    }

    pub fn runOwnershipReplay(self: *Self) !OwnershipReplaySummary {
        const cold = self.snapshot();
        try self.init();
        const initialized = self.snapshot();
        _ = try self.entryHandler(false, 100);
        const armed = self.snapshot();
        _ = try self.retHandler(42, 175);
        const replay_complete = self.snapshot();
        try self.exit();
        const exited = self.snapshot();

        return .{
            .cold = cold,
            .initialized = initialized,
            .armed = armed,
            .replay_complete = replay_complete,
            .exited = exited,
        };
    }

    pub fn runRecoveryReplay(self: *Self) !RecoveryReplaySummary {
        try self.init();
        _ = try self.entryHandler(false, 200);

        var outstanding_instance_exit_rejected = false;
        self.exit() catch |err| switch (err) {
            error.OutstandingProbeInstance => outstanding_instance_exit_rejected = true,
            else => return err,
        };

        var invalid_timestamp_order_rejected = false;
        _ = self.retHandler(9, 199) catch |err| switch (err) {
            error.InvalidTimestampOrder => {
                invalid_timestamp_order_rejected = true;
                return 0;
            },
            else => return err,
        };

        const recovered_duration_ns = try self.retHandler(9, 260);
        try self.exit();

        var post_exit_entry_rejected = false;
        _ = self.entryHandler(false, 300) catch |err| switch (err) {
            error.InvalidLifecycleTransition => post_exit_entry_rejected = true,
            else => return err,
        };

        var post_exit_ret_rejected = false;
        _ = self.retHandler(9, 320) catch |err| switch (err) {
            error.InvalidLifecycleTransition => post_exit_ret_rejected = true,
            else => return err,
        };

        return .{
            .outstanding_instance_exit_rejected = outstanding_instance_exit_rejected,
            .invalid_timestamp_order_rejected = invalid_timestamp_order_rejected,
            .recovered_duration_ns = recovered_duration_ns,
            .post_exit_entry_rejected = post_exit_entry_rejected,
            .post_exit_ret_rejected = post_exit_ret_rejected,
        };
    }
};

test "phase5 kretprobe descriptor stays non-runtime and reviewable" {
    const descriptor = KretprobeExampleSample.descriptor();

    try std.testing.expectEqualStrings("kretprobe_example", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(!descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selfcheck);
}

test "phase5 kretprobe anchor replay keeps the bounded return-probe cues explicit" {
    var sample = KretprobeExampleSample{};
    try sample.init();
    const replay = try sample.runAnchorReplay();

    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", replay.anchor);
    try std.testing.expectEqualStrings(KretprobeExampleSample.default_symbol_name, replay.symbol_name);
    try std.testing.expect(replay.skipped_kernel_thread_path_checked);
    try std.testing.expectEqual(@as(usize, 8), replay.private_data_size_bytes);
    try std.testing.expectEqual(@as(usize, 42), replay.return_value);
    try std.testing.expectEqual(@as(i64, 75), replay.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.nmissed);
    try std.testing.expectEqual(@as(usize, 20), replay.maxactive);
}
