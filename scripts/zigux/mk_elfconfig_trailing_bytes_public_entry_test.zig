const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

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

test "public entry keeps trailing bytes behind an exact 32-bit ELF header from changing the first result" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfig(&input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "public entry keeps trailing bytes behind an exact 64-bit ELF header from changing the first result" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfig(&input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "public entry keeps trailing bytes behind an exact invalid-class header from changing the first result" {
    const input = [_]u8{
        0x7f, 'E', 'L', 'F', 3, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfig(&input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "public entry keeps trailing bytes behind an exact not-ELF header from changing the first result" {
    const input = [_]u8{
        0x00, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
        0x7f, 'E', 'L', 'F', 1, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk.runMkElfconfig(&input, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}
