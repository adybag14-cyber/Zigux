const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elf64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const not_elf_text = "Error: not ELF\n";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 96),
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

fn expectRun(input: []const u8, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfig(input, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

fn appendPayload(first: [16]u8, payload: []const u8) ![]u8 {
    const buffer = try std.testing.allocator.alloc(u8, first.len + payload.len);
    errdefer std.testing.allocator.free(buffer);

    @memcpy(buffer[0..first.len], &first);
    @memcpy(buffer[first.len..], payload);
    return buffer;
}

test "complete first non-ELF ident stays authoritative before later valid ELF32" {
    const first_non_elf = [_]u8{ 'Z', 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const later_elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const input = try appendPayload(first_non_elf, &later_elf32);
    defer std.testing.allocator.free(input);

    try expectRun(input, 1, "", not_elf_text);
}

test "complete first non-ELF ident stays authoritative before later valid ELF64" {
    const first_non_elf = [_]u8{ 0x7f, 'Z', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const later_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const input = try appendPayload(first_non_elf, &later_elf64);
    defer std.testing.allocator.free(input);

    try expectRun(input, 1, "", not_elf_text);
}

test "valid first ELF32 ident stays authoritative before later non-ELF ident" {
    const first_elf32 = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const later_non_elf = [_]u8{ 'Z', 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const input = try appendPayload(first_elf32, &later_non_elf);
    defer std.testing.allocator.free(input);

    try expectRun(input, 0, elf32_define, "");
}

test "valid first ELF64 ident stays authoritative before later non-ELF ident" {
    const first_elf64 = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const later_non_elf = [_]u8{ 0x7f, 'E', 'Z', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    const input = try appendPayload(first_elf64, &later_non_elf);
    defer std.testing.allocator.free(input);

    try expectRun(input, 0, elf64_define, "");
}
