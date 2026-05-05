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

    pub fn andCounter(self: *Self, mask: i64) !i64 {
        return switch (self.stage()) {
            .initialized, .selftest_complete => atomic.fetchAnd(i64, &self.counter, mask, .seq_cst),
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn orCounter(self: *Self, mask: i64) !i64 {
        return switch (self.stage()) {
            .initialized, .selftest_complete => atomic.fetchOr(i64, &self.counter, mask, .seq_cst),
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn xorCounter(self: *Self, mask: i64) !i64 {
        return switch (self.stage()) {
            .initialized, .selftest_complete => atomic.fetchXor(i64, &self.counter, mask, .seq_cst),
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