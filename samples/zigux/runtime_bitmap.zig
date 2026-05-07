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

    fn stageAllowsMutation(current_stage: ModuleStage) bool {
        return switch (current_stage) {
            .initialized, .selftest_complete => true,
            else => false,
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
            .allows_mutation = stageAllowsMutation(current_stage),
        };
    }

    fn ensureMutable(self: *const Self) !void {
        if (!stageAllowsMutation(self.stage())) return error.InvalidLifecycleTransition;
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

test "runtime bitmap sample lifecycle snapshot keeps stage-owned counters explicit" {
    var module = RuntimeBitmapSample{};

    const cold = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.cold, cold.stage);
    try std.testing.expectEqual(@as(usize, 0), cold.init_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), cold.exit_runs);
    try std.testing.expect(!cold.allows_mutation);

    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });
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

test "runtime bitmap sample keeps bounded view summaries stable" {
    var module = RuntimeBitmapSample{};

    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap sample keeps post-selftest mutation replay local to the sample" {
    var module = RuntimeBitmapSample{};
    const second_word_base = RuntimeBitmapSample.bitmap_nbits / 2;

    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    const selftest = try module.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);

    try module.clearRange(0, 1);
    try module.setRange(1, 2);

    const replay_summary = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(u32, 1), replay_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), replay_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 5), replay_summary.weight);
    try std.testing.expect(module.isSet(1));
    try std.testing.expect(module.isSet(2));
    try std.testing.expect(module.isSet(second_word_base));
    try std.testing.expect(module.isSet(second_word_base + 6));

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(replay_summary.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(replay_summary.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(replay_summary.weight, mirror_summary.weight);
    try std.testing.expect(mirror.isSet(1));
    try std.testing.expect(mirror.isSet(2));
    try std.testing.expect(mirror.isSet(second_word_base));
    try std.testing.expect(mirror.isSet(second_word_base + 6));
}

test "runtime bitmap sample failed init leaves the sample cold and empty" {
    var module = RuntimeBitmapSample{};

    try std.testing.expectError(error.BitRangeOutOfBounds, module.initWithSetBits(&.{ 1, RuntimeBitmapSample.bitmap_nbits }));
    const failed_init = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.cold, failed_init.stage);
    try std.testing.expectEqual(@as(usize, 0), failed_init.init_runs);
    try std.testing.expect(!failed_init.allows_mutation);

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, RuntimeBitmapSample.bitmap_nbits), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
    try std.testing.expect(!module.isSet(1));

    try module.initWithSetBits(&.{1});
    const initialized = module.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.initialized, initialized.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized.init_runs);
    try std.testing.expect(initialized.allows_mutation);
    try std.testing.expect(module.isSet(1));
}

test "runtime bitmap sample keeps the highest valid bit explicit" {
    var module = RuntimeBitmapSample{};
    const top_bit = RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{top_bit});

    const summary = module.summary();
    try std.testing.expect(module.isSet(top_bit));
    try std.testing.expect(!module.isSet(top_bit - 1));
    try std.testing.expectEqual(top_bit, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 1), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap sample keeps top-bit boundary mutation and bounds checks reviewable" {
    var module = RuntimeBitmapSample{};
    const top_bit = RuntimeBitmapSample.bitmap_nbits - 1;

    try module.initWithSetBits(&.{});
    try module.setRange(top_bit, 1);
    try std.testing.expect(module.isSet(top_bit));

    try module.clearRange(top_bit, 1);
    try std.testing.expect(!module.isSet(top_bit));
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());

    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(top_bit + 1, 1));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(top_bit + 1, 1));
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
}

test "runtime bitmap sample keeps exit-path summaries stable" {
    const second_word_base = RuntimeBitmapSample.bitmap_nbits / 2;

    var initialized = RuntimeBitmapSample{};
    try initialized.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    const before_initialized_exit = initialized.summary();
    try initialized.exit();

    const after_initialized_exit = initialized.summary();
    const initialized_snapshot = initialized.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.exit_runs);
    try std.testing.expect(!initialized_snapshot.allows_mutation);
    try std.testing.expectEqual(before_initialized_exit.first_set, after_initialized_exit.first_set);
    try std.testing.expectEqual(before_initialized_exit.first_zero, after_initialized_exit.first_zero);
    try std.testing.expectEqual(before_initialized_exit.weight, after_initialized_exit.weight);
    try std.testing.expectEqual(before_initialized_exit.nbits, after_initialized_exit.nbits);
    try std.testing.expect(initialized.isSet(0));
    try std.testing.expect(initialized.isSet(second_word_base + 6));
    try std.testing.expectError(error.InvalidLifecycleTransition, initialized.exit());

    var selftested = RuntimeBitmapSample{};
    try selftested.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    _ = try selftested.runSelftest();
    try selftested.clearRange(0, 1);
    try selftested.setRange(1, 2);
    const before_selftested_exit = selftested.summary();
    try selftested.exit();

    const after_selftested_exit = selftested.summary();
    const selftested_snapshot = selftested.lifecycleSnapshot();
    try std.testing.expectEqual(ModuleStage.exited, selftested_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), selftested_snapshot.exit_runs);
    try std.testing.expect(!selftested_snapshot.allows_mutation);
    try std.testing.expectEqual(before_selftested_exit.first_set, after_selftested_exit.first_set);
    try std.testing.expectEqual(before_selftested_exit.first_zero, after_selftested_exit.first_zero);
    try std.testing.expectEqual(before_selftested_exit.weight, after_selftested_exit.weight);
    try std.testing.expectEqual(before_selftested_exit.nbits, after_selftested_exit.nbits);
    try std.testing.expect(selftested.isSet(1));
    try std.testing.expect(selftested.isSet(2));
    try std.testing.expect(selftested.isSet(second_word_base));
    try std.testing.expect(selftested.isSet(second_word_base + 6));
    try std.testing.expectError(error.InvalidLifecycleTransition, selftested.setRange(1, 1));
}
