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

pub const SelftestSummary = struct {
    anchor: []const u8,
    operation_families: []const OperationFamily,
    checked_returning_paths: bool,
    checked_guard_paths: bool,
};

pub const RuntimeAtomic64Summary = struct {
    counter_snapshot: i64,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
};

pub const CompareExchangeResult = struct {
    previous: i64,
    stored: bool,
};

pub const AddResult = struct {
    previous: i64,
    final: i64,
};

pub const AddUnlessResult = struct {
    previous: i64,
    changed: bool,
};

pub const IncNotZeroResult = struct {
    previous: i64,
    changed: bool,
};

pub const DecIfPositiveResult = struct {
    result: i64,
    changed: bool,
};

pub const RuntimeAtomic64Sample = struct {
    const Self = @This();

    stage_bits: u8 = @intFromEnum(ModuleStage.cold),
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
        return @enumFromInt(atomic.load(u8, &self.stage_bits, .seq_cst));
    }

    fn setStage(self: *Self, next: ModuleStage) void {
        atomic.store(u8, &self.stage_bits, @intFromEnum(next), .seq_cst);
    }

    pub fn init(self: *Self, seed: i64) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        atomic.store(i64, &self.counter, seed, .seq_cst);
        self.init_runs += 1;
        self.setStage(.initialized);
    }

    pub fn snapshotCounter(self: *const Self) i64 {
        return atomic.load(i64, &self.counter, .seq_cst);
    }

    pub fn swapCounter(self: *Self, next: i64) !i64 {
        return switch (self.stage()) {
            .initialized, .selftest_complete => atomic.exchange(i64, &self.counter, next, .seq_cst),
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn compareSwapCounter(self: *Self, expected: i64, desired: i64) !CompareExchangeResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const mismatch = atomic.compareExchange(
                    i64,
                    &self.counter,
                    expected,
                    desired,
                    .seq_cst,
                    .seq_cst,
                );
                break :blk if (mismatch) |previous|
                    .{ .previous = previous, .stored = false }
                else
                    .{ .previous = expected, .stored = true };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn addCounter(self: *Self, addend: i64) !AddResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchAdd(i64, &self.counter, addend, .seq_cst);
                break :blk .{ .previous = previous, .final = previous + addend };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn addUnlessCounter(self: *Self, addend: i64, unless_value: i64) !AddUnlessResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                var current = atomic.load(i64, &self.counter, .seq_cst);
                while (true) {
                    if (current == unless_value) {
                        break :blk .{ .previous = current, .changed = false };
                    }

                    const next = current + addend;
                    const mismatch = atomic.compareExchange(
                        i64,
                        &self.counter,
                        current,
                        next,
                        .seq_cst,
                        .seq_cst,
                    );
                    if (mismatch) |previous| {
                        current = previous;
                        continue;
                    }

                    break :blk .{ .previous = current, .changed = true };
                }
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn incNotZeroCounter(self: *Self) !IncNotZeroResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                var current = atomic.load(i64, &self.counter, .seq_cst);
                while (true) {
                    if (current == 0) {
                        break :blk .{ .previous = current, .changed = false };
                    }

                    const next = current + 1;
                    const mismatch = atomic.compareExchange(
                        i64,
                        &self.counter,
                        current,
                        next,
                        .seq_cst,
                        .seq_cst,
                    );
                    if (mismatch) |previous| {
                        current = previous;
                        continue;
                    }

                    break :blk .{ .previous = current, .changed = true };
                }
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn decIfPositiveCounter(self: *Self) !DecIfPositiveResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                var current = atomic.load(i64, &self.counter, .seq_cst);
                while (true) {
                    const result = current - 1;
                    if (current <= 0) {
                        break :blk .{ .result = result, .changed = false };
                    }

                    const mismatch = atomic.compareExchange(
                        i64,
                        &self.counter,
                        current,
                        result,
                        .seq_cst,
                        .seq_cst,
                    );
                    if (mismatch) |previous| {
                        current = previous;
                        continue;
                    }

                    break :blk .{ .result = result, .changed = true };
                }
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.selftest_runs += 1;
        self.setStage(.selftest_complete);
        return .{
            .anchor = descriptor().anchor,
            .operation_families = &.{
                .arithmetic,
                .bitwise,
                .returning_ops,
                .swap_ops,
                .guard_ops,
            },
            .checked_returning_paths = true,
            .checked_guard_paths = true,
        };
    }

    pub fn summary(self: *const Self) RuntimeAtomic64Summary {
        return .{
            .counter_snapshot = self.snapshotCounter(),
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.exit_runs += 1;
        self.setStage(.exited);
    }
};

test "runtime atomic64 sample keeps post-selftest counter replay and summary explicit" {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeAtomic64Sample{};
    const cold_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 0), cold_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);

    try module.init(41);
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 41), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_returning_paths);
    try std.testing.expect(selftest.checked_guard_paths);

    const add_after_selftest = try module.addCounter(-9);
    try std.testing.expectEqual(@as(i64, 41), add_after_selftest.previous);
    try std.testing.expectEqual(@as(i64, 32), add_after_selftest.final);

    const swap_after_selftest = try module.swapCounter(7);
    try std.testing.expectEqual(@as(i64, 32), swap_after_selftest);
    try std.testing.expectEqual(@as(i64, 7), module.snapshotCounter());

    const selftest_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 7), selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftest_summary.exit_runs);

    try module.exit();
    const exited_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 7), exited_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);
}
