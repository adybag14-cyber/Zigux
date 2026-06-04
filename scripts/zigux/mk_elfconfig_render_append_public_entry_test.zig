const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
const not_elf_text = "Error: not ELF\n";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn initPrefilled(allocator: std.mem.Allocator, prefix: []const u8) !@This() {
        var list = try std.ArrayList(u8).initCapacity(allocator, 128);
        try list.appendSlice(allocator, prefix);
        return .{
            .list = list,
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

test "renderOutcome appends ELF32 output without clearing stderr" {
    var stdout = try Capture.initPrefilled(std.testing.allocator, "stdout-prefix:");
    defer stdout.deinit();
    var stderr = try Capture.initPrefilled(std.testing.allocator, "stderr-prefix:");
    defer stderr.deinit();

    const exit_code = try mk.renderOutcome(&stdout, &stderr, .elf32);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:" ++ elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:", stderr.list.items);
}

test "renderOutcome appends ELF64 output without clearing stderr" {
    var stdout = try Capture.initPrefilled(std.testing.allocator, "stdout-prefix:");
    defer stdout.deinit();
    var stderr = try Capture.initPrefilled(std.testing.allocator, "stderr-prefix:");
    defer stderr.deinit();

    const exit_code = try mk.renderOutcome(&stdout, &stderr, .elf64);
    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:" ++ elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:", stderr.list.items);
}

test "renderOutcome appends truncated diagnostic without clearing stdout" {
    var stdout = try Capture.initPrefilled(std.testing.allocator, "stdout-prefix:");
    defer stdout.deinit();
    var stderr = try Capture.initPrefilled(std.testing.allocator, "stderr-prefix:");
    defer stderr.deinit();

    const exit_code = try mk.renderOutcome(&stdout, &stderr, .truncated);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:", stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:" ++ truncated_text, stderr.list.items);
}

test "renderOutcome appends non-ELF diagnostic without clearing stdout" {
    var stdout = try Capture.initPrefilled(std.testing.allocator, "stdout-prefix:");
    defer stdout.deinit();
    var stderr = try Capture.initPrefilled(std.testing.allocator, "stderr-prefix:");
    defer stderr.deinit();

    const exit_code = try mk.renderOutcome(&stdout, &stderr, .not_elf);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:", stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:" ++ not_elf_text, stderr.list.items);
}

test "renderOutcome invalid class returns failure without touching either writer" {
    var stdout = try Capture.initPrefilled(std.testing.allocator, "stdout-prefix:");
    defer stdout.deinit();
    var stderr = try Capture.initPrefilled(std.testing.allocator, "stderr-prefix:");
    defer stderr.deinit();

    const exit_code = try mk.renderOutcome(&stdout, &stderr, .invalid_class);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("stdout-prefix:", stdout.list.items);
    try std.testing.expectEqualStrings("stderr-prefix:", stderr.list.items);
}
