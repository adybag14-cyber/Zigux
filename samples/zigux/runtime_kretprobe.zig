const std = @import("std");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
};

pub const InstancePrivateData = struct {
    entry_timestamp_ns: i64 = 0,
};

pub const ProbeResult = struct {
    retval: usize,
    duration_ns: i64,
};

pub const RuntimeKretprobeSummary = struct {
    stage: ModuleStage,
    init_runs: usize,
    exit_runs: usize,
    symbol_name: []const u8,
    maxactive: usize,
    active_instances: usize,
    skipped_kernel_threads: usize,
    nmissed: usize,
    last_retval: usize,
    last_duration_ns: i64,
    selftest_runs: usize,
    entry_timestamp_armed: bool,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    probe_focus: []const []const u8,
    skipped_kernel_thread_path_checked: bool,
    duration_path_checked: bool,
    missed_instance_path_checked: bool,
    last_retval: usize,
    last_duration_ns: i64,
    nmissed: usize,
    maxactive: usize,
};

pub const ExitReport = struct {
    symbol_name: []const u8,
    skipped_kernel_threads: usize,
    missed_instances: usize,
    last_retval: usize,
    last_duration_ns: i64,
    selftest_runs: usize,
};

const selftest_probe_focus = [_][]const u8{
    "skipped-kernel-thread",
    "duration-tracking",
    "missed-instance-accounting",
    "lifecycle-retention",
};

pub const RuntimeKretprobeSample = struct {
    const Self = @This();

    pub const default_symbol_name = "do_fork";
    pub const default_maxactive: usize = 20;

    stage_state: ModuleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
    maxactive: usize = default_maxactive,
    init_runs: usize = 0,
    exit_runs: usize = 0,
    selftest_runs: usize = 0,
    active_instances: usize = 0,
    skipped_kernel_threads: usize = 0,
    nmissed: usize = 0,
    last_retval: usize = 0,
    last_duration_ns: i64 = 0,
    entry_timestamp_ns: ?i64 = null,

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

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn retargetSymbol(self: *Self, symbol_name: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (symbol_name.len == 0) return error.InvalidSymbolName;
        self.symbol_name = symbol_name;
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (self.maxactive == 0 or self.maxactive > default_maxactive) return error.InvalidMaxactive;

        self.active_instances = 0;
        self.skipped_kernel_threads = 0;
        self.nmissed = 0;
        self.last_retval = 0;
        self.last_duration_ns = 0;
        self.entry_timestamp_ns = null;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn entryHandler(self: *Self, is_target_thread: bool, timestamp_ns: i64) !bool {
        try self.ensureMutable();

        if (!is_target_thread) {
            self.skipped_kernel_threads += 1;
            return false;
        }

        if (self.active_instances >= self.maxactive) {
            self.nmissed += 1;
            return error.MaxactiveExceeded;
        }

        if (self.active_instances == 0) {
            self.entry_timestamp_ns = timestamp_ns;
        }
        self.active_instances += 1;
        return true;
    }

    pub fn retHandler(self: *Self, retval: usize, timestamp_ns: i64) !ProbeResult {
        try self.ensureMutable();
        if (self.active_instances == 0) return error.InvalidLifecycleTransition;

        const entry_timestamp = self.entry_timestamp_ns orelse return error.InvalidLifecycleTransition;
        if (timestamp_ns < entry_timestamp) return error.InvalidTimestampOrder;

        self.active_instances -= 1;
        if (self.active_instances == 0) {
            self.entry_timestamp_ns = null;
        }

        self.last_retval = retval;
        self.last_duration_ns = timestamp_ns - entry_timestamp;
        return .{
            .retval = retval,
            .duration_ns = self.last_duration_ns,
        };
    }

    pub fn recordMissedInstance(self: *Self) !void {
        try self.ensureMutable();
        self.nmissed += 1;
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        _ = try self.entryHandler(false, 40);
        _ = try self.entryHandler(true, 100);
        const result = try self.retHandler(42, 175);
        try self.recordMissedInstance();

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .probe_focus = &selftest_probe_focus,
            .skipped_kernel_thread_path_checked = true,
            .duration_path_checked = true,
            .missed_instance_path_checked = true,
            .last_retval = result.retval,
            .last_duration_ns = result.duration_ns,
            .nmissed = self.nmissed,
            .maxactive = self.maxactive,
        };
    }

    pub fn summary(self: *const Self) RuntimeKretprobeSummary {
        return .{
            .stage = self.stage(),
            .init_runs = self.init_runs,
            .exit_runs = self.exit_runs,
            .symbol_name = self.symbol_name,
            .maxactive = self.maxactive,
            .active_instances = self.active_instances,
            .skipped_kernel_threads = self.skipped_kernel_threads,
            .nmissed = self.nmissed,
            .last_retval = self.last_retval,
            .last_duration_ns = self.last_duration_ns,
            .selftest_runs = self.selftest_runs,
            .entry_timestamp_armed = self.entry_timestamp_ns != null,
        };
    }

    pub fn exit(self: *Self) !ExitReport {
        try self.ensureMutable();
        if (self.active_instances != 0) return error.OutstandingProbeInstance;

        self.exit_runs += 1;
        self.stage_state = .exited;
        return .{
            .symbol_name = self.symbol_name,
            .skipped_kernel_threads = self.skipped_kernel_threads,
            .missed_instances = self.nmissed,
            .last_retval = self.last_retval,
            .last_duration_ns = self.last_duration_ns,
            .selftest_runs = self.selftest_runs,
        };
    }
};

test "runtime kretprobe sample advertises the bounded runtime pilot contract" {
    const descriptor = RuntimeKretprobeSample.descriptor();

    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime kretprobe summary keeps lifecycle hooks explicit across init selftest and exit" {
    var module = RuntimeKretprobeSample{};

    const cold = module.summary();
    try std.testing.expectEqual(ModuleStage.cold, cold.stage);
    try std.testing.expectEqual(@as(usize, 0), cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.exit_runs);

    try module.init();

    const initialized = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.exit_runs);

    _ = try module.runSelftest();

    const selftested = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested.exit_runs);

    _ = try module.exit();

    const exited = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
}

test "runtime kretprobe summary keeps selftest lifecycle hooks pinned across failed exit recovery" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();
    try std.testing.expect(try module.entryHandler(true, 400));

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.active_instances);

    try std.testing.expectError(error.OutstandingProbeInstance, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(before_failed_exit.stage, after_failed_exit.stage);
    try std.testing.expectEqual(before_failed_exit.init_runs, after_failed_exit.init_runs);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.exit_runs, after_failed_exit.exit_runs);
    try std.testing.expectEqual(before_failed_exit.active_instances, after_failed_exit.active_instances);

    _ = try module.retHandler(7, 455);
    _ = try module.exit();

    const exited = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
}

test "runtime kretprobe sample keeps a retargeted symbol fixed across init selftest and exit" {
    var module = RuntimeKretprobeSample{};
    try module.retargetSymbol("do_sys_openat2");
    try std.testing.expectEqualStrings("do_sys_openat2", module.summary().symbol_name);

    try module.init();
    try std.testing.expectEqualStrings("do_sys_openat2", module.summary().symbol_name);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retargetSymbol("vfs_read"));

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("do_sys_openat2", selftest.symbol_name);
    try std.testing.expectEqualStrings("do_sys_openat2", module.summary().symbol_name);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings("do_sys_openat2", exit_report.symbol_name);
    try std.testing.expectEqualStrings("do_sys_openat2", module.summary().symbol_name);
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.retargetSymbol("do_execve"));
}

test "kretprobe sample preserves initialized-stage failed-exit state until the active probe drains before selftest" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try std.testing.expect(try module.entryHandler(true, 200));

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.active_instances);
    try std.testing.expect(before_failed_exit.entry_timestamp_armed);

    try std.testing.expectError(error.OutstandingProbeInstance, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(before_failed_exit.active_instances, after_failed_exit.active_instances);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);
    try std.testing.expectEqual(before_failed_exit.entry_timestamp_armed, after_failed_exit.entry_timestamp_armed);

    const recovered = try module.retHandler(9, 260);
    try std.testing.expectEqual(@as(usize, 9), recovered.retval);
    try std.testing.expectEqual(@as(i64, 60), recovered.duration_ns);
    try std.testing.expectEqual(@as(usize, 0), module.summary().active_instances);
}

test "kretprobe sample preserves failed-exit state until the active probe drains after selftest" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();
    try std.testing.expect(try module.entryHandler(true, 400));

    const before_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.active_instances);

    try std.testing.expectError(error.OutstandingProbeInstance, module.exit());

    const after_failed_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(before_failed_exit.active_instances, after_failed_exit.active_instances);
    try std.testing.expectEqual(before_failed_exit.nmissed, after_failed_exit.nmissed);
    try std.testing.expectEqual(before_failed_exit.selftest_runs, after_failed_exit.selftest_runs);

    const recovered = try module.retHandler(7, 455);
    try std.testing.expectEqual(@as(usize, 7), recovered.retval);
    try std.testing.expectEqual(@as(i64, 55), recovered.duration_ns);

    const exit_report = try module.exit();
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, exit_report.symbol_name);
    try std.testing.expectEqual(@as(usize, 1), exit_report.selftest_runs);
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
}

test "runtime kretprobe sample keeps selftest missed-instance and maxactive cues explicit" {
    var module = RuntimeKretprobeSample{ .maxactive = 1 };
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings(RuntimeKretprobeSample.default_symbol_name, selftest.symbol_name);
    try std.testing.expectEqual(@as(usize, 4), selftest.probe_focus.len);
    try std.testing.expect(selftest.skipped_kernel_thread_path_checked);
    try std.testing.expect(selftest.duration_path_checked);
    try std.testing.expect(selftest.missed_instance_path_checked);
    try std.testing.expectEqual(@as(usize, 42), selftest.last_retval);
    try std.testing.expectEqual(@as(i64, 75), selftest.last_duration_ns);
    try std.testing.expectEqual(@as(usize, 1), selftest.nmissed);
    try std.testing.expectEqual(@as(usize, 1), selftest.maxactive);

    try std.testing.expect(try module.entryHandler(true, 500));
    try std.testing.expectError(error.MaxactiveExceeded, module.entryHandler(true, 520));
    try std.testing.expectEqual(@as(usize, 2), module.summary().nmissed);
}
