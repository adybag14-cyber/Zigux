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
    while (idx < text.len and text[idx] != 0 and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn skipArg(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and text[idx] != 0 and !std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn countArgc(text: []const u8) usize {
    var idx: usize = 0;
    var count: usize = 0;

    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx >= text.len or text[idx] == 0) {
            break;
        }
        count += 1;
        idx = skipArg(text, idx);
    }

    return count;
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {
    const argc = countArgc(text);
    var argv = try allocator.alloc([]u8, argc);
    errdefer allocator.free(argv);

    var idx: usize = 0;
    var arg_idx: usize = 0;
    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx >= text.len or text[idx] == 0) {
            break;
        }

        const end = skipArg(text, idx);
        argv[arg_idx] = try allocator.dupe(u8, text[idx..end]);
        errdefer {
            for (argv[0 .. arg_idx + 1]) |arg| {
                allocator.free(arg);
            }
        }
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

test "argvSplit treats ascii control whitespace as separators and quotes literally" {
    var result = try argvSplit(std.testing.allocator, "\ralpha\x0bbeta\x0cgamma\r\n\"delta epsilon\" zeta");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 6), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
    try std.testing.expectEqualStrings("\"delta", result.argv[3]);
    try std.testing.expectEqualStrings("epsilon\"", result.argv[4]);
    try std.testing.expectEqualStrings("zeta", result.argv[5]);
}

test "argvSplit duplicates argument storage before the source buffer changes" {
    var source = [_]u8{ 'o', 'n', 'e', ' ', 't', 'w', 'o' };
    var result = try argvSplit(std.testing.allocator, &source);
    defer result.deinit();

    source[0] = 'X';
    source[4] = 'Y';

    try std.testing.expectEqualStrings("one", result.argv[0]);
    try std.testing.expectEqualStrings("two", result.argv[1]);
}

test "argvSplit stops at the first embedded NUL byte" {
    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', 0, 'g', 'a', 'm', 'm', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "argvSplit treats a NUL after leading whitespace as end of input" {
    const source = [_]u8{ ' ', '\t', 0, 'a', 'l', 'p', 'h', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argvSplit treats a NUL reached while skipping separator whitespace as end of input" {
    const source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', '\t', 0, 'b', 'e', 't', 'a' };
    var result = try argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqual(@as(usize, 1), result.argv.len);
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
}
