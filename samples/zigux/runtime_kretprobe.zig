const std = @import("std");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const ProbeFocus = enum {
    entry_timestamp,
    return_value,
    duration_ns,
    missed_instances,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
};

pub const InstancePrivateData = struct {
    entry_stamp_ns: i64 = -1,
};

pub const ProbeResult = struct {
    retval: usize,
    duration_ns: i64,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    probe_focus: []const ProbeFocus,
    skipped_kernel_thread_path_checked: bool,
    duration_path_checked: bool,
    missed_instance_path_checked: bool,
    last_retval: usize,
    last_duration_ns: i64,
    nmissed: usize,
    maxactive: usize,
};

pub const RuntimeKretprobeSummary = struct {
    stage: ModuleStage,
    symbol_name: []const u8,
    maxactive: usize,
    active_instances: usize,
    skipped_kernel_threads: usize,
    nmissed: usize,
    last_retval: usize,
    last_duration_ns: i64,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    entry_timestamp_armed: bool,
};

pub const FailedExitRecoveryReplay = struct {
    before_failed_exit: RuntimeKretprobeSummary,
    after_failed_exit: RuntimeKretprobeSummary,
    recovered: ProbeResult,
    selftest: SelftestSummary,
    final_summary: RuntimeKretprobeSummary,
};

pub const MaxactivePressureReplay = struct {
    before_pressure: RuntimeKretprobeSummary,
    after_pressure: RuntimeKretprobeSummary,
    recovered: ProbeResult,
    final_summary: RuntimeKretprobeSummary,
};

pub const RuntimeKretprobeSample = struct {
    const Self = @This();

    pub const default_symbol_name = "kernel_clone";
    pub const default_maxactive: usize = 20;
    pub const max_symbol_name_len: usize = 512;

    stage_state: ModuleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
    maxactive: usize = default_maxactive,
    active_instances: usize = 0,
    skipped_kernel_threads: usize = 0,
    nmissed: usize = 0,
    instance_private_data: [default_maxactive]InstancePrivateData = [_]InstancePrivateData{.{}} ** default_maxactive,
    last_retval: usize = 0,
    last_duration_ns: i64 = 0,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "runtime_kretprobe",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
        };
    }

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
    }

    pub fn summary(self: *const Self) RuntimeKretprobeSummary {
        return .{
            .stage = self.stage(),
            .symbol_name = self.symbol_name,
            .maxactive = self.maxactive,
            .active_instances = self.active_instances,
            .skipped_kernel_threads = self.skipped_kernel_threads,
            .nmissed = self.nmissed,
            .last_retval = self.last_retval,
            .last_duration_ns = self.last_duration_ns,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .entry_timestamp_armed = self.active_instances > 0,
        };
    }

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    fn resetPrivateData(self: *Self) void {
        for (&self.instance_private_data) |*slot| {
            slot.* = .{};
        }
    }

    pub fn retargetSymbol(self: *Self, symbol_name: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (symbol_name.len == 0) return error.InvalidSymbolName;
        if (symbol_name.len >= max_symbol_name_len) return error.SymbolNameTooLong;

        self.symbol_name = symbol_name;
    }

    pub fn configureMaxactive(self: *Self, maxactive: usize) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (maxactive == 0 or maxactive > default_maxactive) return error.InvalidMaxactive;

        self.maxactive = maxactive;
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (self.symbol_name.len == 0) return error.InvalidSymbolName;
        if (self.symbol_name.len >= max_symbol_name_len) return error.SymbolNameTooLong;
        if (self.maxactive == 0 or self.maxactive > default_maxactive) return error.InvalidMaxactive;

        self.active_instances = 0;
        self.skipped_kernel_threads = 0;
        self.nmissed = 0;
        self.resetPrivateData();
        self.last_retval = 0;
        self.last_duration_ns = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn entryHandler(self: *Self, has_mm: bool, stamp_ns: i64) !bool {
        try self.ensureMutable();

        if (!has_mm) {
            self.skipped_kernel_threads += 1;
            return false;
        }
        if (self.active_instances >= self.maxactive) {
            self.nmissed += 1;
            return error.MaxactiveExceeded;
        }

        self.instance_private_data[self.active_instances] = .{
            .entry_stamp_ns = stamp_ns,
        };
        self.active_instances += 1;
        return true;
    }

    pub fn retHandler(self: *Self, retval: usize, now_ns: i64) !ProbeResult {
        try self.ensureMutable();
        if (self.active_instances == 0) return error.MissingEntryTimestamp;

        const slot_index = self.active_instances - 1;
        const entry_stamp_ns = self.instance_private_data[slot_index].entry_stamp_ns;
        if (entry_stamp_ns < 0) return error.MissingEntryTimestamp;
        if (now_ns < entry_stamp_ns) return error.InvalidTimestampOrder;

        const duration_ns = now_ns - entry_stamp_ns;
        self.instance_private_data[slot_index] = .{};
        self.active_instances -= 1;
        self.last_retval = retval;
        self.last_duration_ns = duration_ns;
        return .{
            .retval = retval,
            .duration_ns = duration_ns,
        };
    }

    pub fn recordMissedInstance(self: *Self) !void {
        try self.ensureMutable();
        self.nmissed += 1;
    }

    pub fn runMaxactivePressureReplay(self: *Self) !MaxactivePressureReplay {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        try self.configureMaxactive(1);
        try self.init();

        const armed = try self.entryHandler(true, 410);
        if (!armed) return error.UnexpectedEntrySkip;
        const before_pressure = self.summary();

        if (self.entryHandler(true, 430)) |_| {
            return error.ExpectedMaxactiveExceeded;
        } else |err| switch (err) {
            error.MaxactiveExceeded => {},
            else => return err,
        }

        const after_pressure = self.summary();
        const recovered = try self.retHandler(17, 490);
        try self.exit();

        return .{
            .before_pressure = before_pressure,
            .after_pressure = after_pressure,
            .recovered = recovered,
            .final_summary = self.summary(),
        };
    }

    pub fn runFailedExitRecoveryReplay(self: *Self) !FailedExitRecoveryReplay {
        const armed = try self.entryHandler(true, 410);
        if (!armed) return error.UnexpectedEntrySkip;
        const before_failed_exit = self.summary();

        if (self.exit()) |_| {
            return error.ExpectedOutstandingProbeInstance;
        } else |err| switch (err) {
            error.OutstandingProbeInstance => {},
            else => return err,
        }

        const after_failed_exit = self.summary();
        const recovered = try self.retHandler(17, 490);
        const selftest = try self.runSelftest();
        try self.exit();

        return .{
            .before_failed_exit = before_failed_exit,
            .after_failed_exit = after_failed_exit,
            .recovered = recovered,
            .selftest = selftest,
            .final_summary = self.summary(),
        };
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const skipped = try self.entryHandler(false, 10);
        if (skipped) return error.UnexpectedEntryArming;

        const armed = try self.entryHandler(true, 100);
        if (!armed) return error.UnexpectedEntrySkip;

        const result = try self.retHandler(42, 175);
        try self.recordMissedInstance();

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .probe_focus = &.{
                .entry_timestamp,
                .return_value,
                .duration_ns,
                .missed_instances,
            },
            .skipped_kernel_thread_path_checked = self.skipped_kernel_threads > 0,
            .duration_path_checked = result.duration_ns > 0,
            .missed_instance_path_checked = self.nmissed > 0,
            .last_retval = self.last_retval,
            .last_duration_ns = self.last_duration_ns,
            .nmissed = self.nmissed,
            .maxactive = self.maxactive,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        if (self.active_instances != 0) return error.OutstandingProbeInstance;

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "runtime kretprobe sample keeps lifecycle replay and summary accounting explicit" {
    const descriptor = RuntimeKretprobeSample.descriptor();
    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeKretprobeSample{};
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    const cold_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.active_instances);
    try std.testing.expect(!cold_summary.entry_timestamp_armed);

    try module.retargetSymbol("do_sys_openat2");
    try module.init();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());

    const initialized_summary = module.summary();
    try std.testing.expectEqualStrings("do_sys_openat2", initialized_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.active_instances);
    try std.testing.expect(!initialized_summary.entry_timestamp_armed);

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.probe_focus.len);
    try std.testing.expect(selftest.skipped_kernel_thread_path_checked);
    try std.testing.expect(selftest.duration_path_checked);
    try std.testing.expect(selftest.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), selftest.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftest.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), selftest.nmissed);
    try std.testing.expectEqual(RuntimeKretprobeSample.default_maxactive, selftest.maxactive);

    const selftest_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 42), selftest_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftest_summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.nmissed);
    try std.testing.expect(!selftest_summary.entry_timestamp_armed);

    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());

    const exited_summary = module.summary();
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 42), exited_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), exited_summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.nmissed);
    try std.testing.expect(!exited_summary.entry_timestamp_armed);
}

test "runtime kretprobe sample replays bounded skip, return, and concurrent timestamp paths" {
    const too_long_symbol = [_]u8{'k'} ** RuntimeKretprobeSample.max_symbol_name_len;

    var cold = RuntimeKretprobeSample{};
    try std.testing.expectError(error.InvalidSymbolName, cold.retargetSymbol(""));
    try std.testing.expectError(error.SymbolNameTooLong, cold.retargetSymbol(too_long_symbol[0..]));
    try std.testing.expectError(error.InvalidMaxactive, cold.configureMaxactive(0));
    try std.testing.expectError(error.InvalidMaxactive, cold.configureMaxactive(RuntimeKretprobeSample.default_maxactive + 1));

    var module = RuntimeKretprobeSample{};
    try module.configureMaxactive(2);
    try module.init();
    try std.testing.expectEqual(@as(usize, 2), module.maxactive);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.configureMaxactive(1));

    try std.testing.expect(!(try module.entryHandler(false, 11)));
    try std.testing.expectEqual(@as(usize, 1), module.skipped_kernel_threads);

    try std.testing.expect(try module.entryHandler(true, 100));
    try std.testing.expect(try module.entryHandler(true, 160));
    try std.testing.expectEqual(@as(usize, 2), module.active_instances);
    try std.testing.expect(module.summary().entry_timestamp_armed);

    try std.testing.expectError(error.InvalidTimestampOrder, module.retHandler(9, 159));

    const second = try module.retHandler(12, 210);
    try std.testing.expectEqual(@as(usize, 12), second.retval);
    try std.testing.expectEqual(@as(i64, 50), second.duration_ns);
    try std.testing.expectEqual(@as(usize, 1), module.active_instances);

    const first = try module.retHandler(37, 260);
    try std.testing.expectEqual(@as(usize, 37), first.retval);
    try std.testing.expectEqual(@as(i64, 160), first.duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.active_instances);

    try module.recordMissedInstance();
    try std.testing.expectEqual(@as(usize, 1), module.nmissed);
    try std.testing.expectError(error.MissingEntryTimestamp, module.retHandler(5, 300));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retargetSymbol("vfs_read"));

    try module.exit();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.entryHandler(true, 320));
}

test "runtime kretprobe sample keeps maxactive pressure replay explicit in the direct sample leg" {
    var module = RuntimeKretprobeSample{};
    const replay = try module.runMaxactivePressureReplay();

    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(ModuleStage.initialized, replay.before_pressure.stage);
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, replay.before_pressure.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), replay.before_pressure.maxactive);
    try std.testing.expectEqual(@as(usize, 1), replay.before_pressure.active_instances);
    try std.testing.expectEqual(@as(usize, 0), replay.before_pressure.nmissed);
    try std.testing.expectEqual(@as(usize, 1), replay.before_pressure.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.before_pressure.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.before_pressure.exit_runs);
    try std.testing.expect(replay.before_pressure.entry_timestamp_armed);

    try std.testing.expectEqual(ModuleStage.initialized, replay.after_pressure.stage);
    try std.testing.expectEqualStrings(replay.before_pressure.symbol_name, replay.after_pressure.symbol_name);
    try std.testing.expectEqual(replay.before_pressure.maxactive, replay.after_pressure.maxactive);
    try std.testing.expectEqual(replay.before_pressure.active_instances, replay.after_pressure.active_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.after_pressure.nmissed);
    try std.testing.expectEqual(replay.before_pressure.init_runs, replay.after_pressure.init_runs);
    try std.testing.expectEqual(replay.before_pressure.selftest_runs, replay.after_pressure.selftest_runs);
    try std.testing.expectEqual(replay.before_pressure.exit_runs, replay.after_pressure.exit_runs);
    try std.testing.expect(replay.after_pressure.entry_timestamp_armed);

    try std.testing.expectEqual(@as(usize, 17), replay.recovered.retval);
    try std.testing.expectEqual(@as(i64, 80), replay.recovered.duration_ns);

    try std.testing.expectEqual(ModuleStage.exited, replay.final_summary.stage);
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, replay.final_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 0), replay.final_summary.active_instances);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 17), replay.final_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 80), replay.final_summary.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.final_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.exit_runs);
    try std.testing.expect(!replay.final_summary.entry_timestamp_armed);
}

test "runtime kretprobe sample keeps failed exit rollback explicit in the direct sample leg" {
    var module = RuntimeKretprobeSample{};
    try module.configureMaxactive(1);
    try module.init();
    const replay = try module.runFailedExitRecoveryReplay();

    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(ModuleStage.initialized, replay.before_failed_exit.stage);
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, replay.before_failed_exit.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), replay.before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), replay.before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.before_failed_exit.maxactive);
    try std.testing.expectEqual(@as(usize, 1), replay.before_failed_exit.active_instances);
    try std.testing.expect(replay.before_failed_exit.entry_timestamp_armed);
    try std.testing.expectEqual(@as(usize, 0), replay.before_failed_exit.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 0), replay.before_failed_exit.nmissed);
    try std.testing.expectEqual(@as(usize, 0), replay.before_failed_exit.last_retval);
    try std.testing.expectEqual(@as(i64, 0), replay.before_failed_exit.last_duration_ns);

    try std.testing.expectEqual(ModuleStage.initialized, replay.after_failed_exit.stage);
    try std.testing.expectEqualStrings(replay.before_failed_exit.symbol_name, replay.after_failed_exit.symbol_name);
    try std.testing.expectEqual(replay.before_failed_exit.init_runs, replay.after_failed_exit.init_runs);
    try std.testing.expectEqual(replay.before_failed_exit.selftest_runs, replay.after_failed_exit.selftest_runs);
    try std.testing.expectEqual(replay.before_failed_exit.exit_runs, replay.after_failed_exit.exit_runs);
    try std.testing.expectEqual(replay.before_failed_exit.maxactive, replay.after_failed_exit.maxactive);
    try std.testing.expectEqual(replay.before_failed_exit.active_instances, replay.after_failed_exit.active_instances);
    try std.testing.expectEqual(replay.before_failed_exit.entry_timestamp_armed, replay.after_failed_exit.entry_timestamp_armed);
    try std.testing.expectEqual(replay.before_failed_exit.skipped_kernel_threads, replay.after_failed_exit.skipped_kernel_threads);
    try std.testing.expectEqual(replay.before_failed_exit.nmissed, replay.after_failed_exit.nmissed);
    try std.testing.expectEqual(replay.before_failed_exit.last_retval, replay.after_failed_exit.last_retval);
    try std.testing.expectEqual(replay.before_failed_exit.last_duration_ns, replay.after_failed_exit.last_duration_ns);

    try std.testing.expectEqual(@as(usize, 17), replay.recovered.retval);
    try std.testing.expectEqual(@as(i64, 80), replay.recovered.duration_ns);
    try std.testing.expect(replay.selftest.skipped_kernel_thread_path_checked);
    try std.testing.expect(replay.selftest.duration_path_checked);
    try std.testing.expect(replay.selftest.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), replay.selftest.last_retval);
    try std.testing.expectEqual(@as(i64, 75), replay.selftest.last_duration_ns);

    try std.testing.expectEqual(ModuleStage.exited, replay.final_summary.stage);
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, replay.final_summary.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.maxactive);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.skipped_kernel_threads);
    try std.testing.expectEqual(@as(usize, 1), replay.final_summary.nmissed);
    try std.testing.expectEqual(@as(usize, 42), replay.final_summary.last_retval);
    try std.testing.expectEqual(@as(i64, 75), replay.final_summary.last_duration_ns);
    try std.testing.expect(!replay.final_summary.entry_timestamp_armed);
}
