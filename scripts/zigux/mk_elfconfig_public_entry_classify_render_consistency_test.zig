const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 64),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *@This(), bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }
};

const Rendered = struct {
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

fn renderClassified(allocator: std.mem.Allocator, input: []const u8) !Rendered {
    var stdout = try Capture.init(allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.renderOutcome(
        &stdout,
        &stderr,
        mk_elfconfig.classify(input),
    );

    return .{
        .exit_code = exit_code,
        .stdout = try allocator.dupe(u8, stdout.list.items),
        .stderr = try allocator.dupe(u8, stderr.list.items),
    };
}

fn renderPublicEntry(allocator: std.mem.Allocator, input: []const u8) !Rendered {
    var stdout = try Capture.init(allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);

    return .{
        .exit_code = exit_code,
        .stdout = try allocator.dupe(u8, stdout.list.items),
        .stderr = try allocator.dupe(u8, stderr.list.items),
    };
}

fn expectPublicEntryMatchesClassifyThenRender(input: []const u8) !void {
    const allocator = std.testing.allocator;

    const expected = try renderClassified(allocator, input);
    defer allocator.free(expected.stdout);
    defer allocator.free(expected.stderr);

    const actual = try renderPublicEntry(allocator, input);
    defer allocator.free(actual.stdout);
    defer allocator.free(actual.stderr);

    try std.testing.expectEqual(expected.exit_code, actual.exit_code);
    try std.testing.expectEqualStrings(expected.stdout, actual.stdout);
    try std.testing.expectEqualStrings(expected.stderr, actual.stderr);
}

test "public entry is classify then render for every outcome" {
    const cases = [_][]const u8{
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0 },
        &[_]u8{ 0x7f, 'E', 'L', 'X', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        &[_]u8{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    };

    for (cases) |input| {
        try expectPublicEntryMatchesClassifyThenRender(input);
    }
}

test "public entry consistency ignores bytes after classified first ident" {
    const cases = [_][]const u8{
        &([_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } ++ [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1 }),
        &([_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } ++ [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1 }),
        &([_]u8{ 0x7f, 'E', 'L', 'F', 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } ++ [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1 }),
        &([_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 } ++ [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1 }),
    };

    for (cases) |input| {
        try expectPublicEntryMatchesClassifyThenRender(input);
    }
}
