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
    checked_bitwise_paths: bool,
    checked_guard_paths: bool,
};

pub const CompareExchangeResult = struct {
    previous: i64,
    stored: bool,
};

pub const AddUnlessResult = struct {
    previous: i64,
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

    fn ensureActive(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
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

    pub fn addCounter(self: *Self, addend: i64) !void {
        try self.ensureActive();
        _ = atomic.fetchAdd(i64, &self.counter, addend, .seq_cst);
    }

    pub fn subCounter(self: *Self, subtrahend: i64) !void {
        try self.ensureActive();
        _ = atomic.fetchSub(i64, &self.counter, subtrahend, .seq_cst);
    }

    pub fn fetchAddCounter(self: *Self, addend: i64) !i64 {
        try self.ensureActive();
        return atomic.fetchAdd(i64, &self.counter, addend, .seq_cst);
    }

    pub fn fetchSubCounter(self: *Self, subtrahend: i64) !i64 {
        try self.ensureActive();
        return atomic.fetchSub(i64, &self.counter, subtrahend, .seq_cst);
    }

    pub fn addReturnCounter(self: *Self, addend: i64) !i64 {
        return (try self.fetchAddCounter(addend)) + addend;
    }

    pub fn subReturnCounter(self: *Self, subtrahend: i64) !i64 {
        return (try self.fetchSubCounter(subtrahend)) - subtrahend;
    }

    pub fn incCounter(self: *Self) !void {
        try self.addCounter(1);
    }

    pub fn decCounter(self: *Self) !void {
        try self.subCounter(1);
    }

    pub fn incReturnCounter(self: *Self) !i64 {
        return self.addReturnCounter(1);
    }

    pub fn decReturnCounter(self: *Self) !i64 {
        return self.subReturnCounter(1);
    }

    pub fn swapCounter(self: *Self, next: i64) !i64 {
        try self.ensureActive();
        return atomic.exchange(i64, &self.counter, next, .seq_cst);
    }

    pub fn andCounter(self: *Self, mask: i64) !i64 {
        try self.ensureActive();
        return atomic.fetchAnd(i64, &self.counter, mask, .seq_cst);
    }

    pub fn orCounter(self: *Self, mask: i64) !i64 {
        try self.ensureActive();
        return atomic.fetchOr(i64, &self.counter, mask, .seq_cst);
    }

    pub fn xorCounter(self: *Self, mask: i64) !i64 {
        try self.ensureActive();
        return atomic.fetchXor(i64, &self.counter, mask, .seq_cst);
    }

    pub fn compareSwapCounter(self: *Self, expected: i64, desired: i64) !CompareExchangeResult {
        try self.ensureActive();
        const mismatch = atomic.compareExchange(
            i64,
            &self.counter,
            expected,
            desired,
            .seq_cst,
            .seq_cst,
        );
        return if (mismatch) |previous|
            .{ .previous = previous, .stored = false }
        else
            .{ .previous = expected, .stored = true };
    }

    pub fn addUnlessCounter(self: *Self, addend: i64, unless_value: i64) !AddUnlessResult {
        try self.ensureActive();
        var current = atomic.load(i64, &self.counter, .seq_cst);
        while (true) {
            if (current == unless_value) {
                return .{ .previous = current, .changed = false };
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

            return .{ .previous = current, .changed = true };
        }
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
            .checked_bitwise_paths = true,
            .checked_guard_paths = true,
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

test "runtime atomic64 sample keeps selftest-complete replay local to the sample" {
    const descriptor = RuntimeAtomic64Sample.descriptor();
    try std.testing.expectEqualStrings("runtime_atomic64", descriptor.name);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeAtomic64Sample{};
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    try module.init(0x1111_1111_2222_2222);
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), module.snapshotCounter());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);

    try module.addCounter(4);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2226), module.snapshotCounter());
    try module.subCounter(2);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2224), module.snapshotCounter());

    const previous_add = try module.fetchAddCounter(-3);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2224), previous_add);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2221), module.snapshotCounter());

    const previous_sub = try module.fetchSubCounter(5);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2221), previous_sub);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221c), module.snapshotCounter());

    const added = try module.addReturnCounter(6);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), added);
    const subtracted = try module.subReturnCounter(4);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), subtracted);
    const incremented = try module.incReturnCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221f), incremented);
    const decremented = try module.decReturnCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), decremented);
    try module.incCounter();
    try module.decCounter();
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), module.snapshotCounter());

    const seeded_swap = try module.swapCounter(-9);
    try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_221e), seeded_swap);
    try std.testing.expectEqual(@as(i64, -9), module.snapshotCounter());

    const initialized_compare = try module.compareSwapCounter(-9, 17);
    try std.testing.expect(initialized_compare.stored);
    try std.testing.expectEqual(@as(i64, -9), initialized_compare.previous);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    const initialized_summary = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings("lib/atomic64_test.c", initialized_summary.anchor);
    try std.testing.expectEqual(@as(usize, 5), initialized_summary.operation_families.len);
    try std.testing.expect(initialized_summary.checked_returning_paths);
    try std.testing.expect(initialized_summary.checked_bitwise_paths);
    try std.testing.expect(initialized_summary.checked_guard_paths);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const replay_swap = try module.swapCounter(23);
    try std.testing.expectEqual(@as(i64, 17), replay_swap);
    try std.testing.expectEqual(@as(i64, 23), module.snapshotCounter());

    const replay_compare = try module.compareSwapCounter(23, 31);
    try std.testing.expect(replay_compare.stored);
    try std.testing.expectEqual(@as(i64, 23), replay_compare.previous);
    try std.testing.expectEqual(@as(i64, 31), module.snapshotCounter());

    const replay_add_unless = try module.addUnlessCounter(4, 99);
    try std.testing.expect(replay_add_unless.changed);
    try std.testing.expectEqual(@as(i64, 31), replay_add_unless.previous);
    try std.testing.expectEqual(@as(i64, 35), module.snapshotCounter());

    const and_previous = try module.andCounter(0b1_1111);
    try std.testing.expectEqual(@as(i64, 35), and_previous);
    try std.testing.expectEqual(@as(i64, 3), module.snapshotCounter());

    const xor_previous = try module.xorCounter(0b1_0010);
    try std.testing.expectEqual(@as(i64, 3), xor_previous);
    try std.testing.expectEqual(@as(i64, 17), module.snapshotCounter());

    try module.exit();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.fetchAddCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addReturnCounter(1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.incReturnCounter());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 17));
}
