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

fn cStringPrefix(text: []const u8) []const u8 {
    const end = std.mem.indexOfScalar(u8, text, 0) orelse text.len;
    return text[0..end];
}

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
    const bounded_text = cStringPrefix(text);
    const argc = countArgc(bounded_text);
    var argv = try allocator.alloc([]u8, argc);

    var idx: usize = 0;
    var arg_idx: usize = 0;
    errdefer {
        freeArgvPrefix(allocator, argv, arg_idx);
        allocator.free(argv);
    }
    while (idx < bounded_text.len) {
        idx = skipSpaces(bounded_text, idx);
        if (idx >= bounded_text.len) {
            break;
        }

        const end = skipArg(bounded_text, idx);
        argv[arg_idx] = try allocator.dupe(u8, bounded_text[idx..end]);
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

test "argvSplit stops at the first embedded nul byte" {
    var split = try argvSplit(std.testing.allocator, "alpha beta\x00ignored tail");
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 2), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);

    var leading_nul = try argv_split(std.testing.allocator, "\x00alpha beta");
    defer argv_free(&leading_nul);
    try std.testing.expectEqual(@as(usize, 0), leading_nul.argc());
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
