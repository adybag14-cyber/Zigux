// SPDX-License-Identifier: GPL-2.0-only
const std = @import("std");

pub const ArgvSplitResult = struct {
    storage: []u8,
    argv: [][]u8,

    pub fn deinit(self: *ArgvSplitResult, allocator: std.mem.Allocator) void {
        allocator.free(self.argv);
        allocator.free(self.storage);
        self.* = .{
            .storage = &.{},
            .argv = &.{},
        };
    }
};

pub fn countArgc(text: []const u8) usize {
    var count: usize = 0;
    var was_space = true;

    for (text) |ch| {
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
    var storage = try allocator.dupe(u8, cStringPrefix(text));
    errdefer allocator.free(storage);

    const argc = countArgc(storage);
    var argv = try allocator.alloc([]u8, argc);
    errdefer allocator.free(argv);

    var arg_index: usize = 0;
    var arg_start: ?usize = null;

    for (storage, 0..) |*ch, index| {
        if (std.ascii.isWhitespace(ch.*)) {
            if (arg_start) |start| {
                argv[arg_index] = storage[start..index];
                arg_index += 1;
                arg_start = null;
            }
            ch.* = 0;
        } else if (arg_start == null) {
            arg_start = index;
        }
    }

    if (arg_start) |start| {
        argv[arg_index] = storage[start..];
        arg_index += 1;
    }

    std.debug.assert(arg_index == argc);
    return .{
        .storage = storage,
        .argv = argv,
    };
}

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

test "argvSplit collapses repeated whitespace into single separators" {
    var split = try argvSplit(std.testing.allocator, " alpha  beta\tgamma\n");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), split.argv.len);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
}

test "argvSplit returns an empty argv for blank input" {
    var split = try argvSplit(std.testing.allocator, "  \t\n");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 0), split.argv.len);
    try std.testing.expectEqual(@as(usize, 0), countArgc("  \t\n"));
}

test "argvSplit keeps quote characters because Linux argv_split does not parse quotes" {
    var split = try argvSplit(std.testing.allocator, "alpha \"beta gamma\" delta");
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 4), split.argv.len);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("\"beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma\"", split.argv[2]);
    try std.testing.expectEqualStrings("delta", split.argv[3]);
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
