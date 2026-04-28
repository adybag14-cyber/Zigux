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
    parse_and_print,
    iteration_and_ranges,
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
    checked_iteration_paths: bool,
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

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
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

    fn assignBit(self: *Self, bit: u32, value: bool) void {
        const word_index: usize = @intCast(bit / bitmap_view.bits_per_long);
        const bit_index: u6 = @intCast(bit % bitmap_view.bits_per_long);
        const mask: bitmap_view.Word = @as(bitmap_view.Word, 1) << bit_index;
        if (value) {
            self.words[word_index] |= mask;
        } else {
            self.words[word_index] &= ~mask;
        }
    }

    pub fn initWithSetBits(self: *Self, bits: []const u32) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        @memset(self.words[0..], 0);
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            self.assignBit(bit, true);
        }

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
                .parse_and_print,
                .iteration_and_ranges,
            },
            .checked_range_mutations = true,
            .checked_iteration_paths = true,
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

test "runtime bitmap sample keeps bounded view summaries stable" {
    var module = RuntimeBitmapSample{};

    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap sample selftest keeps the bounded review contract explicit" {
    const descriptor = RuntimeBitmapSample.descriptor();
    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const summary_before_selftest = module.summary();
    const selftest = try module.runSelftest();

    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqualStrings(descriptor.anchor, selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(OperationFamily.clear_set, selftest.operation_families[0]);
    try std.testing.expectEqual(OperationFamily.copy, selftest.operation_families[1]);
    try std.testing.expectEqual(OperationFamily.parse_and_print, selftest.operation_families[2]);
    try std.testing.expectEqual(OperationFamily.iteration_and_ranges, selftest.operation_families[3]);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);
    try std.testing.expectEqual(@as(usize, 1), module.selftest_runs);

    const summary_after_selftest = module.summary();
    try std.testing.expectEqual(summary_before_selftest.first_set, summary_after_selftest.first_set);
    try std.testing.expectEqual(summary_before_selftest.first_zero, summary_after_selftest.first_zero);
    try std.testing.expectEqual(summary_before_selftest.weight, summary_after_selftest.weight);
    try std.testing.expectEqual(summary_before_selftest.nbits, summary_after_selftest.nbits);
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
}

test "runtime bitmap sample keeps post-selftest mutation replay explicit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });
    _ = try module.runSelftest();

    try module.clearRange(bitmap_view.bits_per_long, 2);
    try module.setRange(9, 4);

    const summary_after_mutation = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(u32, 0), summary_after_mutation.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary_after_mutation.first_zero);
    try std.testing.expectEqual(@as(u32, 7), summary_after_mutation.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary_after_mutation.nbits);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!module.isSet(bitmap_view.bits_per_long));

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(summary_after_mutation.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(summary_after_mutation.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(summary_after_mutation.weight, mirror_summary.weight);
    try std.testing.expect(mirror.isSet(12));
    try std.testing.expect(mirror.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!mirror.isSet(bitmap_view.bits_per_long));
}

test "runtime bitmap sample keeps exit lifecycle and post-exit snapshot explicit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });
    try module.clearRange(bitmap_view.bits_per_long, 2);
    try module.setRange(9, 4);
    _ = try module.runSelftest();

    const summary_before_exit = module.summary();
    try module.exit();

    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!module.isSet(bitmap_view.bits_per_long));

    const summary_after_exit = module.summary();
    try std.testing.expectEqual(summary_before_exit.first_set, summary_after_exit.first_set);
    try std.testing.expectEqual(summary_before_exit.first_zero, summary_after_exit.first_zero);
    try std.testing.expectEqual(summary_before_exit.weight, summary_after_exit.weight);
    try std.testing.expectEqual(summary_before_exit.nbits, summary_after_exit.nbits);

    var source = RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 2, 9 });
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.copyFrom(&source));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}
