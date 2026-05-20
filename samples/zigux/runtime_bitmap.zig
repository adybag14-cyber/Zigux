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
    first_set: usize,
    first_zero: usize,
    weight: usize,
    nbits: usize,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    operation_families: []const OperationFamily,
    checked_range_mutations: bool,
    checked_iteration_paths: bool,
};

pub const RuntimeBitmapSample = struct {
    const Self = @This();

    pub const bitmap_nbits: usize = bitmap_view.word_bits * 2;
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

    fn validateRange(start: usize, len: usize) !void {
        if (len == 0) return;
        if (start >= bitmap_nbits) return error.BitRangeOutOfBounds;
        if (len > bitmap_nbits - start) return error.BitRangeOutOfBounds;
    }

    fn assignBit(self: *Self, bit: usize, value: bool) void {
        const word_index = bit / bitmap_view.word_bits;
        const bit_index = bit % bitmap_view.word_bits;
        const mask: bitmap_view.Word = @as(bitmap_view.Word, 1) << @intCast(bit_index);
        if (value) {
            self.words[word_index] |= mask;
        } else {
            self.words[word_index] &= ~mask;
        }
    }

    fn view(self: *const Self) bitmap_view.BitmapView {
        return bitmap_view.BitmapView.init(self.words[0..], bitmap_nbits);
    }

    pub fn initWithSetBits(self: *Self, bits: []const usize) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        @memset(self.words[0..], 0);
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            self.assignBit(bit, true);
        }

        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn setRange(self: *Self, start: usize, len: usize) !void {
        try self.ensureMutable();
        try validateRange(start, len);

        var bit = start;
        while (bit < start + len) : (bit += 1) {
            self.assignBit(bit, true);
        }
    }

    pub fn clearRange(self: *Self, start: usize, len: usize) !void {
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

    pub fn isSet(self: *const Self, bit: usize) bool {
        if (bit >= bitmap_nbits) return false;
        return self.view().isSet(bit);
    }

    pub fn nthSetBit(self: *const Self, ordinal: usize) ?usize {
        var seen: usize = 0;
        var bit: usize = 0;
        while (bit < bitmap_nbits) : (bit += 1) {
            if (!self.isSet(bit)) continue;
            if (seen == ordinal) return bit;
            seen += 1;
        }
        return null;
    }

    pub fn summary(self: *const Self) RuntimeBitmapSummary {
        const bitmap = self.view();
        return .{
            .first_set = bitmap.firstSetBit() orelse bitmap_nbits,
            .first_zero = bitmap.firstClearBit() orelse bitmap_nbits,
            .weight = bitmap.countSetBits(),
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
    const second_word_base = bitmap_view.word_bits;

    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });

    const summary = module.summary();
    try std.testing.expectEqual(@as(usize, 0), summary.first_set);
    try std.testing.expectEqual(@as(usize, 1), summary.first_zero);
    try std.testing.expectEqual(@as(usize, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
}

test "runtime bitmap sample exposes ordered set-bit replay for sparse populations" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 10, 20, 30, 40, 50, 60, 80, 123 });

    const expected = [_]usize{ 10, 20, 30, 40, 50, 60, 80, 123 };
    for (expected, 0..) |bit, index| {
        try std.testing.expectEqual(bit, module.nthSetBit(index) orelse return error.ExpectedNthSetBit);
    }
    try std.testing.expectEqual(@as(?usize, null), module.nthSetBit(expected.len));
}

test "runtime bitmap sample selftest keeps the bounded review contract explicit" {
    const descriptor = RuntimeBitmapSample.descriptor();
    const second_word_base = bitmap_view.word_bits;
    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });

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
    try std.testing.expect(module.isSet(second_word_base + 6));
}

test "runtime bitmap sample keeps post-selftest mutation replay explicit" {
    var module = RuntimeBitmapSample{};
    const second_word_base = bitmap_view.word_bits;
    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    _ = try module.runSelftest();

    try module.clearRange(second_word_base, 2);
    try module.setRange(9, 4);

    const summary_after_mutation = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 0), summary_after_mutation.first_set);
    try std.testing.expectEqual(@as(usize, 1), summary_after_mutation.first_zero);
    try std.testing.expectEqual(@as(usize, 7), summary_after_mutation.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary_after_mutation.nbits);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(!module.isSet(second_word_base));

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(summary_after_mutation.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(summary_after_mutation.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(summary_after_mutation.weight, mirror_summary.weight);
    try std.testing.expect(mirror.isSet(12));
    try std.testing.expect(mirror.isSet(second_word_base + 6));
    try std.testing.expect(!mirror.isSet(second_word_base));
}

test "runtime bitmap sample keeps exit lifecycle and post-exit snapshot explicit" {
    var module = RuntimeBitmapSample{};
    const second_word_base = bitmap_view.word_bits;
    try module.initWithSetBits(&.{ 0, 5, second_word_base, second_word_base + 6 });
    try module.clearRange(second_word_base, 2);
    try module.setRange(9, 4);
    _ = try module.runSelftest();

    const summary_before_exit = module.summary();
    try module.exit();

    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), module.exit_runs);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(second_word_base + 6));
    try std.testing.expect(!module.isSet(second_word_base));

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

test "runtime bitmap sample keeps bounds errors explicit in the direct sample leg" {
    var module = RuntimeBitmapSample{};

    try std.testing.expectError(error.BitRangeOutOfBounds, module.initWithSetBits(&.{RuntimeBitmapSample.bitmap_nbits}));
    try module.initWithSetBits(&.{ 1, 3 });
    try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(RuntimeBitmapSample.bitmap_nbits - 1, 2));
    try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(RuntimeBitmapSample.bitmap_nbits, 1));
}

test "runtime bitmap sample keeps zero-length mutations and invalid copy sources explicit in the direct sample leg" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 2, 7 });

    const summary_before_zero_length = module.summary();
    try module.setRange(5, 0);
    try module.clearRange(RuntimeBitmapSample.bitmap_nbits, 0);

    const summary_after_zero_length = module.summary();
    try std.testing.expectEqual(summary_before_zero_length.first_set, summary_after_zero_length.first_set);
    try std.testing.expectEqual(summary_before_zero_length.first_zero, summary_after_zero_length.first_zero);
    try std.testing.expectEqual(summary_before_zero_length.weight, summary_after_zero_length.weight);
    try std.testing.expectEqual(summary_before_zero_length.nbits, summary_after_zero_length.nbits);

    var cold_source = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&cold_source));

    var exited_source = RuntimeBitmapSample{};
    try exited_source.initWithSetBits(&.{ 9, 13 });
    try exited_source.exit();
    try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&exited_source));
}
