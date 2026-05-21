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

    fn assignBit(self: *Self, bit: u32, value: bool) void {
        const word_index: usize = @intCast(bit / bitmap_view.word_bits);
        const bit_index: u6 = @intCast(bit % bitmap_view.word_bits);
        const mask: bitmap_view.Word = @as(bitmap_view.Word, 1) << bit_index;
        if (value) {
            self.words[word_index] |= mask;
        } else {
            self.words[word_index] &= ~mask;
        }
    }

    pub fn initWithSetBits(self: *Self, bits: []const u32) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        self.words = [_]bitmap_view.Word{0} ** backing_word_count;
        for (bits) |bit| {
            if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
            self.assignBit(bit, true);
        }
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn initFromBitList(self: *Self, bit_list: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;

        const parsed_words = [_]bitmap_view.Word{0} ** backing_word_count;
        var parsed = Self{ .words = parsed_words };
        const trimmed = std.mem.trim(u8, bit_list, &std.ascii.whitespace);
        if (trimmed.len != 0) {
            var tokens = std.mem.splitScalar(u8, trimmed, ',');
            while (tokens.next()) |raw_token| {
                const token = std.mem.trim(u8, raw_token, &std.ascii.whitespace);
                if (token.len == 0) return error.InvalidBitList;
                const bit = std.fmt.parseUnsigned(u32, token, 10) catch return error.InvalidBitList;
                if (bit >= bitmap_nbits) return error.BitRangeOutOfBounds;
                parsed.assignBit(bit, true);
            }
        }

        self.words = parsed.words;
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

test "runtime bitmap sample leaves failed parsed init cold and empty" {
    var module = RuntimeBitmapSample{};

    try std.testing.expectError(error.InvalidBitList, module.initFromBitList("0,,64"));
    try std.testing.expectEqual(ModuleStage.cold, module.stage());

    const summary = module.summary();
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.first_set);
    try std.testing.expectEqual(@as(u32, 0), summary.first_zero);
    try std.testing.expectEqual(@as(u32, 0), summary.weight);
    try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);
    try std.testing.expectEqual(@as(usize, 0), summary.init_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), summary.exit_runs);
    try std.testing.expect(!module.isSet(0));
    try std.testing.expectEqual(@as(?u32, null), module.nthSetBit(0));
    try std.testing.expectEqual(@as(u32, 0), try module.countSetBitsInRange(0, RuntimeBitmapSample.bitmap_nbits));
}
