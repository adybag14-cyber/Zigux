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

pub const BitwiseResult = struct {
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

    pub fn subCounter(self: *Self, subtrahend: i64) !AddResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchSub(i64, &self.counter, subtrahend, .seq_cst);
                break :blk .{ .previous = previous, .final = previous - subtrahend };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn orCounter(self: *Self, mask: i64) !BitwiseResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchOr(i64, &self.counter, mask, .seq_cst);
                break :blk .{ .previous = previous, .final = previous | mask };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn andCounter(self: *Self, mask: i64) !BitwiseResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchAnd(i64, &self.counter, mask, .seq_cst);
                break :blk .{ .previous = previous, .final = previous & mask };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn xorCounter(self: *Self, mask: i64) !BitwiseResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchXor(i64, &self.counter, mask, .seq_cst);
                break :blk .{ .previous = previous, .final = previous ^ mask };
            },
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn andNotCounter(self: *Self, mask: i64) !BitwiseResult {
        return switch (self.stage()) {
            .initialized, .selftest_complete => blk: {
                const previous = atomic.fetchAnd(i64, &self.counter, ~mask, .seq_cst);
                break :blk .{ .previous = previous, .final = previous & ~mask };
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
                    const mismatch = atomic.compareExchange(i64, &self.counter, current, next, .seq_cst, .seq_cst);
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
                    const mismatch = atomic.compareExchange(i64, &self.counter, current, next, .seq_cst, .seq_cst);
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
                    const mismatch = atomic.compareExchange(i64, &self.counter, current, result, .seq_cst, .seq_cst);
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
        return .{ .anchor = descriptor().anchor, .operation_families = &.{ .arithmetic, .bitwise, .returning_ops, .swap_ops, .guard_ops }, .checked_returning_paths = true, .checked_guard_paths = true };
    }

    pub fn summary(self: *const Self) RuntimeAtomic64Summary {
        return .{ .counter_snapshot = self.snapshotCounter(), .init_runs = self.init_runs, .selftest_runs = self.selftest_runs, .exit_runs = self.exit_runs };
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

test "runtime atomic64 sample keeps lifecycle replay and summary accounting explicit" {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeAtomic64Sample{};
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    const cold_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 0), cold_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold_summary.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());

    try module.init(5);
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    const initialized_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 5), initialized_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_summary.exit_runs);

    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 5), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_returning_paths);
    try std.testing.expect(selftest.checked_guard_paths);

    const add_result = try module.addCounter(7);
    try std.testing.expectEqual(@as(i64, 5), add_result.previous);
    try std.testing.expectEqual(@as(i64, 12), add_result.final);

    const post_selftest_or = try module.orCounter(0b0100);
    try std.testing.expectEqual(@as(i64, 12), post_selftest_or.previous);
    try std.testing.expectEqual(@as(i64, 12), post_selftest_or.final);

    const post_selftest_and = try module.andCounter(0b1110);
    try std.testing.expectEqual(@as(i64, 12), post_selftest_and.previous);
    try std.testing.expectEqual(@as(i64, 12), post_selftest_and.final);

    const post_selftest_xor = try module.xorCounter(0b0011);
    try std.testing.expectEqual(@as(i64, 12), post_selftest_xor.previous);
    try std.testing.expectEqual(@as(i64, 15), post_selftest_xor.final);

    const post_selftest_andnot = try module.andNotCounter(0b0100);
    try std.testing.expectEqual(@as(i64, 15), post_selftest_andnot.previous);
    try std.testing.expectEqual(@as(i64, 11), post_selftest_andnot.final);

    const compare_mismatch = try module.compareSwapCounter(19, 31);
    try std.testing.expect(!compare_mismatch.stored);
    try std.testing.expectEqual(@as(i64, 11), compare_mismatch.previous);
    try std.testing.expectEqual(@as(i64, 11), module.snapshotCounter());

    const compare_stored = try module.compareSwapCounter(11, 19);
    try std.testing.expect(compare_stored.stored);
    try std.testing.expectEqual(@as(i64, 11), compare_stored.previous);
    try std.testing.expectEqual(@as(i64, 19), module.snapshotCounter());

    const add_unless_blocked = try module.addUnlessCounter(5, 19);
    try std.testing.expect(!add_unless_blocked.changed);
    try std.testing.expectEqual(@as(i64, 19), add_unless_blocked.previous);

    const add_unless_changed = try module.addUnlessCounter(-4, 99);
    try std.testing.expect(add_unless_changed.changed);
    try std.testing.expectEqual(@as(i64, 19), add_unless_changed.previous);
    try std.testing.expectEqual(@as(i64, 15), module.snapshotCounter());

    const inc_not_zero = try module.incNotZeroCounter();
    try std.testing.expect(inc_not_zero.changed);
    try std.testing.expectEqual(@as(i64, 15), inc_not_zero.previous);
    try std.testing.expectEqual(@as(i64, 16), module.snapshotCounter());

    const dec_if_positive = try module.decIfPositiveCounter();
    try std.testing.expect(dec_if_positive.changed);
    try std.testing.expectEqual(@as(i64, 15), dec_if_positive.result);
    try std.testing.expectEqual(@as(i64, 15), module.snapshotCounter());

    const swapped = try module.swapCounter(19);
    try std.testing.expectEqual(@as(i64, 15), swapped);
    try std.testing.expectEqual(@as(i64, 19), module.snapshotCounter());

    const post_selftest_summary = module.summary();
    try std.testing.expectEqual(@as(i64, 19), post_selftest_summary.counter_snapshot);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 1), post_selftest_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), post_selftest_summary.exit_runs);

    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
}
