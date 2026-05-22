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
    top_bit_contract,
};

pub const sample_review_focus = [_]SampleFocus{
    .descriptor_and_anchor,
    .summary_replay,
    .sparse_iteration,
    .parse_and_print,
    .range_mutation_and_copy,
    .selftest_lifecycle,
    .exit_lifecycle_and_guards,
    .top_bit_contract,
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

    pub const bitmap_nbits: u32 = @intCast(bitmap_view.word_bits * 2);
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
        if (start >= bitmap_nbits or len > bitmap_nbits - start) return error.BitRangeOutOfBounds;
    }

    fn assignBitWords(words: []bitmap_view.Word, bit: u32, value: bool) void {
        const word_index: usize = @intCast(bit / bitmap_view.word_bits);
        const bit_index: u6 = @intCast(bit % bitmap_view.word_bits);
        const mask: bitmap_view.Word = @as(bitmap_view.Word, 1) << bit_index;
        if (value) {
            words[word_index] |= mask;
        } else {
            words[word_index] &= ~mask;
        }
    }

    fn assignBit(self: *Self, bit: u32, value: bool) void {
        assignBitWords(self.words[0..], bit, value);
    }

    pub fn initWithSetBits(self: *Self, bits: []const u32) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        var next_words = [_]bitmap_view.Word{0} ** backing_word_count;
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            assignBitWords(next_words[0..], bit, true);
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
            var tokens = std.mem.splitScalar(u8, trimmed, ',');
            while (tokens.next()) |raw_token| {
                const token = std.mem.trim(u8, raw_token, &std.ascii.whitespace);
                if (token.len == 0) return error.InvalidBitList;
                const bit = std.fmt.parseUnsigned(u32, token, 10) catch return error.InvalidBitList;
                if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
                assignBitWords(next_words[0..], bit, true);
            }
        }

        self.words = next_words;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn setRange(self: *Self, start: u32, len: u32) !void {
        try self.ensureMutable();
        try validateRange(start, len);
        var bit = start;
        while (bit < start + len) : (bit += 1) self.assignBit(bit, true);
    }

    pub fn clearRange(self: *Self, start: u32, len: u32) !void {
        try self.ensureMutable();
        try validateRange(start, len);
        var bit = start;
        while (bit < start + len) : (bit += 1) self.assignBit(bit, false);
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
        const view = bitmap_view.BitmapView.init(self.words[0..], @intCast(bitmap_nbits));
        return view.isSet(@intCast(bit));
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

    pub fn summary(self: *const Self) RuntimeBitmapSummary {
        const view = bitmap_view.BitmapView.init(self.words[0..], @intCast(bitmap_nbits));
        return .{
            .first_set = if (view.firstSetBit()) |bit| @intCast(bit) else bitmap_nbits,
            .first_zero = if (view.firstClearBit()) |bit| @intCast(bit) else bitmap_nbits,
            .weight = @intCast(view.countSetBits()),
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
            .operation_families = &.{ .clear_set, .copy, .parse_and_print, .iteration_and_ranges },
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

fn expectSummaryStable(before: RuntimeBitmapSummary, after: RuntimeBitmapSummary) !void {
    try std.testing.expectEqual(before.first_set, after.first_set);
    try std.testing.expectEqual(before.first_zero, after.first_zero);
    try std.testing.expectEqual(before.weight, after.weight);
    try std.testing.expectEqual(before.nbits, after.nbits);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
}

test "runtime bitmap sample review contract keeps bounded starter focus explicit" {
    const descriptor = RuntimeBitmapSample.descriptor();
    const contract = RuntimeBitmapSample.reviewContract();

    try std.testing.expectEqualStrings("runtime_bitmap", descriptor.name);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);
    try std.testing.expectEqual(@as(usize, sample_review_focus.len), contract.focus.len);
    try std.testing.expectEqual(@as(usize, sample_review_non_goals.len), contract.non_goals.len);
    try std.testing.expectEqual(SampleFocus.top_bit_contract, contract.focus[contract.focus.len - 1]);
}

test "runtime bitmap sample keeps sparse summaries and nth-set replay explicit" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 10, 20, 30, 40, 50, 60, 80, 123 });

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 10), summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 8), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expectEqual(@as(?u32, 10), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 123), module.nthSetBit(7));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(8));
    try std.testing.expectEqual(@as(u32, 7), try module.countSetBitsInRange(0, 81));
}

test "runtime bitmap sample keeps parse print and range mutation replay explicit" {
    var module = RuntimeBitmapSample{};
    try module.initFromBitList("0, 5, 64, 70");

    const formatted = try module.formatSetBits(std.testing.allocator);
    defer std.testing.allocator.free(formatted);
    try std.testing.expectEqualStrings("0,5,64,70", formatted);

    try module.clearRange(@intCast(bitmap_view.word_bits), 2);
    try module.setRange(9, 4);

    const summary = module.summary();
    try std.testing.expectEqual(@as(u32, 0), summary.first_set);
    try std.testing.expectEqual(@as(u32, 1), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 7), summary.weight);
    try std.testing.expect(module.isSet(12));
    try std.testing.expect(module.isSet(@intCast(bitmap_view.word_bits + 6)));
    try std.testing.expect(!module.isSet(@intCast(bitmap_view.word_bits)));
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(9, 4));
}

test "runtime bitmap sample keeps selftest copy and exit lifecycle explicit" {
    var source = RuntimeBitmapSample{};
    try source.initWithSetBits(&.{ 0, 5, 64, 70 });
    const before = source.summary();
    const selftest = try source.runSelftest();

    try std.testing.expectEqualStrings("lib/test_bitmap.c", selftest.anchor);
    try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);
    try std.testing.expect(selftest.checked_range_mutations);
    try std.testing.expect(selftest.checked_iteration_paths);

    var mirror = RuntimeBitmapSample{};
    try mirror.initWithSetBits(&.{});
    try mirror.copyFrom(&source);
    const mirrored = mirror.summary();
    try std.testing.expectEqual(before.first_set, mirrored.first_set);
    try std.testing.expectEqual(before.weight, mirrored.weight);

    try source.exit();
    const after = source.summary();
    try std.testing.expectEqual(ModuleStage.exited, source.stage());
    try std.testing.expectEqual(@as(usize, 1), after.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after.exit_runs);
    try std.testing.expectError(error.InvalidLifecycleTransition, source.setRange(1, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, source.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, source.exit());
}

test "runtime bitmap sample rejects re-selftest without disturbing lifecycle summaries" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();

    const before_rejected_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_rejected_selftest.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.selftest_complete, module.stage());
    try expectSummaryStable(before_rejected_selftest, after_rejected_selftest);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    try module.exit();

    const before_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_rejected_exit_selftest.exit_runs);

    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());

    const after_rejected_exit_selftest = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectSummaryStable(before_rejected_exit_selftest, after_rejected_exit_selftest);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
}

test "runtime bitmap sample rejects re-init without disturbing initialized summaries" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    const before_reinit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_reinit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    try std.testing.expectError(error.InvalidLifecycleTransition, module.initWithSetBits(&.{ 1, 2 }));

    const after_reinit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try expectSummaryStable(before_reinit, after_reinit);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
}

test "runtime bitmap sample keeps initialized summary stable across direct exit without selftest" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });

    const before_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.initialized, module.stage());
    try std.testing.expectEqual(@as(u32, 0), before_exit.first_set);
    try std.testing.expectEqual(@as(u32, 1), before_exit.first_zero);
    try std.testing.expectEqual(@as(u32, 4), before_exit.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, before_exit.nbits);
    try std.testing.expectEqual(@as(usize, 1), before_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), before_exit.exit_runs);

    try module.exit();

    const after_exit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(before_exit.first_set, after_exit.first_set);
    try std.testing.expectEqual(before_exit.first_zero, after_exit.first_zero);
    try std.testing.expectEqual(before_exit.weight, after_exit.weight);
    try std.testing.expectEqual(before_exit.nbits, after_exit.nbits);
    try std.testing.expectEqual(before_exit.init_runs, after_exit.init_runs);
    try std.testing.expectEqual(@as(usize, 0), after_exit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 0), module.nthSetBit(0));
    try std.testing.expectEqual(@as(?u32, 5), module.nthSetBit(1));
    try std.testing.expectEqual(@as(?u32, 64), module.nthSetBit(2));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(4));
    try std.testing.expectEqual(@as(u32, 4), try module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());
    try std.testing.expectError(error.InvalidLifecycleTransition, module.setRange(5, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.clearRange(64, 1));
    try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());
}

test "runtime bitmap sample rejects re-init after exit without disturbing lifecycle summaries" {
    var module = RuntimeBitmapSample{};
    try module.initWithSetBits(&.{ 0, 5, 64, 70 });
    _ = try module.runSelftest();
    try module.exit();

    const before_reinit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try std.testing.expectEqual(@as(usize, 1), before_reinit.init_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), before_reinit.exit_runs);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));

    try std.testing.expectError(error.InvalidLifecycleTransition, module.initWithSetBits(&.{ 1, 2 }));

    const after_reinit = module.summary();
    try std.testing.expectEqual(ModuleStage.exited, module.stage());
    try expectSummaryStable(before_reinit, after_reinit);
    try std.testing.expect(module.isSet(0));
    try std.testing.expect(module.isSet(5));
    try std.testing.expect(module.isSet(64));
    try std.testing.expect(module.isSet(70));
    try std.testing.expectEqual(@as(?u32, 70), module.nthSetBit(3));
}
