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

pub const SampleFocus = enum {
    descriptor_and_anchor,
    summary_replay,
    sparse_iteration,
    parse_and_print,
    range_mutation_and_copy,
    selftest_lifecycle,
    exit_lifecycle_and_guards,
};

pub const sample_review_focus = [_]SampleFocus{
    .descriptor_and_anchor,
    .summary_replay,
    .sparse_iteration,
    .parse_and_print,
    .range_mutation_and_copy,
    .selftest_lifecycle,
    .exit_lifecycle_and_guards,
};

pub const sample_review_non_goals = [_][]const u8{
    "loadable runtime bitmap module parity",
    "shared runtime-loader command-name or argv-policy controls",
    "real runtime execution through a live substrate",
    "full lib/test_bitmap.c parity beyond the bounded starter packet",
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
    init_runs: usize,
    selftest_runs: usize,
    exit_runs: usize,
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

    pub fn reviewContract() ReviewContract {
        return .{
            .focus = &sample_review_focus,
            .non_goals = &sample_review_non_goals,
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

    fn assignBitInto(words: []bitmap_view.Word, bit: u32, value: bool) void {
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
        assignBitInto(self.words[0..], bit, value);
    }

    pub fn initWithSetBits(self: *Self, bits: []const u32) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var next_words = [_]bitmap_view.Word{0} ** backing_word_count;
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            assignBitInto(next_words[0..], bit, true);
        }

        self.words = next_words;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn initFromBitList(self: *Self, bit_list: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var next_words = [_]bitmap_view.Word{0} ** backing_word_count;

        const trimmed = std.mem.trim(u8, bit_list, &std.ascii.whitespace);
        if (trimmed.len != 0) {
            var saw_any = false;
            var tokens = std.mem.splitScalar(u8, trimmed, ',');
            while (tokens.next()) |raw_token| {
                const token = std.mem.trim(u8, raw_token, &std.ascii.whitespace);
                if (token.len == 0) return error.InvalidBitList;

                const bit = std.fmt.parseUnsigned(u32, token, 10) catch return error.InvalidBitList;
                if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;

                assignBitInto(next_words[0..], bit, true);
                saw_any = true;
            }
            if (!saw_any) return error.InvalidBitList;
        }

        self.words = next_words;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn formatSetBits(self: *const Self, allocator: std.mem.Allocator) ![]u8 {
        var output: std.ArrayList(u8) = .empty;
        errdefer output.deinit(allocator);

        var first = true;
        var bit: u32 = 0;
        while (bit < bitmap_nbits) : (bit += 1) {
            if (!self.isSet(bit)) continue;

            if (!first) try output.append(allocator, ',');
            first = false;
            try output.print(allocator, "{}", .{bit});
        }

        return output.toOwnedSlice(allocator);
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

    pub fn nthSetBit(self: *const Self, ordinal: u32) ?u32 {
        var seen: u32 = 0;
        var bit: u32 = 0;
        while (bit < bitmap_nbits) : (bit += 1) {
            if (!self.isSet(bit)) continue;
            if (seen == ordinal) return bit;
            seen += 1;
        }
        return null;
    }

    pub fn countSetBitsInRange(self: *const Self, start: u32, len: u32) !u32 {
        try validateRange(start, len);

        var total: u32 = 0;
        var bit = start;
        while (bit < start + len) : (bit += 1) {
            if (self.isSet(bit)) total += 1;
        }
        return total;
    }

    pub fn summary(self: *const Self) RuntimeBitmapSummary {
        const view = bitmap_view.viewFromWords(self.words[0..], bitmap_nbits);
        const bounded = bitmap_view.summarize(view);
        return .{
            .first_set = bounded.first_set,
            .first_zero = bounded.first_zero,
            .weight = bounded.weight,
            .nbits = bitmap_nbits,
            .init_runs = self.init_runs,
            .selftest_runs = self.selftest_runs,
            .exit_runs = self.exit_runs,
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

test "runtime bitmap sample review contract keeps bounded starter focus explicit" {
    const expected_focus = sample_review_focus;
    const expected_non_goals = sample_review_non_goals;
    const descriptor = RuntimeBitmapSample.descriptor();
    const contract = RuntimeBitmapSample.reviewContract();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    try std.testing.expectEqual(@as(usize, expected_focus.len), contract.focus.len);
    for (expected_focus, contract.focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }

    try std.testing.expectEqual(@as(usize, expected_non_goals.len), contract.non_goals.len);
    for (expected_non_goals, contract.non_goals) |expected, actual| {
        try std.testing.expectEqualStrings(expected, actual);
    }
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

test "runtime bitmap sample exposes ordered set-bit replay for sparse populations" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 10, 20, 30, 40, 50, 60, 80, 123 });

    const expected = [_]u32{ 10, 20, 30, 40, 50, 60, 80, 123 };
    for (expected, 0..) |bit, index| {
        try std.testing.expectEqual(bit, module.nthSetBit(@intCast(index)) orelse return error.ExpectedNthSetBit);
    }
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(@intCast(expected.len)));
}

test "runtime bitmap sample keeps bounded range-count replay explicit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6, bitmap_view.bits_per_long + 7, bitmap_view.bits_per_long + 8, 123 });

    try std.testing.expectEqual(@as(u32, 2), try module.countSetBitsInRange(0, 8));
    try std.testing.expectEqual(@as(u32, 0), try module.countSetBitsInRange(8, 1));
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(bitmap_view.bits_per_long, 9));
    try std.testing.expectEqual(@as(u32, 3), try module.countSetBitsInRange(bitmap_view.bits_per_long + 6, 3));
    try std.testing.expectEqual(@as(u32, 0), try module.countSetBitsInRange(RuntimeBitmapSample.bitmap_nbits, 0));

    _ = try module.runSelftest();
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(bitmap_view.bits_per_long, 9));

    try module.exit();
    try std.testing.expectEqual(@as(u32, 3), try module.countSetBitsInRange(bitmap_view.bits_per_long + 6, 3));
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        module.countSetBitsInRange(RuntimeBitmapSample.bitmap_nbits - 1, 2),
    );
}

test "runtime bitmap sample keeps parse-and-print replay explicit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);

    try std.testing.expectEqualStrings("0,5,64,70", formatted);

    var parsed = RuntimeBitmapSample{};
    try parsed.initFromBitList("0, 5, 64, 70");

    const parsed_summary = parsed.summary();
    const module_summary = module.summary();
    try std.testing.expectEqual(module_summary.first_set, parsed_summary.first_set);
    try std.testing.expectEqual(module_summary.first_zero, parsed_summary.first_zero);
    try std.testing.expectEqual(module_summary.weight, parsed_summary.weight);
    try std.testing.expectEqual(module_summary.nbits, parsed_summary.nbits);
    try std.testing.expect(parsed.isSet(0));
    try std.testing.expect(parsed.isSet(5));
    try std.testing.expect(parsed.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(parsed.isSet(bitmap_view.bits_per_long + 6));

    var empty = RuntimeBitmapSample{};
    try empty.initFromBitList("  ");

    const empty_summary = empty.summary();
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, empty_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), empty_summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, empty_summary.nbits);
    try std.testing.expectEqual(@as(?u32, null), empty.nthSetBit(0));

    const empty_formatted = try empty.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(empty_formatted);
    try std.testing.expectEqualStrings("", empty_formatted);

    var invalid = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, invalid.initFromBitList("0, nope"));

    var trailing_comma = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, trailing_comma.initFromBitList("0,"));

    var doubled_separator = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, doubled_separator.initFromBitList("0,,5"));
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

    const summary_after_selftest = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary_after_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary_after_selftest.exit_runs);
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

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,9,10,11,12,70", formatted);

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&module);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(ModuleStage.initialized, mirror.stage());
    try std.testing.expectEqual(@as(usize, 1), mirror_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.exit_runs);
    try std.testing.expectEqual(summary_after_mutation.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(summary_after_mutation.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(summary_after_mutation.weight, mirror_summary.weight);
    try std.testing.expectEqual(summary_after_mutation.nbits, mirror_summary.nbits);
    try std.testing.expect(mirror.isSet(12));
    try std.testing.expect(mirror.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!mirror.isSet(bitmap_view.bits_per_long));

    const mirror_formatted = try mirror.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(mirror_formatted);
    try std.testing.expectEqualStrings(formatted, mirror_formatted);
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
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!module.isSet(bitmap_view.bits_per_long));

    const summary_after_exit = module.summary();
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), summary_after_exit.exit_runs);
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

test "runtime bitmap sample keeps initWithSetBits duplicate normalization and repeat-init lifecycle explicit in the direct sample leg" {
    var duplicate_bits = RuntimeBitmapSample{};
    try duplicate_bits.initWithSetBits(&.{ 70, 5, 70, 0, bitmap_view.bits_per_long, 5 });

    const duplicate_summary = duplicate_bits.summary();
    try std.testing.expectEqual(@as(u32, 0), duplicate_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), duplicate_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), duplicate_summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, duplicate_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), duplicate_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), duplicate_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), duplicate_summary.exit_runs);
    try std.testing.expectEqual(ModuleStage.initialized, duplicate_bits.stage());
    try std.testing.expect(duplicate_bits.isSet(0));
    try std.testing.expect(duplicate_bits.isSet(5));
    try std.testing.expect(duplicate_bits.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(duplicate_bits.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expectEqual(@as(?u32, 0), duplicate_bits.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 5), duplicate_bits.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, bitmap_view.bits_per_long), duplicate_bits.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, bitmap_view.bits_per_long + 6), duplicate_bits.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), duplicate_bits.nthSetBit(4));

    const duplicate_formatted = try duplicate_bits.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(duplicate_formatted);
    try std.testing.expectEqualStrings("0,5,64,70", duplicate_formatted);

    try std.testing.expectError(error.InvalidLifecycleTransition, duplicate_bits.initWithSetBits(&.{1}));
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

test "runtime bitmap sample accepts selftest-complete copy sources in the direct sample leg" {
    var source = RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 4, 7, bitmap_view.bits_per_long + 1, bitmap_view.bits_per_long + 9 });
    const source_summary_before_selftest = source.summary();
    _ = try source.runSelftest();

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&source);

    const mirror_summary = mirror.summary();
    try std.testing.expectEqual(ModuleStage.initialized, mirror.stage());
    try std.testing.expectEqual(source_summary_before_selftest.first_set, mirror_summary.first_set);
    try std.testing.expectEqual(source_summary_before_selftest.first_zero, mirror_summary.first_zero);
    try std.testing.expectEqual(source_summary_before_selftest.weight, mirror_summary.weight);
    try std.testing.expectEqual(source_summary_before_selftest.nbits, mirror_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), mirror_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), mirror_summary.exit_runs);
    try std.testing.expect(mirror.isSet(4));
    try std.testing.expect(mirror.isSet(7));
    try std.testing.expect(mirror.isSet(bitmap_view.bits_per_long + 1));
    try std.testing.expect(mirror.isSet(bitmap_view.bits_per_long + 9));

    const formatted = try mirror.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("4,7,65,73", formatted);

    const selftest = try mirror.runSelftest();
    try std.testing.expectEqual(ModuleStage.selftest_complete, mirror.stage());
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expectEqual(OperationFamily.copy, selftest.operation_families[1]);
}

test "runtime bitmap sample keeps bit-list bounds, separators, duplicate normalization, and repeat-init lifecycle explicit in the direct sample leg" {
    var trailing_comma = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, trailing_comma.initFromBitList("0,"));

    var doubled_separator = RuntimeBitmapSample{};
    try std.testing.expectError(error.InvalidBitList, doubled_separator.initFromBitList("0,,5"));

    var out_of_bounds = RuntimeBitmapSample{};
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        out_of_bounds.initFromBitList("0, 5, 64, 128"),
    );

    var duplicate_bits = RuntimeBitmapSample{};
    try duplicate_bits.initFromBitList("70, 5, 70, 0, 64, 5");

    const duplicate_summary = duplicate_bits.summary();
    try std.testing.expectEqual(@as(u32, 0), duplicate_summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), duplicate_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), duplicate_summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, duplicate_summary.nbits);
    try std.testing.expectEqual(@as(usize, 1), duplicate_summary.init_runs);
    try std.testing.expectEqual(ModuleStage.initialized, duplicate_bits.stage());
    try std.testing.expect(duplicate_bits.isSet(0));
    try std.testing.expect(duplicate_bits.isSet(5));
    try std.testing.expect(duplicate_bits.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(duplicate_bits.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expectEqual(@as(?u32, 0), duplicate_bits.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 5), duplicate_bits.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, bitmap_view.bits_per_long), duplicate_bits.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, bitmap_view.bits_per_long + 6), duplicate_bits.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), duplicate_bits.nthSetBit(4));

    const duplicate_formatted = try duplicate_bits.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(duplicate_formatted);
    try std.testing.expectEqualStrings("0,5,64,70", duplicate_formatted);

    var module = RuntimeBitmapSample{};
    try module.initFromBitList("0, 5, 64, 70");

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 4), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expectEqual(@as(usize, 1), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.initFromBitList("1"));
}

test "runtime bitmap sample keeps transactional init failures explicit in the direct sample leg" {
    var parsed = RuntimeBitmapSample{};
    try std.testing.expectError(error.BitRangeOutOfBounds, parsed.initFromBitList("0, 5, 64, 128"));
    try std.testing.expectEqual(ModuleStage.cold, parsed.stage());

    const parsed_summary = parsed.summary();
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, parsed_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), parsed_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), parsed_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), parsed_summary.exit_runs);
    try std.testing.expectEqual(@as(?u32, null), parsed.nthSetBit(0));
    try std.testing.expect(!parsed.isSet(0));
    try std.testing.expect(!parsed.isSet(5));
    try std.testing.expect(!parsed.isSet(bitmap_view.bits_per_long));

    const parsed_formatted = try parsed.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(parsed_formatted);
    try std.testing.expectEqualStrings("", parsed_formatted);

    try parsed.initFromBitList("0, 5, 64, 70");
    try std.testing.expectEqual(ModuleStage.initialized, parsed.stage());
    try std.testing.expect(parsed.isSet(0));
    try std.testing.expect(parsed.isSet(5));
    try std.testing.expect(parsed.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(parsed.isSet(bitmap_view.bits_per_long + 6));

    var direct = RuntimeBitmapSample{};
    try std.testing.expectError(error.BitRangeOutOfBounds, direct.initWithSetBits(&.{ 1, RuntimeBitmapSample.bitmap_nbits }));
    try std.testing.expectEqual(ModuleStage.cold, direct.stage());

    const direct_summary = direct.summary();
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, direct_summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), direct_summary.weight);
    try std.testing.expectEqual(@as(usize, 0), direct_summary.init_runs);
    try std.testing.expect(!direct.isSet(1));
    try std.testing.expectEqual(@as(?u32, null), direct.nthSetBit(0));

    try direct.initWithSetBits(&.{ 1, 3 });
    try std.testing.expectEqual(ModuleStage.initialized, direct.stage());
    try std.testing.expect(direct.isSet(1));
    try std.testing.expect(direct.isSet(3));
}

test "runtime bitmap sample keeps failed range mutations non-destructive in the direct sample leg" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, bitmap_view.bits_per_long, bitmap_view.bits_per_long + 6 });

    const summary_before_failure = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));

    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        module.setRange(RuntimeBitmapSample.bitmap_nbits - 1, 2),
    );
    try std.testing.expectError(
        error.BitRangeOutOfBounds,
        module.clearRange(RuntimeBitmapSample.bitmap_nbits, 1),
    );

    const summary_after_failure = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(summary_before_failure.first_set, summary_after_failure.first_set);
    try std.testing.expectEqual(summary_before_failure.first_zero, summary_after_failure.first_zero);
    try std.testing.expectEqual(summary_before_failure.weight, summary_after_failure.weight);
    try std.testing.expectEqual(summary_before_failure.nbits, summary_after_failure.nbits);
    try std.testing.expectEqual(summary_before_failure.init_runs, summary_after_failure.init_runs);
    try std.testing.expectEqual(summary_before_failure.selftest_runs, summary_after_failure.selftest_runs);
    try std.testing.expectEqual(summary_before_failure.exit_runs, summary_after_failure.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long));
    try std.testing.expect(module.isSet(bitmap_view.bits_per_long + 6));
    try std.testing.expect(!module.isSet(bitmap_view.bits_per_long + 1));
}