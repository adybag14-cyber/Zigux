const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_ident = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_ident = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

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

fn edgeInvalidIdent(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn expectSilentInvalid(input: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

fn expectDefine(input: []const u8, expected: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(expected, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "invalid class edge values stay silent failures" {
    for ([_]u8{ 0, 3, 255 }) |class| {
        const ident = edgeInvalidIdent(class);
        try std.testing.expectEqual(mk_elfconfig.Outcome.invalid_class, mk_elfconfig.classify(&ident));
        try expectSilentInvalid(&ident);
    }
}

test "invalid edge class first header is not rescued by later valid headers" {
    for ([_]u8{ 0, 3, 255 }) |class| {
        const ident = edgeInvalidIdent(class);
        var input: [48]u8 = undefined;
        @memcpy(input[0..16], &ident);
        @memcpy(input[16..32], &elf32_ident);
        @memcpy(input[32..48], &elf64_ident);

        try expectSilentInvalid(&input);
    }
}

test "valid first header remains authoritative before invalid edge tails" {
    for ([_]u8{ 0, 3, 255 }) |class| {
        const invalid_tail = edgeInvalidIdent(class);
        var elf32_input: [32]u8 = undefined;
        @memcpy(elf32_input[0..16], &elf32_ident);
        @memcpy(elf32_input[16..32], &invalid_tail);
        try expectDefine(&elf32_input, "#define KERNEL_ELFCLASS ELFCLASS32\n");

        var elf64_input: [32]u8 = undefined;
        @memcpy(elf64_input[0..16], &elf64_ident);
        @memcpy(elf64_input[16..32], &invalid_tail);
        try expectDefine(&elf64_input, "#define KERNEL_ELFCLASS ELFCLASS64\n");
    }
}

test "non-ELF first header remains authoritative before invalid edge tails" {
    for ([_]u8{ 0, 3, 255 }) |class| {
        const invalid_tail = edgeInvalidIdent(class);
        var input: [32]u8 = undefined;
        @memcpy(input[0..16], &not_elf_ident);
        @memcpy(input[16..32], &invalid_tail);

        var stdout = try Capture.init(std.testing.allocator);
        defer stdout.deinit();
        var stderr = try Capture.init(std.testing.allocator);
        defer stderr.deinit();

        const exit_code = try mk_elfconfig.runMkElfconfig(&input, &stdout, &stderr);
        try std.testing.expectEqual(@as(u8, 1), exit_code);
        try std.testing.expectEqualStrings("", stdout.list.items);
        try std.testing.expectEqualStrings("Error: not ELF\n", stderr.list.items);
    }
}
