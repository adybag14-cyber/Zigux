const std = @import("std");

pub const ArgvSplitResult = struct {
    allocator: std.mem.Allocator,
    argv: [][]u8,

    pub fn argc(self: ArgvSplitResult) usize {
        return self.argv.len;
    }

    pub fn deinit(self: *ArgvSplitResult) void {
        for (self.argv) |arg| {
            self.allocator.free(arg);
        }
        self.allocator.free(self.argv);
        self.* = .{
            .allocator = self.allocator,
            .argv = &.{},
        };
    }
};

fn skipSpaces(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn skipArg(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and !std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn countArgc(text: []const u8) usize {
    var idx: usize = 0;
    var count: usize = 0;

    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx >= text.len) {
            break;
        }
        count += 1;
        idx = skipArg(text, idx);
    }

    return count;
}

fn freeArgvPrefix(allocator: std.mem.Allocator, argv: [][]u8, count: usize) void {
    for (argv[0..count]) |arg| {
        allocator.free(arg);
    }
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {
    const argc = countArgc(text);
    var argv = try allocator.alloc([]u8, argc);

    var idx: usize = 0;
    var arg_idx: usize = 0;
    errdefer {
        freeArgvPrefix(allocator, argv, arg_idx);
        allocator.free(argv);
    }
    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx >= text.len) {
            break;
        }

        const end = skipArg(text, idx);
        argv[arg_idx] = try allocator.dupe(u8, text[idx..end]);
        arg_idx += 1;
        idx = end;
    }

    return .{
        .allocator = allocator,
        .argv = argv,
    };
}

pub fn argvFree(result: *ArgvSplitResult) void {
    result.deinit();
}

pub const argv_split = argvSplit;
pub const argv_free = argvFree;

test "argvSplit matches the phase 1 committed fixture shape" {
    var result = try argvSplit(std.testing.allocator, "alpha beta gamma");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqual(@as(usize, 3), result.argv.len);
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
}

test "argvSplit collapses repeated whitespace and blank inputs to zero arguments" {
    var blank = try argvSplit(std.testing.allocator, "");
    defer blank.deinit();
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
    try std.testing.expectEqual(@as(usize, 0), blank.argv.len);

    var spaced = try argvSplit(std.testing.allocator, " \t alpha \n  beta   gamma  ");
    defer spaced.deinit();
    try std.testing.expectEqual(@as(usize, 3), spaced.argc());
    try std.testing.expectEqualStrings("alpha", spaced.argv[0]);
    try std.testing.expectEqualStrings("beta", spaced.argv[1]);
    try std.testing.expectEqualStrings("gamma", spaced.argv[2]);

    var only_spaces = try argv_split(std.testing.allocator, " \n\t ");
    defer argv_free(&only_spaces);
    try std.testing.expectEqual(@as(usize, 0), only_spaces.argc());
}

test "argvSplit releases partial allocations when duplication fails" {
    const Harness = struct {
        fn run(allocator: std.mem.Allocator, text: []const u8) !void {
            var result = try argvSplit(allocator, text);
            defer result.deinit();
        }
    };

    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        Harness.run,
        .{"alpha beta gamma"},
    );
}

test "argvSplit preserves literal shell-like bytes and embedded nul tokens" {
    var result = try argv_split(std.testing.allocator, "  key=value  \"quoted\"  path\\name\x00tail  ");
    defer argv_free(&result);

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("key=value", result.argv[0]);
    try std.testing.expectEqualStrings("\"quoted\"", result.argv[1]);
    try std.testing.expectEqualStrings("path\\name\x00tail", result.argv[2]);
    try std.testing.expectEqual(@as(usize, 14), result.argv[2].len);
    try std.testing.expectEqual(@as(u8, 0), result.argv[2][9]);

    result.argv[0][0] = 'K';
    try std.testing.expectEqualStrings("Key=value", result.argv[0]);
}

test "argvSplit treats exactly ASCII whitespace bytes as separators" {
    const whitespace = [_]u8{ ' ', '\t', '\n', '\r', 0x0b, 0x0c };
    for (whitespace) |separator| {
        var text = [_]u8{ separator, 'a', separator, 'b', separator };
        var result = try argvSplit(std.testing.allocator, text[0..]);
        defer result.deinit();

        try std.testing.expectEqual(@as(usize, 2), result.argc());
        try std.testing.expectEqualStrings("a", result.argv[0]);
        try std.testing.expectEqualStrings("b", result.argv[1]);
    }

    const controls = [_]u8{ 0x00, 0x01, 0x1f, 0x7f };
    for (controls) |control| {
        var text = [_]u8{ 'a', control, 'b' };
        var result = try argv_split(std.testing.allocator, text[0..]);
        defer argv_free(&result);

        try std.testing.expectEqual(@as(usize, 1), result.argc());
        try std.testing.expectEqualSlices(u8, text[0..], result.argv[0]);
    }
}

test "argvFree is safe after repeated cleanup" {
    var result = try argv_split(std.testing.allocator, "alpha beta");

    argv_free(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    argv_free(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}
