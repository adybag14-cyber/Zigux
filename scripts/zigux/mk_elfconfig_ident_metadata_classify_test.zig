const std = @import("std");
const mk = @import("mk_elfconfig.zig");

const ei_nident: usize = 16;
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

fn headerWithMetadata(class: u8, metadata: [11]u8) [ei_nident]u8 {
    var header = [_]u8{ 0x7f, 'E', 'L', 'F', class, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
    @memcpy(header[5..], &metadata);
    return header;
}

fn expectRun(input: []const u8, exit_code: u8, stdout_text: []const u8, stderr_text: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(exit_code, try mk.runMkElfconfig(input, &stdout, &stderr));
    try std.testing.expectEqualStrings(stdout_text, stdout.list.items);
    try std.testing.expectEqualStrings(stderr_text, stderr.list.items);
}

test "classify ignores non-class ident metadata bytes for ELF32 and ELF64" {
    const metadata_cases = [_][11]u8{
        .{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        .{ 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
        .{ 2, 1, 255, 3, 4, 5, 6, 7, 8, 9, 10 },
        .{ 255, 0, 127, 254, 253, 252, 251, 250, 249, 248, 247 },
    };

    for (metadata_cases) |metadata| {
        const elf32_header = headerWithMetadata(1, metadata);
        const elf64_header = headerWithMetadata(2, metadata);

        try std.testing.expectEqual(mk.Outcome.elf32, mk.classify(&elf32_header));
        try std.testing.expectEqual(mk.Outcome.elf64, mk.classify(&elf64_header));
    }
}

test "public entry ignores non-class metadata when rendering success" {
    const elf32_header = headerWithMetadata(1, .{ 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 245 });
    const elf64_header = headerWithMetadata(2, .{ 0, 3, 0, 7, 0, 11, 0, 13, 0, 17, 0 });

    try expectRun(&elf32_header, 0, elf32_define, "");
    try expectRun(&elf64_header, 0, elf64_define, "");
}

test "public entry ignores metadata before reporting invalid class" {
    const invalid_headers = [_][ei_nident]u8{
        headerWithMetadata(0, .{ 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 }),
        headerWithMetadata(3, .{ 2, 1, 255, 1, 2, 3, 4, 5, 6, 7, 8 }),
        headerWithMetadata(255, .{ 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255 }),
    };

    for (invalid_headers) |header| {
        try std.testing.expectEqual(mk.Outcome.invalid_class, mk.classify(&header));
        try expectRun(&header, 1, "", "");
    }
}
