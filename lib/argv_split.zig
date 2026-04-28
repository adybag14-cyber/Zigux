// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");
const empty_argv_null_terminated: []const ?[*:0]const u8 = &.{null};

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
        allocator.free(self.storage);
        self.* = .{
            .storage = undefined,
            .argv = &.{},
            .argv_null_terminated = empty_argv_null_terminated,
        };
    }

    pub fn cArgv(self: *const ArgvSplitResult) [*]const ?[*:0]const u8 {
        return self.argv_null_terminated.ptr;
    }
};

pub fn countArgc(text: []const u8) usize {
    const current = cStringPrefix(text);
    var count: usize = 0;
    var was_space = true;

    for (current) |ch| {
        if (std.ascii.isWhitespace(ch)) {
            was_space = true;
        } else if (was_space) {
            was_space = false;
            count += 1;
        }
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
    var storage = try allocator.dupeZ(u8, cStringPrefix(text));
    errdefer allocator.free(storage);

    const argc = countArgc(storage);
    if (argc == 0) {
        if (argcp) |count_out| {
            count_out.* = 0;
        }
        return .{
            .storage = storage,
            .argv = &.{},
            .argv_null_terminated = empty_argv_null_terminated,
        };
    }

    var argv = try allocator.alloc([:0]u8, argc);
    errdefer allocator.free(argv);

    var argv_null_terminated = try allocator.alloc(?[*:0]const u8, argc + 1);
    errdefer allocator.free(argv_null_terminated);

    var arg_index: usize = 0;
    var arg_start: ?usize = null;

    for (storage, 0..) |*ch, index| {
        if (std.ascii.isWhitespace(ch.*)) {
            ch.* = 0;
            if (arg_start) |start| {
                argv[arg_index] = storage[start..index :0];
                argv_null_terminated[arg_index] = argv[arg_index].ptr;
                arg_index += 1;
                arg_start = null;
            }
        } else if (arg_start == null) {
            arg_start = index;
        }
    }

    if (arg_start) |start| {
        argv[arg_index] = storage[start..storage.len :0];
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

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
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

const blank_expected = [_][]const u8{};

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

test "argvSplit matches focused parity fixtures" {
    try expectFixture(.{
        .input = " alpha  beta\tgamma\n",
        .expected = &whitespace_expected,
    });
    try expectFixture(.{
        .input = "  \t\n",
        .expected = &blank_expected,
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

test "argvSplit preserves C-string termination for the final token and argv vector" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), split.storage[split.storage.len]);
    try std.testing.expectEqualStrings("root=/dev/vda", std.mem.span(split.cArgv()[1].?));
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);
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
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}

test "ArgvSplitResult deinit leaves exported argv views empty and null terminated" {
    var split = try argvSplit(std.testing.allocator, "console=ttyS0 root=/dev/vda");

    try std.testing.expectEqual(@as(usize, 2), split.argv.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[split.argv.len]);

    split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 1), split.argv_null_terminated.len);
    try std.testing.expectEqual(@as(?[*:0]const u8, null), split.cArgv()[0]);
}
