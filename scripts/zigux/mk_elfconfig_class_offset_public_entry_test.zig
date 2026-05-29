const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elf_magic = [_]u8{ 0x7f, 'E', 'L', 'F' };

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

fn headerWith(class_byte: u8, filler: u8) [16]u8 {
    var header = [_]u8{filler} ** 16;
    @memcpy(header[0..elf_magic.len], &elf_magic);
    header[4] = class_byte;
    return header;
}

fn expectClassifies(expected: mk_elfconfig.Outcome, header: []const u8) !void {
    try std.testing.expectEqual(expected, mk_elfconfig.classify(header));
}

test "classify uses byte 4 as the only ELF class authority" {
    var elf32 = headerWith(1, 0xff);
    elf32[5] = 2;
    elf32[6] = 2;
    elf32[7] = 2;

    var elf64 = headerWith(2, 0x00);
    elf64[5] = 1;
    elf64[6] = 1;
    elf64[7] = 1;

    try expectClassifies(.elf32, &elf32);
    try expectClassifies(.elf64, &elf64);
}

test "classify ignores class-looking bytes after EI_CLASS" {
    var class_none = headerWith(0, 1);
    class_none[5] = 1;
    class_none[6] = 2;

    var class_future = headerWith(3, 2);
    class_future[5] = 1;
    class_future[6] = 2;

    var class_max = headerWith(0xff, 1);
    class_max[15] = 2;

    try expectClassifies(.invalid_class, &class_none);
    try expectClassifies(.invalid_class, &class_future);
    try expectClassifies(.invalid_class, &class_max);
}

test "runMkElfconfig renders according to EI_CLASS despite noisy ident tail" {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    var header = headerWith(2, 1);
    header[5] = 1;
    header[6] = 1;
    header[7] = 1;

    const exit_code = try mk_elfconfig.runMkElfconfig(
        &header,
        &stdout,
        &stderr,
    );

    try std.testing.expectEqual(@as(u8, 0), exit_code);
    try std.testing.expectEqualStrings("#define KERNEL_ELFCLASS ELFCLASS64\n", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}
