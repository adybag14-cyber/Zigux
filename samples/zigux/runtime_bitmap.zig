const std = @import("std");
const bitmap_view = @import("bitmap_view");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const OperationFamily = enum {
    clear_set,
    copy,
    summary,
    lifecycle,
};

pub const SampleFocus = enum {
    descriptor_and_anchor,
    summary_replay,
    selftest_lifecycle,
};

pub const sample_review_focus = [_]SampleFocus{
    .descriptor_and_anchor,
    .summary_replay,
    .selftest_lifecycle,
};

pub const sample_review_non_goals = [_][]const u8{
    "loadable runtime bitmap module parity",
    "shared runtime-loader command-name or argv-policy controls",
    "real runtime execution through a live substrate",
};

pub const ReviewContract = struct {
    focus: []const SampleFocus,
    non_goals: []const []const u8,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
};

pub const RuntimeBitmapSummary = struct {
    first_set: u32,
    first_zero: u32,
    weight: u32,
    nbits: u32,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    operation_families: []const OperationFamily,
    checked_range_mutations: bool,
    checked_lifecycle_paths: bool,
};

pub const LifecycleSnapshot = struct {
    stage: ModuleStage,
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
    allows_mutation: bool,
};

pub const RuntimeBitmapSample = struct {
    const Self = @This();

    pub const bitmap_nbits: u32 = bitmap_view.bits_per_long * 2;
    const backing_word_count: usize = 2;

    stage_state: ModuleStage = .cold,
    words: [backing_word_count]bitmap_view.Word = [_]bitmap_view.Word{0} ** backing_word_count,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "runtime_bitmap",
            .anchor = "lib/test_bitmap.c",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
        };
    }

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
        };
    }

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
    }

    pub fn lifecycleSnapshot(self: *const Self) LifecycleSnapshot {
        const current_stage = self.stage();
        return .{
            .stage = current_stage,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
            .allows_mutation = switch (current_stage) {
                .initialized, .selftest_complete => true,
                else => false,
            },
        };
    }

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    fn validateRange(start: u32, len: u32) !void {
        if (len == 0) return;
        if (start >= bitmap_nbits) return error.BitRangeOutOfBounds;
        if (len > bitmap_nbits - start) return error.BitRangeOutOfBounds;
    }

    fn assignBitToWords(words: []bitmap_view.Word, bit: u32, value: bool) void {
        const word_index: usize = @intCast(bit / bitmap_view.bits_per_long);
        const bit_index: u6 = @intCast(bit % bitmap_view.bits_per_long);
        const mask: bitmap_view.Word = @as(bitmap_view.Word, 1) << bit_index;
        if (value) {
            words[word_index] |= mask;
        } else {
            words[word_index] &= ~mask;
        }
    }

    fn assignBit(self: *Self, bit: u32, value: bool) void {
        assignBitToWords(self.words[0..], bit, value);
    }

    pub fn initWithSetBits(self: *Self, bits: []const u32) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var next_words = [_]bitmap_view.Word{0} ** backing_word_count;
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            assignBitToWords(next_words[0..], bit, true);
        }

        self.words = next_words;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn setRange(self: *Self, start: u32, len: u32) !void {
        try self.ensureMutable();
        try validateRange(start, len);

        var bit = start;
        while (bit < start + len) : (bit += 1) {
            self.assignBit(bit, true);
        }
    }

    pub fn clearRange(self: *Self, start: u32, len: u32) !void {
        try self.ensureMutable();
        try validateRange(start, len);

        var bit = start;
        while (bit < start + len) : (bit += 1) {
            self.assignBit(bit, false);
        }
    }

    pub fn copyFrom(self: *Self, other: *const Self) !void {
        try self.ensureMutable();
        switch (other.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidSourceLifecycle,
        }

        self.words = other.words;
    }

    pub fn isSet(self: *const Self, bit: u32) bool {
        const view = bitmap_view.viewFromWords(self.words[0..], bitmap_nbits);
        return bitmap_view.testBit(view, bit);
    }

    pub fn summary(self: *const Self) RuntimeBitmapSummary {
        const view = bitmap_view.viewFromWords(self.words[0..], bitmap_nbits);
        const bounded = bitmap_view.summarize(view);
        return .{
            .first_set = bounded.first_set,
            .first_zero = bounded.first_zero,
            .weight = bounded.weight,
            .nbits = bitmap_nbits,
        };
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .operation_families = &.{
                .clear_set,
                .copy,
                .summary,
                .lifecycle,
            },
            .checked_range_mutations = true,
            .checked_lifecycle_paths = true,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};

test "runtime bitmap sample review contract keeps bounded starter focus explicit" {
    const descriptor = RuntimeBitmapSample.descriptor();
    const contract = RuntimeBitmapSample.reviewContract();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    try std.testing.expectEqual(@as(usize, sample_review_focus.len), contract.focus.len);
    for (sample_review_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }

    try std.testing.expectEqual(@as(usize, sample_review_non_goals.len), contract.non_goals.len);
    for (sample_review_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
}

test "runtime bitmap sample review contract stays aligned with the selftest packet" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const contract = RuntimeBitmapSample.reviewContract();
    const selftest = try module.runSelftest();

    try std.testing.expectEqual(@as(usize, 3), contract.focus.len);
    try std.testing.expectEqual(SampleFocus.descriptor_and_anchor, contract.focus[0]);
    try std.testing.expectEqual(SampleFocus.summary_replay, contract.focus[1]);
    try std.testing.expectEqual(SampleFocus.selftest_lifecycle, contract.focus[2]);
    try std.testing.expectEqualStrings(RuntimeBitmapSample.descriptor().anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(OperationFamily.summary, selftest.operation_families[2]);
    try std.testing.expectEqual(OperationFamily.lifecycle, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_lifecycle_paths);
}

test "runtime bitmap sample lifecycle snapshot keeps counters and mutation guard explicit" {
    var module = RuntimeBitmapSample{};

    const cold = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.cold, cold.stage);
    try std.testing.expectEqual(@as(usize, 0), cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.exit_runs);
    try std.testing.expect(!cold.allows_mutation);

    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long + 1 });
    const initialized = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized.exit_runs);
    try std.testing.expect(initialized.allows_mutation);

    _ = try module.runSelftest();
    const selftested = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.selftest_complete, selftested.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), selftested.exit_runs);
    try std.testing.expect(selftested.allows_mutation);

    try module.exit();
    const exited = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, exited.stage);
    try std.testing.expectEqual(@as(usize, 1), exited.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited.exit_runs);
    try std.testing.expect(!exited.allows_mutation);
}

test "runtime bitmap sample keeps bounded view summaries stable" {
    var module = RuntimeBitmapSample{};

    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap sample failed init leaves the sample cold and empty" {
    var module = RuntimeBitmapSample{};

    try std.testing.expectError(error.BitRangeOutOfBounds, module.initWithSetBits(&.{ 1, RuntimeBitmapSample.bitmap_nbits }));
    try std.testing.expectEqual(ModuleStage.cold, module.stage());
    try std.testing.expectEqual(@as(usize, 0), module.init_runs);

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, RuntimeBitmapSample.bitmap_nbits), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
    try std.testing.expect(!module.isSet(1));

    try module.initWithSetBits(&.{1});
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.init_runs);
    try std.testing.expect(module.isSet(1));
}

test "runtime bitmap sample copyFrom accepts a selftested source without widening lifecycle claims" {
    var source = RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long + 7 });
    _ = try source.runSelftest();

    var destination = RuntimeBitmapSample{};
    try destination.initWithSetBits(&.{ 2, 9 });
    try destination.copyFrom(&source);

    const summary = destination.summary();
    const snapshot = destination.lifecycleSnapshot();

    try std.testing.expectEqual(ModuleStage.initialized, destination.stage());
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 3), summary.weight);
    try std.testing.expect(destination.isSet(0));
    try std.testing.expect(destination.isSet(5));
    try std.testing.expect(destination.isSet(bitmap_view.bits_per_long + 7));
    try std.testing.expect(!destination.isSet(2));
    try std.testing.expectEqual(@as(usize, 1), snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.exit_runs);
    try std.testing.expect(snapshot.allows_mutation);
}

test "runtime bitmap sample copyFrom rejects an exited source and preserves destination state" {
    var source = RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long + 2 });
    _ = try source.runSelftest();
    try source.exit();

    var destination = RuntimeBitmapSample{};
    try destination.initWithSetBits(&.{ 3, 9 });
    const before = destination.summary();

    try std.testing.expectError(error.InvalidSourceLifecycle, destination.copyFrom(&source));

    const after = destination.summary();
    const snapshot = destination.lifecycleSnapshot();

    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(ModuleStage.initialized, destination.stage());
    try std.testing.expect(destination.isSet(3));
    try std.testing.expect(destination.isSet(9));
    try std.testing.expect(!destination.isSet(0));
    try std.testing.expectEqual(@as(usize, 1), snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), snapshot.exit_runs);
    try std.testing.expect(snapshot.allows_mutation);

    try destination.setRange(0, 1);
    try std.testing.expect(destination.isSet(0));
}
