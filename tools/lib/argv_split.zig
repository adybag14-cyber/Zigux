const std = @import("std");

fn skipArg(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and !std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

fn skipSpaces(text: []const u8, start: usize) usize {
    var idx = start;
    while (idx < text.len and std.ascii.isWhitespace(text[idx])) : (idx += 1) {}
    return idx;
}

pub fn countArgc(text: []const u8) usize {
    var count: usize = 0;
    var idx: usize = 0;

    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx < text.len) {
            count += 1;
            idx = skipArg(text, idx);
        }
    }

    return count;
}

pub fn argvFree(allocator: std.mem.Allocator, argv: [][]u8) void {
    for (argv) |arg| {
        allocator.free(arg);
    }
    allocator.free(argv);
}

pub fn argvSplit(allocator: std.mem.Allocator, text: []const u8) ![][]u8 {
    const argc = countArgc(text);
    var argv = try allocator.alloc([]u8, argc);
    errdefer allocator.free(argv);

    var idx: usize = 0;
    var arg_index: usize = 0;
    errdefer {
        for (argv[0..arg_index]) |arg| {
            allocator.free(arg);
        }
    }

    while (idx < text.len) {
        idx = skipSpaces(text, idx);
        if (idx < text.len) {
            const end = skipArg(text, idx);
            argv[arg_index] = try allocator.dupe(u8, text[idx..end]);
            arg_index += 1;
            idx = end;
        }
    }

    return argv;
}

test "argv split counts and splits whitespace-separated arguments" {
    const allocator = std.testing.allocator;
    const argv = try argvSplit(allocator, " alpha  beta\tgamma\n");
    defer argvFree(allocator, argv);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("alpha", argv[0]);
    try std.testing.expectEqualStrings("beta", argv[1]);
    try std.testing.expectEqualStrings("gamma", argv[2]);
}

test "argv split returns an empty vector for blank input" {
    const allocator = std.testing.allocator;
    const argv = try argvSplit(allocator, "   \t\n");
    defer argvFree(allocator, argv);

    try std.testing.expectEqual(@as(usize, 0), argv.len);
    try std.testing.expectEqual(@as(usize, 0), countArgc("   \t\n"));
}
