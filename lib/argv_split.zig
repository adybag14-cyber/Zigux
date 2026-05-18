// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const empty_argv_null_terminated: []const ?[*:0]const u8 = &.{null};
var empty_storage_null_terminated = [_:0]u8{0};
const empty_storage_view = empty_storage_null_terminated[0..0 :0];

pub const ArgvSplitResult = struct {
    storage: [:0]u8,
    argv: [][:0]u8,
    argv_null_terminated: []const ?[*:0]const u8,

    pub fn deinit(self: *ArgvSplitResult, allocator: std.mem.Allocator) void {
        if (self.argv_null_terminated.ptr != empty_argv_null_terminated.ptr) {
            allocator.free(self.argv_null_terminated);
        }
        if (self.argv.len != 0) {
            allocator.free(self.argv);
        }
        if (self.storage.ptr != empty_storage_view.ptr) {
            allocator.free(self.storage);
        }
        self.* = .{
            .storage = empty_storage_view,
            .argv = &.{},
            .argv_null_terminated = empty_argv_null_terminated,
        };
    }

    pub fn cArgv(self: *const ArgvSplitResult) [*:null]const ?[*:0]const u8 {
        std.debug.assert(self.argv_null_terminated.len == self.argv.len + 1);
        std.debug.assert(self.argv_null_terminated[self.argv.len] == null);
        return self.argv_null_terminated[0..self.argv.len :null].ptr;
    }
};

const ArgSpan = struct {
    start: usize,
    end: usize,
};

pub fn countArgc(text: []const u8) usize {
    const current = cStringPrefix(text);
    var count: usize = 0;
    var cursor: usize = 0;

    while (nextArgSpan(current, &cursor)) |_| {
        count += 1;
    }

    return count;
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {
    return argvSplitWithArgc(allocator, text, null);
}

pub fn argvSplitWithArgc(
    allocator: std.mem.Allocator,
    text: []const u8,
    argcp: ?*usize,
) !ArgvSplitResult {
    const current = cStringPrefix(text);
    const argc = countArgc(current);
    if (argc == 0) {
        if (argcp) |count_out| {
            count_out.* = 0;
        }
        return .{
            .storage = empty_storage_view,
            .argv = &.{},
            .argv_null_terminated = empty_argv_null_terminated,
        };
    }

    var storage = try allocator.dupeZ(u8, current);
    errdefer allocator.free(storage);

    var argv = try allocator.alloc([:0]u8, argc);
    errdefer allocator.free(argv);

    var argv_null_terminated = try allocArgvNullTerminated(allocator, argc);
    errdefer allocator.free(argv_null_terminated);

    var arg_index: usize = 0;
    var cursor: usize = 0;
    const mutable_storage = storage[0..storage.len];

    while (nextSplitArgSpan(mutable_storage, &cursor)) |span| {
        argv[arg_index] = storage[span.start..span.end :0];
        argv_null_terminated[arg_index] = argv[arg_index].ptr;
        arg_index += 1;
    }

    argv_null_terminated[arg_index] = null;
    std.debug.assert(arg_index == argc);
    if (argcp) |count_out| {
        count_out.* = argc;
    }
    return .{
        .storage = storage,
        .argv = argv,
        .argv_null_terminated = argv_null_terminated,
    };
}

pub fn argvFree(allocator: std.mem.Allocator, result: *ArgvSplitResult) void {
    result.deinit(allocator);
}

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn nextArgSpan(text: []const u8, cursor: *usize) ?ArgSpan {
    var index = cursor.*;

    while (index < text.len and std.ascii.isWhitespace(text[index])) : (index += 1) {}
    if (index == text.len) {
        cursor.* = index;
        return null;
    }

    const start = index;
    while (index < text.len and !std.ascii.isWhitespace(text[index])) : (index += 1) {}

    cursor.* = index;
    return .{
        .start = start,
        .end = index,
    };
}

fn nextSplitArgSpan(text: []u8, cursor: *usize) ?ArgSpan {
    var index = cursor.*;

    while (index < text.len and std.ascii.isWhitespace(text[index])) : (index += 1) {
        text[index] = 0;
    }
    if (index == text.len) {
        cursor.* = index;
        return null;
    }

    const start = index;
    while (index < text.len and !std.ascii.isWhitespace(text[index])) : (index += 1) {}

    const end = index;
    while (index < text.len and std.ascii.isWhitespace(text[index])) : (index += 1) {
        text[index] = 0;
    }

    cursor.* = index;
    return .{
        .start = start,
        .end = end,
    };
}

fn allocArgvNullTerminated(
    allocator: std.mem.Allocator,
    argc: usize,
) ![]?[*:0]const u8 {
    const argv_null_terminated_len = try std.math.add(usize, argc, 1);
    return allocator.alloc(?[*:0]const u8, argv_null_terminated_len);
}

const ArgvFixture = struct {
    input: []const u8,
    expected: []const []const u8,
};

const whitespace_expected = [_][]const u8{
    "alpha",
    "beta",
    "gamma",
};

const ascii_control_whitespace_expected = [_][]const u8{
    "alpha",
    "beta",
    "gamma",
    "delta",
};

const blank_expected = [_][]const u8{};

const leading_nul_expected = [_][]const u8{};

const nul_expected = [_][]const u8{
    "alpha",
    "beta",
};

const quote_expected = [_][]const u8{
    "alpha",
    "\"beta",
    "gamma\"",
    "delta",
};

fn expectFixture(fixture: ArgvFixture) !void {
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(std.testing.allocator, fixture.input, &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(fixture.expected.len, countArgc(fixture.input));
    try std.testing.expectEqual(fixture.expected.len, argc);
    try std.testing.expectEqual(fixture.expected.len, split.argv.len);

    const c_argv = split.cArgv();
    for (fixture.expected, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, split.argv[index]);
        try std.testing.expectEqualStrings(expected, std.mem.span(c_argv[index].?));
    }

    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv[fixture.expected.len]);
}

fn runArgvSplitWithFailingAllocator(allocator: std.mem.Allocator, text: []const u8) !void {
    var split = try argvSplit(allocator, text);
    defer split.deinit(allocator);
}

test "argvSplit matches focused parity fixtures" {
    try expectFixture(.{
        .input = " alpha  beta\tgamma\n",
        .expected = &whitespace_expected,
    });
    try expectFixture(.{
        .input = "\ralpha\x0bbeta\x0cgamma\r\n\tdelta",
        .expected = &ascii_control_whitespace_expected,
    });
    try expectFixture(.{
        .input = "  \t\n",
        .expected = &blank_expected,
    });
    try expectFixture(.{
        .input = "\x00ignored tail",
        .expected = &leading_nul_expected,
    });
    try expectFixture(.{
        .input = "alpha beta\x00ignored tail",
        .expected = &nul_expected,
    });
    try expectFixture(.{
        .input = "alpha \"beta gamma\" delta",
        .expected = &quote_expected,
    });
}

test "argvSplit duplicates the input before tokenizing" {
    var source = [_]u8{ 'o', 'n', 'e', ' ', 't', 'w', 'o' };
    var split = try argvSplit(std.testing.allocator, &source);
    defer split.deinit(std.testing.allocator);

    source[0] = 'X';
    source[4] = 'Y';

    try std.testing.expectEqualStrings("one", split.argv[0]);
    try std.testing.expectEqualStrings("two", split.argv[1]);
}

test "argvSplit keeps non-blank results independently owned across calls" {
    var first = try argvSplit(std.testing.allocator, "alpha beta");
    defer first.deinit(std.testing.allocator);
    var second = try argvSplit(std.testing.allocator, "alpha beta");
    defer second.deinit(std.testing.allocator);

    try std.testing.expect(first.storage.ptr != second.storage.ptr);
    try std.testing.expect(first.argv.ptr != second.argv.ptr);
    try std.testing.expect(first.argv_null_terminated.ptr != second.argv_null_terminated.ptr);
    try std.testing.expect(@intFromPtr(first.cArgv()) != @intFromPtr(second.cArgv()));

    for (first.argv, second.argv, 0..) |first_token, second_token, index| {
        try std.testing.expectEqualStrings(first_token, second_token);
        try std.testing.expect(first_token.ptr != second_token.ptr);
        try std.testing.expect(@intFromPtr(first_token.ptr) == @intFromPtr(first.cArgv()[index].?));
        try std.testing.expect(@intFromPtr(second_token.ptr) == @intFromPtr(second.cArgv()[index].?));
    }
}

test "argvSplit tokens stay inside the owned storage copy" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda rw");
    defer split.deinit(std.testing.allocator);

    const storage_start = @intFromPtr(split.storage.ptr);
    const storage_end = storage_start + split.storage.len;
    const c_argv = split.cArgv();

    for (split.argv, 0..) |token, index| {
        const token_start = @intFromPtr(token.ptr);
        const token_end = token_start + token.len;
        const offset = token_start - storage_start;

        try std.testing.expect(token_start >= storage_start);
        try std.testing.expect(token_end <= storage_end);
        try std.testing.expectEqual(@intFromPtr(token.ptr), @intFromPtr(c_argv[index].?));
        try std.testing.expectEqual(@as(u8, 0), split.storage[offset + token.len]);
    }
}

test "argvSplit zeroes copied whitespace separators across the tokenized buffer" {
    var split = try argvSplit(std.testing.allocator, " alpha  beta\tgamma\n");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[0]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[6]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[7]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[12]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[18]);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
}

test "argvSplit zeroes carriage-return, vertical-tab, and form-feed separators too" {
    var split = try argvSplit(std.testing.allocator, "\ralpha\x0bbeta\x0cgamma\r\n\tdelta");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[0]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[6]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[11]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[17]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[18]);
    try std.testing.expectEqual(@as(u8, 0), split.storage[19]);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
    try std.testing.expectEqualStrings("delta", split.argv[3]);
}

test "argvSplit preserves C-string termination for the final token and argv vector" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqualStrings("root=/dev/vda", std.mem.span(split.cArgv()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);
}

test "cArgv exposes a sentinel-terminated pointer view for Zig callers" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    defer split.deinit(std.testing.allocator);

    const c_argv_with_sentinel: [:null]const ?[*:0]const u8 = split.cArgv()[0..split.argv.len :null];

    try std.testing.expectEqual(split.argv.len, c_argv_with_sentinel.len);
    try std.testing.expectEqualStrings("console=ttyS0", std.mem.span(c_argv_with_sentinel[0].?));
    try std.testing.expectEqualStrings("root=/dev/vda", std.mem.span(c_argv_with_sentinel[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv_with_sentinel[split.argv.len]);
}

test "argvSplit reuses the exported empty argv view for blank input" {
    var buffer: [4]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(fba.allocator(), " \t\n", &argc);
    defer split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(empty_argv_null_terminated.ptr, split.argv_null_terminated.ptr);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "argvSplit reuses the exported empty storage view for blank input without allocating" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(fba.allocator(), " \t\n", &argc);
    defer split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(empty_storage_view.ptr, split.storage.ptr);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "argvSplit treats whitespace before the first NUL as blank input" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(fba.allocator(), " \t\n\x00ignored tail", &argc);
    defer split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), countArgc(" \t\n\x00ignored tail"));
    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(empty_storage_view.ptr, split.storage.ptr);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(empty_argv_null_terminated.ptr, split.argv_null_terminated.ptr);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "argvSplit treats a leading NUL as blank input" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(fba.allocator(), "\x00ignored tail", &argc);
    defer split.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), countArgc("\x00ignored tail"));
    try std.testing.expectEqual(@as(usize, 0), argc);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(empty_storage_view.ptr, split.storage.ptr);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(empty_argv_null_terminated.ptr, split.argv_null_terminated.ptr);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "blank-input deinit on one caller keeps the shared sentinel views usable for another" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var first = try argvSplitWithArgc(fba.allocator(), " \t\n", null);
    var second = try argvSplitWithArgc(fba.allocator(), "", null);
    defer second.deinit(fba.allocator());

    try std.testing.expectEqual(first.storage.ptr, second.storage.ptr);
    try std.testing.expectEqual(first.argv_null_terminated.ptr, second.argv_null_terminated.ptr);
    try std.testing.expectEqual(first.cArgv(), second.cArgv());

    first.deinit(fba.allocator());

    try std.testing.expectEqual(@as(usize, 0), first.storage.len);
    try std.testing.expectEqual(@as(u8, 0), first.storage[first.storage.len]);
    try std.testing.expectEqual(@as(usize, 1), first.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArgv()[0]);

    try std.testing.expectEqual(@as(usize, 0), second.storage.len);
    try std.testing.expectEqual(@as(u8, 0), second.storage[second.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), second.argv.len);
    try std.testing.expectEqual(@as(usize, 1), second.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), second.cArgv()[0]);
    try std.testing.expectEqual(first.storage.ptr, second.storage.ptr);
    try std.testing.expectEqual(first.argv_null_terminated.ptr, second.argv_null_terminated.ptr);
    try std.testing.expectEqual(first.cArgv(), second.cArgv());
}

test "argvFree keeps blank-input sentinel teardown safe and repeatable" {
    var buffer = [_]u8{};
    var fba = std.heap.FixedBufferAllocator.init(&buffer);
    var argc: usize = std.math.maxInt(usize);
    var split = try argvSplitWithArgc(fba.allocator(), " \t\n", &argc);

    try std.testing.expectEqual(@as(usize, 0), argc);

    argvFree(fba.allocator(), &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);

    argvFree(fba.allocator(), &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "ArgvSplitResult deinit clears exported storage and argv views" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");

    try std.testing.expect(split.storage.len != 0);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 2), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);

    split.deinit(std.testing.allocator);
    var blank = try argvSplitWithArgc(std.testing.allocator, "", null);
    defer blank.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
    try std.testing.expect(split.storage.ptr == blank.storage.ptr);
    try std.testing.expect(split.argv_null_terminated.ptr == blank.argv_null_terminated.ptr);
    try std.testing.expect(split.cArgv() == blank.cArgv());
}

test "ArgvSplitResult deinit is idempotent after the exported views are cleared" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");

    split.deinit(std.testing.allocator);
    split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "argvFree mirrors argv_free release ownership and stays safe after teardown" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");

    argvFree(std.testing.allocator, &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);

    argvFree(std.testing.allocator, &split);
    try std.testing.expectEqual(@as(usize, 0), split.storage.len);
    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "non-blank argvSplit results keep caller-owned teardown isolated across siblings" {
    var first = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    var second = try argvSplit(std.testing.allocator, "init=/bin/sh quiet");
    defer second.deinit(std.testing.allocator);

    const first_storage_ptr = first.storage.ptr;
    const first_argv_ptr = first.argv.ptr;
    const first_argv_null_terminated_ptr = first.argv_null_terminated.ptr;
    const second_storage_ptr = second.storage.ptr;
    const second_argv_ptr = second.argv.ptr;
    const second_argv_null_terminated_ptr = second.argv_null_terminated.ptr;
    const second_c_argv = second.cArgv();

    try std.testing.expect(first_storage_ptr != second_storage_ptr);
    try std.testing.expect(first_argv_ptr != second_argv_ptr);
    try std.testing.expect(first_argv_null_terminated_ptr != second_argv_null_terminated_ptr);
    try std.testing.expect(first.cArgv() != second_c_argv);
    try std.testing.expectEqualStrings("console=ttyS0", first.argv[0]);
    try std.testing.expectEqualStrings("root=/dev/vda", first.argv[1]);
    try std.testing.expectEqualStrings("init=/bin/sh", second.argv[0]);
    try std.testing.expectEqualStrings("quiet", second.argv[1]);

    first.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), first.storage.len);
    try std.testing.expectEqual(@as(u8, 0), first.storage[first.storage.len]);
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);
    try std.testing.expectEqual(@as(usize, 1), first.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), first.cArgv()[0]);

    try std.testing.expect(second.storage.ptr == second_storage_ptr);
    try std.testing.expect(second.argv.ptr == second_argv_ptr);
    try std.testing.expect(second.argv_null_terminated.ptr == second_argv_null_terminated_ptr);
    try std.testing.expect(second.cArgv() == second_c_argv);
    try std.testing.expectEqualStrings("init=/bin/sh", second.argv[0]);
    try std.testing.expectEqualStrings("quiet", second.argv[1]);
    try std.testing.expectEqualStrings("init=/bin/sh", std.mem.span(second.cArgv()[0].?));
    try std.testing.expectEqualStrings("quiet", std.mem.span(second.cArgv()[1].?));
}

test "argvSplit frees intermediate allocations when allocator failure interrupts setup" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        runArgvSplitWithFailingAllocator,
        .{"console=ttyS0 root=/dev/vda rw"},
    );
}

test "argvSplitWithArgc keeps caller argc unchanged when allocation fails before returning a result" {
    var backing = [_]u8{0} ** 15;
    var fba = std.heap.FixedBufferAllocator.init(&backing);
    var argc: usize = std.math.maxInt(usize);

    try std.testing.expectError(
        error.OutOfMemory,
        argvSplitWithArgc(fba.allocator(), "alpha beta", &argc),
    );
    try std.testing.expectEqual(std.math.maxInt(usize), argc);
}

test "argvSplit reports overflow before sizing the null-terminated argv vector" {
    try std.testing.expectError(
        error.Overflow,
        allocArgvNullTerminated(std.testing.allocator, std.math.maxInt(usize)),
    );
}
