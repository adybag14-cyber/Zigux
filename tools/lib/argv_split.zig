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

fn cStringPrefix(text: []const u8) []const u8 {
    return text[0 .. std.mem.indexOfScalar(u8, text, 0) orelse text.len];
}

fn countArgc(text: []const u8) usize {
    const current = cStringPrefix(text);
    var idx: usize = 0;
    var count: usize = 0;

    while (idx < current.len) {
        idx = skipSpaces(current, idx);
        if (idx >= current.len) {
            break;
        }
        count += 1;
        idx = skipArg(current, idx);
    }

    return count;
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitResult {
    const current = cStringPrefix(text);
    const argc = countArgc(current);
    var argv = try allocator.alloc([]u8, argc);

    var idx: usize = 0;
    var arg_idx: usize = 0;
    errdefer {
        for (argv[0..arg_idx]) |arg| {
            allocator.free(arg);
        }
        allocator.free(argv);
    }
    while (idx < current.len) {
        idx = skipSpaces(current, idx);
        if (idx >= current.len) {
            break;
        }

        const end = skipArg(current, idx);
        argv[arg_idx] = try allocator.dupe(u8, current[idx..end]);
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

test "argvSplit duplicates tokens instead of aliasing the source buffer" {
    var text = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a' };
    var result = try argv_split(std.testing.allocator, text[0..]);
    defer argv_free(&result);

    text[0] = 'o';
    text[6] = 'z';

    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "argvSplit frees duplicated args when a later dupe fails" {
    try std.testing.checkAllAllocationFailures(std.testing.allocator, struct {
        fn run(allocator: std.mem.Allocator) !void {
            var result = try argvSplit(allocator, "alpha beta gamma");
            defer result.deinit();
            try std.testing.expectEqual(@as(usize, 3), result.argc());
        }
    }.run, .{});
}

test "argvSplit stops at the first embedded nul byte" {
    var result = try argvSplit(std.testing.allocator, "alpha beta\x00gamma delta");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "argvSplit truncates a token at an embedded nul byte" {
    var result = try argvSplit(std.testing.allocator, "alpha\x00beta gamma");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
}

test "argvSplit treats a leading nul byte as blank input" {
    var result = try argvSplit(std.testing.allocator, "\x00ignored tail");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);
}

test "argvSplit treats carriage return vertical tab and form feed as separators" {
    var result = try argvSplit(std.testing.allocator, "alpha\r\x0bbeta\x0cgamma\x00delta");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
}

test "argvSplit keeps non-whitespace control bytes inside a token" {
    var result = try argvSplit(std.testing.allocator, "alpha\x07beta gamma\x1fdelta\x00tail");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 2), result.argc());
    try std.testing.expectEqualStrings("alpha\x07beta", result.argv[0]);
    try std.testing.expectEqualStrings("gamma\x1fdelta", result.argv[1]);
}

test "argvSplit keeps quotes backslashes and equals literal inside tokens" {
    var result = try argvSplit(
        std.testing.allocator,
        "alpha=\"beta\" 'gamma' path\\with\\slashes key=value\x00tail ignored",
    );
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 4), result.argc());
    try std.testing.expectEqualStrings("alpha=\"beta\"", result.argv[0]);
    try std.testing.expectEqualStrings("'gamma'", result.argv[1]);
    try std.testing.expectEqualStrings("path\\with\\slashes", result.argv[2]);
    try std.testing.expectEqualStrings("key=value", result.argv[3]);
}

test "argvSplit matches ASCII separator classification byte-for-byte before the first nul" {
    var byte: u8 = 1;
    while (byte < 0x80) : (byte += 1) {
        var input = [_]u8{ 'a', 'l', 'p', 'h', 'a', byte, 'b', 'e', 't', 'a', 0, 't', 'a', 'i', 'l' };
        var result = try argvSplit(std.testing.allocator, input[0..]);
        defer result.deinit();

        if (std.ascii.isWhitespace(byte)) {
            try std.testing.expectEqual(@as(usize, 2), result.argc());
            try std.testing.expectEqualStrings("alpha", result.argv[0]);
            try std.testing.expectEqualStrings("beta", result.argv[1]);
        } else {
            try std.testing.expectEqual(@as(usize, 1), result.argc());
            try std.testing.expectEqualStrings(input[0..10], result.argv[0]);
        }
    }
}

test "countArgc stops at the first embedded nul byte" {
    try std.testing.expectEqual(@as(usize, 0), countArgc("\x00ignored tail"));
    try std.testing.expectEqual(@as(usize, 2), countArgc("alpha beta\x00gamma delta"));
    try std.testing.expectEqual(@as(usize, 0), countArgc(" \t\x00gamma delta"));
    try std.testing.expectEqual(@as(usize, 1), countArgc("alpha\x00 beta gamma"));
}

test "argvSplit reset state stays reusable after deinit and argv_free" {
    var result = try argvSplit(std.testing.allocator, "alpha beta");
    try std.testing.expectEqual(@as(usize, 2), result.argc());

    result.deinit();
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    argv_free(&result);
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    const allocator = result.allocator;
    result = try argvSplit(allocator, "gamma");
    defer result.deinit();
    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqualStrings("gamma", result.argv[0]);
}
