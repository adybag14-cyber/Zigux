const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

fn ident(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn appendIdent(buffer: *std.ArrayList(u8), allocator: std.mem.Allocator, class: u8) !void {
    const bytes = ident(class);
    try buffer.appendSlice(allocator, &bytes);
}

fn expectInvalidClass(input: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

fn expectSuccess(input: []const u8, expected: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(expected, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "middle invalid class values are silent failures" {
    const classes = [_]u8{ 4, 5, 7, 16, 42, 127, 128, 200, 254 };

    for (classes) |class| {
        const header = ident(class);
        try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(&header));
        try expectInvalidClass(&header);
    }
}

test "invalid class first ident is not rescued by a later valid ident" {
    const invalid_classes = [_]u8{ 4, 42, 127, 128, 254 };

    for (invalid_classes) |class| {
        var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 48);
        defer input.deinit(std.testing.allocator);

        try appendIdent(&input, std.testing.allocator, class);
        try appendIdent(&input, std.testing.allocator, 1);
        try appendIdent(&input, std.testing.allocator, 2);

        try expectInvalidClass(input.items);
    }
}

test "valid class first ident remains authoritative before invalid class tail" {
    inline for (.{ .{ 1, elf32_define }, .{ 2, elf64_define } }) |case| {
        var input = try std.ArrayList(u8).initCapacity(std.testing.allocator, 48);
        defer input.deinit(std.testing.allocator);

        try appendIdent(&input, std.testing.allocator, case[0]);
        try appendIdent(&input, std.testing.allocator, 127);
        try appendIdent(&input, std.testing.allocator, 254);

        try expectSuccess(input.items, case[1]);
    }
}
