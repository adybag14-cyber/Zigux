const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf32_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const elf64_header = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const truncated_header = [_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };
const not_elf_header = [_]u8{ 0x00, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
const invalid_class_header = [_]u8{ 0x7f, 'E', 'L', 'F', 0xff, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

const Case = struct {
    name: []const u8,
    input: []const u8,
    exit_code: u8,
    stdout: []const u8,
    stderr: []const u8,
};

const cases = [_]Case{
    .{
        .name = "ELF32 writes only stdout",
        .input = &elf32_header,
        .exit_code = 0,
        .stdout = "#define KERNEL_ELFCLASS ELFCLASS32\n",
        .stderr = "",
    },
    .{
        .name = "ELF64 writes only stdout",
        .input = &elf64_header,
        .exit_code = 0,
        .stdout = "#define KERNEL_ELFCLASS ELFCLASS64\n",
        .stderr = "",
    },
    .{
        .name = "truncated writes only stderr",
        .input = &truncated_header,
        .exit_code = 1,
        .stdout = "",
        .stderr = "Error: input truncated\n",
    },
    .{
        .name = "non-ELF writes only stderr",
        .input = &not_elf_header,
        .exit_code = 1,
        .stdout = "",
        .stderr = "Error: not ELF\n",
    },
    .{
        .name = "invalid class writes neither stream",
        .input = &invalid_class_header,
        .exit_code = 1,
        .stdout = "",
        .stderr = "",
    },
};

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

test "runMkElfconfig partitions every public outcome by output channel" {
    for (cases) |case| {
        var stdout = try Capture.init(std.testing.allocator);
        defer stdout.deinit();
        var stderr = try Capture.init(std.testing.allocator);
        defer stderr.deinit();

        const exit_code = try mk_elfconfig.runMkElfconfig(case.input, &stdout, &stderr);

        try std.testing.expectEqual(case.exit_code, exit_code);
        try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
        try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
    }
}

test "output partition remains based on the first complete ident only" {
    for (cases) |case| {
        if (case.input.len < 16) continue;

        var payload = std.ArrayList(u8).empty;
        defer payload.deinit(std.testing.allocator);
        try payload.appendSlice(std.testing.allocator, case.input);
        try payload.appendSlice(std.testing.allocator, &elf64_header);
        try payload.appendSlice(std.testing.allocator, &not_elf_header);

        var stdout = try Capture.init(std.testing.allocator);
        defer stdout.deinit();
        var stderr = try Capture.init(std.testing.allocator);
        defer stderr.deinit();

        const exit_code = try mk_elfconfig.runMkElfconfig(payload.items, &stdout, &stderr);

        try std.testing.expectEqual(case.exit_code, exit_code);
        try std.testing.expectEqualStrings(case.stdout, stdout.list.items);
        try std.testing.expectEqualStrings(case.stderr, stderr.list.items);
    }
}
