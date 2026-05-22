const std = @import("std");
const atomic = @import("atomic");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const OperationFamily = enum {
    arithmetic,
    bitwise,
    returning_ops,
    swap_ops,
    guard_ops,
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
    allows_counter_ops: bool,
};

pub const Summary = struct {
    counter_snapshot: i64,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    operation_families: []const OperationFamily,
    checked_returning_paths: bool,
    checked_bitwise_paths: bool,
    checked_guard_paths: bool,
};

pub const CounterUpdate = struct {
    previous: i64,
    final: i64,
};

pub const CompareSwapResult = struct {
    previous: i64,
    stored: bool,
};

pub const AddUnlessResult = struct {
    previous: i64,
    changed: bool,
};

pub const DecIfPositiveResult = struct {
    result: i64,
    changed: bool,
};

const selftest_operation_families = [_]OperationFamily{
    .arithmetic,
    .bitwise,
    .returning_ops,
    .swap_ops,
    .guard_ops,
};

pub const RuntimeAtomic64Sample = struct {
    const Self = @This();

    stage_state: ModuleStage = .cold,
    counter: i64 = 0,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "runtime_atomic64",
            .anchor = "lib/atomic64_test.c",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
        };
    }

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
    }

    fn ensureActive(self: *const Self) !void {
        return switch (self.stage_state) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    fn updateResult(previous: i64, final: i64) CounterUpdate {
        return .{
            .previous = previous,
            .final = final,
        };
    }

    pub fn init(self: *Self, seed: i64) !void {
        if (self.stage_state != .cold) return error.InvalidLifecycleTransition;
        self.counter = seed;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn snapshotCounter(self: *const Self) i64 {
        return self.counter;
    }

    pub fn lifecycleSnapshot(self: *const Self) LifecycleSnapshot {
        return .{
            .stage = self.stage_state,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .allows_counter_ops = switch (self.stage_state) {
                .initialized, .selftest_complete => true,
                else => false,
            },
        };
    }

    pub fn summary(self: *const Self) Summary {
        return .{
            .counter_snapshot = self.counter,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
        };
    }

    pub fn addCounter(self: *Self, delta: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchAdd(i64, &self.counter, delta, .acq_rel);
        return updateResult(previous, previous +% delta);
    }

    pub fn subCounter(self: *Self, delta: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchSub(i64, &self.counter, delta, .acq_rel);
        return updateResult(previous, previous -% delta);
    }

    pub fn addReturnCounter(self: *Self, delta: i64) !i64 {
        const result = try self.addCounter(delta);
        return result.final;
    }

    pub fn subReturnCounter(self: *Self, delta: i64) !i64 {
        const result = try self.subCounter(delta);
        return result.final;
    }

    pub fn incReturnCounter(self: *Self) !i64 {
        return self.addReturnCounter(1);
    }

    pub fn decReturnCounter(self: *Self) !i64 {
        return self.subReturnCounter(1);
    }

    pub fn swapCounter(self: *Self, next: i64) !i64 {
        try self.ensureActive();
        return atomic.exchange(i64, &self.counter, next, .acq_rel);
    }

    pub fn compareSwapCounter(
        self: *Self,
        expected: i64,
        desired: i64,
    ) !CompareSwapResult {
        try self.ensureActive();
        const outcome = try atomic.compareExchangeStrong(
            i64,
            &self.counter,
            expected,
            desired,
            .acq_rel,
            .acquire,
        );
        if (outcome) |previous| {
            return .{
                .previous = previous,
                .stored = false,
            };
        }
        return .{
            .previous = expected,
            .stored = true,
        };
    }

    pub fn addUnlessCounter(
        self: *Self,
        delta: i64,
        unless_value: i64,
    ) !AddUnlessResult {
        try self.ensureActive();

        while (true) {
            const current = try atomic.load(i64, &self.counter, .acquire);
            if (current == unless_value) {
                return .{
                    .previous = current,
                    .changed = false,
                };
            }

            const desired = current +% delta;
            const outcome = try atomic.compareExchangeWeak(
                i64,
                &self.counter,
                current,
                desired,
                .acq_rel,
                .acquire,
            );
            if (outcome == null) {
                return .{
                    .previous = current,
                    .changed = true,
                };
            }
        }
    }

    pub fn incNotZeroCounter(self: *Self) !AddUnlessResult {
        try self.ensureActive();

        while (true) {
            const current = try atomic.load(i64, &self.counter, .acquire);
            if (current == 0) {
                return .{
                    .previous = 0,
                    .changed = false,
                };
            }

            const desired = current +% 1;
            const outcome = try atomic.compareExchangeWeak(
                i64,
                &self.counter,
                current,
                desired,
                .acq_rel,
                .acquire,
            );
            if (outcome == null) {
                return .{
                    .previous = current,
                    .changed = true,
                };
            }
        }
    }

    pub fn decIfPositiveCounter(self: *Self) !DecIfPositiveResult {
        try self.ensureActive();

        while (true) {
            const current = try atomic.load(i64, &self.counter, .acquire);
            const result = current -% 1;
            if (current <= 0) {
                return .{
                    .result = result,
                    .changed = false,
                };
            }

            const outcome = try atomic.compareExchangeWeak(
                i64,
                &self.counter,
                current,
                result,
                .acq_rel,
                .acquire,
            );
            if (outcome == null) {
                return .{
                    .result = result,
                    .changed = true,
                };
            }
        }
    }

    pub fn andCounter(self: *Self, mask: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchAnd(i64, &self.counter, mask, .acq_rel);
        return updateResult(previous, previous & mask);
    }

    pub fn orCounter(self: *Self, mask: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchOr(i64, &self.counter, mask, .acq_rel);
        return updateResult(previous, previous | mask);
    }

    pub fn xorCounter(self: *Self, mask: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchXor(i64, &self.counter, mask, .acq_rel);
        return updateResult(previous, previous ^ mask);
    }

    pub fn andNotCounter(self: *Self, mask: i64) !CounterUpdate {
        try self.ensureActive();
        const previous = try atomic.fetchAnd(i64, &self.counter, ~mask, .acq_rel);
        return updateResult(previous, previous & ~mask);
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage_state != .initialized) return error.InvalidLifecycleTransition;
        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .operation_families = &selftest_operation_families,
            .checked_returning_paths = true,
            .checked_bitwise_paths = true,
            .checked_guard_paths = true,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage_state) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "runtime atomic64 sample keeps descriptor and lifecycle contract explicit" {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeAtomic64Sample{};
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try module.init(7);
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    _ = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
}

test "runtime atomic64 sample keeps arithmetic and guard paths reviewable" {
    var module = RuntimeAtomic64Sample{};
    try module.init(3);

    const add_result = try module.addCounter(4);
    try std.testing.expectEqual(@as(i64, 3), add_result.previous);
    try std.testing.expectEqual(@as(i64, 7), add_result.final);

    const cmp_result = try module.compareSwapCounter(7, 11);
    try std.testing.expect(cmp_result.stored);
    try std.testing.expectEqual(@as(i64, 7), cmp_result.previous);
    try std.testing.expectEqual(@as(i64, 11), module.snapshotCounter());

    const dec_positive = try module.decIfPositiveCounter();
    try std.testing.expect(dec_positive.changed);
    try std.testing.expectEqual(@as(i64, 10), dec_positive.result);

    const add_unless = try module.addUnlessCounter(5, 99);
    try std.testing.expect(add_unless.changed);
    try std.testing.expectEqual(@as(i64, 10), add_unless.previous);

    _ = try module.runSelftest();
    const inc_not_zero = try module.incNotZeroCounter();
    try std.testing.expect(inc_not_zero.changed);
    try std.testing.expectEqual(@as(i64, 15), inc_not_zero.previous);
}

test "runtime atomic64 sample rejects re-selftest without disturbing lifecycle summaries" {
    var module = RuntimeAtomic64Sample{};
    try module.init(23);
    _ = try module.runSelftest();

    const before_rejected_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(i64, 23), before_rejected_selftest.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(before_rejected_selftest.counter_snapshot, after_rejected_selftest.counter_snapshot);
    try std.testing.expectEqual(before_rejected_selftest.init_runs, after_rejected_selftest.init_runs);
    try std.testing.expectEqual(before_rejected_selftest.selftest_runs, after_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(before_rejected_selftest.exit_runs, after_rejected_selftest.exit_runs);

    try module.exit();

    const before_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(i64, 23), before_rejected_exit_selftest.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(before_rejected_exit_selftest.counter_snapshot, after_rejected_exit_selftest.counter_snapshot);
    try std.testing.expectEqual(before_rejected_exit_selftest.init_runs, after_rejected_exit_selftest.init_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest.selftest_runs, after_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(before_rejected_exit_selftest.exit_runs, after_rejected_exit_selftest.exit_runs);
}