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

pub const LifecycleSnapshot = struct {
    stage: ModuleStage,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    registration_runs: usize,
    unregistration_runs: usize,
    probe_registered: bool,
    active_instances: usize,
    completed_instances: usize,
    last_retval: ?i32,
    last_entry_timestamp_ns: ?i64,
    last_return_timestamp_ns: ?i64,
    last_duration_ns: ?i64,
    oldest_active_entry_timestamp_ns: ?i64,
    newest_active_entry_timestamp_ns: ?i64,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    checked_registration_paths: bool,
    checked_return_paths: bool,
    checked_lifecycle_guards: bool,
};

pub const RuntimeKretprobeSample = struct {
    const Self = @This();
    const max_active_instances = 8;

    stage_state: ModuleStage = .cold,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,
    registration_runs: usize = 0,
    unregistration_runs: usize = 0,
    probe_registered: bool = false,
    active_instances: usize = 0,
    completed_instances: usize = 0,
    last_retval: ?i32 = null,
    next_timestamp_ns: i64 = 10,
    last_entry_timestamp_ns: ?i64 = null,
    last_return_timestamp_ns: ?i64 = null,
    last_duration_ns: ?i64 = null,
    active_entry_timestamps_ns: [max_active_instances]?i64 = [_]?i64{null} ** max_active_instances,

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

    fn nextSyntheticTimestamp(self: *Self) i64 {
        const timestamp_ns = self.next_timestamp_ns;
        self.next_timestamp_ns += 10;
        return timestamp_ns;
    }

    fn oldestActiveEntryTimestampNs(self: *const Self) ?i64 {
        if (self.active_instances == 0) return null;
        return self.active_entry_timestamps_ns[0];
    }

    fn newestActiveEntryTimestampNs(self: *const Self) ?i64 {
        if (self.active_instances == 0) return null;
        return self.active_entry_timestamps_ns[self.active_instances - 1];
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn lifecycleSnapshot(self: *const Self) LifecycleSnapshot {
        return .{
            .stage = self.stage(),
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .registration_runs = self.registration_runs,
            .unregistration_runs = self.unregistration_runs,
            .probe_registered = self.probe_registered,
            .active_instances = self.active_instances,
            .completed_instances = self.completed_instances,
            .last_retval = self.last_retval,
            .last_entry_timestamp_ns = self.last_entry_timestamp_ns,
            .last_return_timestamp_ns = self.last_return_timestamp_ns,
            .last_duration_ns = self.last_duration_ns,
            .oldest_active_entry_timestamp_ns = self.oldestActiveEntryTimestampNs(),
            .newest_active_entry_timestamp_ns = self.newestActiveEntryTimestampNs(),
        };
    }

    pub fn registerProbe(self: *Self) !void {
        try self.ensureMutable();
        if (self.probe_registered) return error.ProbeAlreadyRegistered;

        self.probe_registered = true;
        self.registration_runs += 1;
    }

    pub fn recordEntry(self: *Self) !void {
        try self.recordEntryAt(self.nextSyntheticTimestamp());
    }

    pub fn recordEntryAt(self: *Self, entry_timestamp_ns: i64) !void {
        try self.ensureMutable();
        if (!self.probe_registered) return error.ProbeNotRegistered;
        if (self.active_instances == max_active_instances) return error.ActiveInstanceCapacityExceeded;

        self.active_entry_timestamps_ns[self.active_instances] = entry_timestamp_ns;
        self.active_instances += 1;
        self.last_entry_timestamp_ns = entry_timestamp_ns;
    }

    pub fn recordReturn(self: *Self, retval: i32) !void {
        try self.recordReturnAt(retval, self.nextSyntheticTimestamp());
    }

    pub fn recordReturnAt(self: *Self, retval: i32, return_timestamp_ns: i64) !void {
        try self.ensureMutable();
        if (!self.probe_registered) return error.ProbeNotRegistered;
        if (self.active_instances == 0) return error.ReturnWithoutEntry;

        const entry_index = self.active_instances - 1;
        const entry_timestamp_ns = self.active_entry_timestamps_ns[entry_index] orelse unreachable;
        if (return_timestamp_ns < entry_timestamp_ns) return error.ReturnBeforeEntryTimestamp;

        self.active_entry_timestamps_ns[entry_index] = null;
        self.active_instances -= 1;
        self.completed_instances += 1;
        self.last_retval = retval;
        self.last_return_timestamp_ns = return_timestamp_ns;
        self.last_duration_ns = return_timestamp_ns - entry_timestamp_ns;
    }

    pub fn unregisterProbe(self: *Self) !void {
        try self.ensureMutable();
        if (!self.probe_registered) return error.ProbeNotRegistered;
        if (self.active_instances != 0) return error.OutstandingReturnInstance;

        self.probe_registered = false;
        self.unregistration_runs += 1;
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        try self.registerProbe();
        try self.recordEntry();
        try self.recordReturn(0);
        try self.unregisterProbe();

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .checked_registration_paths = true,
            .checked_return_paths = true,
            .checked_lifecycle_guards = true,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        if (self.probe_registered) return error.OutstandingRegistration;
        if (self.active_instances != 0) return error.OutstandingReturnInstance;

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

fn expectSnapshotStable(before: LifecycleSnapshot, after: LifecycleSnapshot) !void {
    try std.testing.expectEqual(before.stage, after.stage);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
    try std.testing.expectEqual(before.registration_runs, after.registration_runs);
    try std.testing.expectEqual(before.unregistration_runs, after.unregistration_runs);
    try std.testing.expectEqual(before.probe_registered, after.probe_registered);
    try std.testing.expectEqual(before.active_instances, after.active_instances);
    try std.testing.expectEqual(before.completed_instances, after.completed_instances);
    try std.testing.expectEqual(before.last_retval, after.last_retval);
    try std.testing.expectEqual(before.last_entry_timestamp_ns, after.last_entry_timestamp_ns);
    try std.testing.expectEqual(before.last_return_timestamp_ns, after.last_return_timestamp_ns);
    try std.testing.expectEqual(before.last_duration_ns, after.last_duration_ns);
    try std.testing.expectEqual(
        before.oldest_active_entry_timestamp_ns,
        after.oldest_active_entry_timestamp_ns,
    );
    try std.testing.expectEqual(
        before.newest_active_entry_timestamp_ns,
        after.newest_active_entry_timestamp_ns,
    );
}

test "runtime kretprobe sample advertises the bounded pilot-module contract" {
    const descriptor = RuntimeKretprobeSample.descriptor();
    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
}

test "runtime kretprobe sample keeps selftest hook and return replay explicit" {
    var module = RuntimeKretprobeSample{};
    try module.init();

    const selftest = try module.runSelftest();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", selftest.anchor);
    try std.testing.expect(selftest.checked_registration_paths);
    try std.testing.expect(selftest.checked_return_paths);
    try std.testing.expect(selftest.checked_lifecycle_guards);

    const snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), snapshot.unregistration_runs);
    try std.testing.expect(!snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), snapshot.last_retval);
}

test "runtime kretprobe sample keeps reusable probe replay explicit after selftest" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(17);
    try module.unregisterProbe();

    const before_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), before_exit.unregistration_runs);
    try std.testing.expect(!before_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 2), before_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 17), before_exit.last_retval);

    try module.exit();

    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(before_exit.unregistration_runs, after_exit.unregistration_runs);
    try std.testing.expectEqual(before_exit.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_exit.last_retval, after_exit.last_retval);
}

test "runtime kretprobe sample keeps active-instance timestamp replay explicit across overlapping returns" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntryAt(10);
    try module.recordEntryAt(35);

    const before_returns = module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 2), before_returns.active_instances);
    try std.testing.expectEqual(@as(?i64, 10), before_returns.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 35), before_returns.newest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 35), before_returns.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), before_returns.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), before_returns.last_duration_ns);

    try module.recordReturnAt(7, 80);
    const after_inner_return = module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 1), after_inner_return.active_instances);
    try std.testing.expectEqual(@as(usize, 1), after_inner_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, 7), after_inner_return.last_retval);
    try std.testing.expectEqual(@as(?i64, 80), after_inner_return.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 45), after_inner_return.last_duration_ns);
    try std.testing.expectEqual(@as(?i64, 10), after_inner_return.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 10), after_inner_return.newest_active_entry_timestamp_ns);

    try module.recordReturnAt(11, 150);
    const after_outer_return = module.lifecycleSnapshot();
    try std.testing.expectEqual(@as(usize, 0), after_outer_return.active_instances);
    try std.testing.expectEqual(@as(usize, 2), after_outer_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, 11), after_outer_return.last_retval);
    try std.testing.expectEqual(@as(?i64, 150), after_outer_return.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 140), after_outer_return.last_duration_ns);
    try std.testing.expectEqual(@as(?i64, null), after_outer_return.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), after_outer_return.newest_active_entry_timestamp_ns);
}

test "runtime kretprobe sample rejects re-init without disturbing initialized selftested and exited snapshots" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    const initialized_before = initialized.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.init());
    try expectSnapshotStable(initialized_before, initialized.lifecycleSnapshot());

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    const selftested_before = selftested.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.init());
    try expectSnapshotStable(selftested_before, selftested.lifecycleSnapshot());

    var exited = RuntimeKretprobeSample{};
    try exited.init();
    _ = try exited.runSelftest();
    try exited.exit();
    const exited_before = exited.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, exited.init());
    try expectSnapshotStable(exited_before, exited.lifecycleSnapshot());
}

test "runtime kretprobe sample rejects re-selftest without disturbing summaries" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    _ = try module.runSelftest();

    const before_selftest = module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try expectSnapshotStable(before_selftest, module.lifecycleSnapshot());

    try module.exit();
    const before_exit_selftest = module.lifecycleSnapshot();
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try expectSnapshotStable(before_exit_selftest, module.lifecycleSnapshot());
}

test "runtime kretprobe sample keeps rejected re-exit rollback explicit" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.exit();

    const initialized_before_reexit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_before_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_before_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_before_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_reexit.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_reexit.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_reexit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_reexit.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_before_reexit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.exit());
    try expectSnapshotStable(initialized_before_reexit, initialized.lifecycleSnapshot());

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.exit();

    const selftested_before_reexit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_before_reexit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.unregistration_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_before_reexit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_reexit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), selftested_before_reexit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.exit());
    try expectSnapshotStable(selftested_before_reexit, selftested.lifecycleSnapshot());
}

test "runtime kretprobe sample keeps post-exit probe mutation guards explicit" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.exit();

    const initialized_before_post_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_before_post_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_before_post_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_post_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_before_post_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_post_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_post_exit.unregistration_runs);
    try std.testing.expect(!initialized_before_post_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_post_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_before_post_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_before_post_exit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.recordEntry());
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.recordReturn(5));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.unregisterProbe());
    try expectSnapshotStable(initialized_before_post_exit, initialized.lifecycleSnapshot());

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.exit();

    const selftested_before_post_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_before_post_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.unregistration_runs);
    try std.testing.expect(!selftested_before_post_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), selftested_before_post_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_post_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), selftested_before_post_exit.last_retval);

    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.registerProbe());
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.recordEntry());
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.recordReturn(11));
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.unregisterProbe());
    try expectSnapshotStable(selftested_before_post_exit, selftested.lifecycleSnapshot());
}

test "runtime kretprobe sample keeps failed exit rollback explicit while a probe is still registered across initialized and selftested stages" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(5);

    const before_failed_exit = module.lifecycleSnapshot();
    try std.testing.expect(before_failed_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_failed_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_failed_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 5), before_failed_exit.last_retval);

    try std.testing.expectError(error.OutstandingRegistration, module.exit());
    try expectSnapshotStable(before_failed_exit, module.lifecycleSnapshot());

    try module.unregisterProbe();
    const before_exit = module.lifecycleSnapshot();
    try module.exit();
    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_exit.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_exit.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(before_exit.unregistration_runs, after_exit.unregistration_runs);
    try std.testing.expectEqual(before_exit.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_exit.last_retval, after_exit.last_retval);
}

test "runtime kretprobe sample keeps failed exit rollback explicit while a return instance is still active across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();
    try initialized.recordEntry();

    const before_initialized_failed_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, before_initialized_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_failed_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_failed_exit.unregistration_runs);
    try std.testing.expect(before_initialized_failed_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_failed_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_failed_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_failed_exit.last_retval);

    try std.testing.expectError(error.OutstandingRegistration, initialized.exit());
    try expectSnapshotStable(before_initialized_failed_exit, initialized.lifecycleSnapshot());

    try initialized.recordReturn(21);
    try initialized.unregisterProbe();
    const before_initialized_exit = initialized.lifecycleSnapshot();
    try initialized.exit();
    const initialized_after_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(before_initialized_exit.init_runs, initialized_after_exit.init_runs);
    try std.testing.expectEqual(before_initialized_exit.selftest_runs, initialized_after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);
    try std.testing.expectEqual(before_initialized_exit.registration_runs, initialized_after_exit.registration_runs);
    try std.testing.expectEqual(before_initialized_exit.unregistration_runs, initialized_after_exit.unregistration_runs);
    try std.testing.expectEqual(before_initialized_exit.completed_instances, initialized_after_exit.completed_instances);
    try std.testing.expectEqual(before_initialized_exit.last_retval, initialized_after_exit.last_retval);

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();
    try selftested.recordEntry();

    const before_selftested_failed_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_failed_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_failed_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_failed_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_failed_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_failed_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_failed_exit.unregistration_runs);
    try std.testing.expect(before_selftested_failed_exit.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_failed_exit.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_failed_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_failed_exit.last_retval);

    try std.testing.expectError(error.OutstandingRegistration, selftested.exit());
    try expectSnapshotStable(before_selftested_failed_exit, selftested.lifecycleSnapshot());

    try selftested.recordReturn(42);
    try selftested.unregisterProbe();
    const before_selftested_exit = selftested.lifecycleSnapshot();
    try selftested.exit();
    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(before_selftested_exit.init_runs, selftested_after_exit.init_runs);
    try std.testing.expectEqual(before_selftested_exit.selftest_runs, selftested_after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(before_selftested_exit.registration_runs, selftested_after_exit.registration_runs);
    try std.testing.expectEqual(before_selftested_exit.unregistration_runs, selftested_after_exit.unregistration_runs);
    try std.testing.expectEqual(before_selftested_exit.completed_instances, selftested_after_exit.completed_instances);
    try std.testing.expectEqual(before_selftested_exit.last_retval, selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps failed unregister rollback explicit while a return instance is still active" {
    var module = RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();

    const before_failed_unregister = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, before_failed_unregister.stage);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.unregistration_runs);
    try std.testing.expect(before_failed_unregister.probe_registered);
    try std.testing.expectEqual(@as(usize, 1), before_failed_unregister.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_failed_unregister.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_failed_unregister.last_retval);

    try std.testing.expectError(error.OutstandingReturnInstance, module.unregisterProbe());
    try expectSnapshotStable(before_failed_unregister, module.lifecycleSnapshot());

    try module.recordReturn(21);
    const before_cleanup = module.lifecycleSnapshot();
    try std.testing.expect(before_cleanup.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_cleanup.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_cleanup.completed_instances);
    try std.testing.expectEqual(@as(?i32, 21), before_cleanup.last_retval);

    try module.unregisterProbe();
    try module.exit();

    const after_exit = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);
    try std.testing.expectEqual(before_cleanup.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(before_cleanup.selftest_runs, after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expectEqual(before_cleanup.registration_runs, after_exit.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.unregistration_runs);
    try std.testing.expectEqual(before_cleanup.completed_instances, after_exit.completed_instances);
    try std.testing.expectEqual(before_cleanup.last_retval, after_exit.last_retval);
}

test "runtime kretprobe sample keeps rejected entry-without-registration rollback explicit across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();

    const before_initialized_rejected_entry = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, before_initialized_rejected_entry.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_entry.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.unregistration_runs);
    try std.testing.expect(!before_initialized_rejected_entry.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_entry.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_rejected_entry.last_retval);

    try std.testing.expectError(error.ProbeNotRegistered, initialized.recordEntry());
    try expectSnapshotStable(before_initialized_rejected_entry, initialized.lifecycleSnapshot());

    try initialized.exit();
    const initialized_after_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();

    const before_selftested_rejected_entry = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_rejected_entry.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_entry.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.unregistration_runs);
    try std.testing.expect(!before_selftested_rejected_entry.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_entry.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_entry.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_rejected_entry.last_retval);

    try std.testing.expectError(error.ProbeNotRegistered, selftested.recordEntry());
    try expectSnapshotStable(before_selftested_rejected_entry, selftested.lifecycleSnapshot());

    try selftested.exit();
    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps rejected return-without-entry rollback explicit across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();

    const before_initialized_rejected_return = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, before_initialized_rejected_return.stage);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), before_initialized_rejected_return.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.unregistration_runs);
    try std.testing.expect(before_initialized_rejected_return.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.active_instances);
    try std.testing.expectEqual(@as(usize, 0), before_initialized_rejected_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), before_initialized_rejected_return.last_retval);

    try std.testing.expectError(error.ReturnWithoutEntry, initialized.recordReturn(7));
    try expectSnapshotStable(before_initialized_rejected_return, initialized.lifecycleSnapshot());

    try initialized.unregisterProbe();
    try initialized.exit();
    const initialized_after_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();

    const before_selftested_rejected_return = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, before_selftested_rejected_return.stage);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_return.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), before_selftested_rejected_return.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.unregistration_runs);
    try std.testing.expect(before_selftested_rejected_return.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), before_selftested_rejected_return.active_instances);
    try std.testing.expectEqual(@as(usize, 1), before_selftested_rejected_return.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), before_selftested_rejected_return.last_retval);

    try std.testing.expectError(error.ReturnWithoutEntry, selftested.recordReturn(11));
    try expectSnapshotStable(before_selftested_rejected_return, selftested.lifecycleSnapshot());

    try selftested.recordEntry();
    try selftested.recordReturn(42);
    try selftested.unregisterProbe();
    try selftested.exit();
    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps duplicate registration rollback explicit across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();

    const initialized_before = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_before.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_before.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.unregistration_runs);
    try std.testing.expect(initialized_before.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_before.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_before.last_retval);

    try std.testing.expectError(error.ProbeAlreadyRegistered, initialized.registerProbe());
    try expectSnapshotStable(initialized_before, initialized.lifecycleSnapshot());

    try initialized.unregisterProbe();
    try initialized.exit();
    const initialized_after_exit = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_after_exit.exit_runs);

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();

    const selftested_before = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested_before.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_before.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested_before.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_before.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_before.unregistration_runs);
    try std.testing.expect(selftested_before.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), selftested_before.active_instances);
    try std.testing.expectEqual(@as(usize, 1), selftested_before.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), selftested_before.last_retval);

    try std.testing.expectError(error.ProbeAlreadyRegistered, selftested.registerProbe());
    try expectSnapshotStable(selftested_before, selftested.lifecycleSnapshot());

    try selftested.recordEntry();
    try selftested.recordReturn(42);
    try selftested.unregisterProbe();
    try selftested.exit();
    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_after_exit.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 42), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps maxactive saturation rollback explicit across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();
    inline for ([_]i64{ 10, 20, 30, 40, 50, 60, 70, 80 }) |entry_timestamp_ns| {
        try initialized.recordEntryAt(entry_timestamp_ns);
    }

    const initialized_before_capacity = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before_capacity.stage);
    try std.testing.expectEqual(@as(usize, 8), initialized_before_capacity.active_instances);
    try std.testing.expectEqual(@as(?i64, 10), initialized_before_capacity.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 80), initialized_before_capacity.newest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 80), initialized_before_capacity.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i32, null), initialized_before_capacity.last_retval);

    try std.testing.expectError(error.ActiveInstanceCapacityExceeded, initialized.recordEntryAt(90));
    try expectSnapshotStable(initialized_before_capacity, initialized.lifecycleSnapshot());

    inline for ([_]struct { retval: i32, ts: i64 }{
        .{ .retval = 1, .ts = 81 },
        .{ .retval = 2, .ts = 82 },
        .{ .retval = 3, .ts = 83 },
        .{ .retval = 4, .ts = 84 },
        .{ .retval = 5, .ts = 85 },
        .{ .retval = 6, .ts = 86 },
        .{ .retval = 7, .ts = 87 },
        .{ .retval = 8, .ts = 88 },
    }) |ret| {
        try initialized.recordReturnAt(ret.retval, ret.ts);
    }
    try initialized.unregisterProbe();
    try initialized.exit();

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();
    inline for ([_]i64{ 100, 110, 120, 130, 140, 150, 160, 170 }) |entry_timestamp_ns| {
        try selftested.recordEntryAt(entry_timestamp_ns);
    }

    const selftested_before_capacity = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested_before_capacity.stage);
    try std.testing.expectEqual(@as(usize, 8), selftested_before_capacity.active_instances);
    try std.testing.expectEqual(@as(?i64, 100), selftested_before_capacity.oldest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 170), selftested_before_capacity.newest_active_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 170), selftested_before_capacity.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i32, 0), selftested_before_capacity.last_retval);

    try std.testing.expectError(error.ActiveInstanceCapacityExceeded, selftested.recordEntryAt(180));
    try expectSnapshotStable(selftested_before_capacity, selftested.lifecycleSnapshot());

    inline for ([_]struct { retval: i32, ts: i64 }{
        .{ .retval = 11, .ts = 171 },
        .{ .retval = 12, .ts = 172 },
        .{ .retval = 13, .ts = 173 },
        .{ .retval = 14, .ts = 174 },
        .{ .retval = 15, .ts = 175 },
        .{ .retval = 16, .ts = 176 },
        .{ .retval = 17, .ts = 177 },
        .{ .retval = 18, .ts = 178 },
    }) |ret| {
        try selftested.recordReturnAt(ret.retval, ret.ts);
    }
    try selftested.unregisterProbe();
    try selftested.exit();

    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 9), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 18), selftested_after_exit.last_retval);
}

test "runtime kretprobe sample keeps return timestamp rollback explicit across initialized and selftested stages" {
    var initialized = RuntimeKretprobeSample{};
    try initialized.init();
    try initialized.registerProbe();
    try initialized.recordEntryAt(40);

    const initialized_before_bad_return = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized_before_bad_return.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_before_bad_return.active_instances);
    try std.testing.expectEqual(@as(?i64, 40), initialized_before_bad_return.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), initialized_before_bad_return.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, null), initialized_before_bad_return.last_duration_ns);

    try std.testing.expectError(error.ReturnBeforeEntryTimestamp, initialized.recordReturnAt(7, 39));
    try expectSnapshotStable(initialized_before_bad_return, initialized.lifecycleSnapshot());

    try initialized.recordReturnAt(7, 41);
    try initialized.unregisterProbe();
    try initialized.exit();

    var selftested = RuntimeKretprobeSample{};
    try selftested.init();
    _ = try selftested.runSelftest();
    try selftested.registerProbe();
    try selftested.recordEntryAt(100);

    const selftested_before_bad_return = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested_before_bad_return.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_before_bad_return.active_instances);
    try std.testing.expectEqual(@as(?i64, 100), selftested_before_bad_return.last_entry_timestamp_ns);
    try std.testing.expectEqual(@as(?i32, 0), selftested_before_bad_return.last_retval);

    try std.testing.expectError(error.ReturnBeforeEntryTimestamp, selftested.recordReturnAt(11, 99));
    try expectSnapshotStable(selftested_before_bad_return, selftested.lifecycleSnapshot());

    try selftested.recordReturnAt(11, 120);
    try selftested.unregisterProbe();
    try selftested.exit();

    const selftested_after_exit = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_after_exit.stage);
    try std.testing.expectEqual(@as(usize, 2), selftested_after_exit.completed_instances);
    try std.testing.expectEqual(@as(?i32, 11), selftested_after_exit.last_retval);
    try std.testing.expectEqual(@as(?i64, 120), selftested_after_exit.last_return_timestamp_ns);
    try std.testing.expectEqual(@as(?i64, 20), selftested_after_exit.last_duration_ns);
}
