const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";

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

const RunResult = struct {
    exit_code: u8,
    stdout: std.ArrayList(u8),
    stderr: std.ArrayList(u8),

    fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
        self.stdout.deinit(allocator);
        self.stderr.deinit(allocator);
    }
};

fn runFdBytes(name: []const u8, bytes: []const u8) !RunResult {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, name, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, bytes, 0);

    var stdout = try Capture.init(std.testing.allocator);
    errdefer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    errdefer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    return .{
        .exit_code = exit_code,
        .stdout = stdout.list,
        .stderr = stderr.list,
    };
}

fn noisyIdent(class: u8) [16]u8 {
    return .{
        0x7f, 'E',  'L',  'F',
        class, 0xff, 0x00, 0x7f,
        0x80, 0x55, 0xaa, 0x13,
        0x37, 0xfe, 0xed, 0x99,
    };
}

fn quietIdent(class: u8) [16]u8 {
    return .{
        0x7f, 'E', 'L', 'F',
        class, 1,   1,   0,
        0,    0,   0,   0,
        0,    0,   0,   0,
    };
}

test "fd-backed ELF32 success is driven by EI_CLASS despite noisy ident metadata" {
    const first = noisyIdent(1);
    var bytes: [32]u8 = undefined;
    @memcpy(bytes[0..16], &first);
    @memcpy(bytes[16..32], &quietIdent(2));

    var result = try runFdBytes("elf32_noisy_metadata.bin", &bytes);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), result.exit_code);
    try std.testing.expectEqualStrings(elfclass32_define, result.stdout.items);
    try std.testing.expectEqualStrings("", result.stderr.items);
}

test "fd-backed ELF64 success is driven by EI_CLASS despite noisy ident metadata" {
    const first = noisyIdent(2);
    var bytes: [32]u8 = undefined;
    @memcpy(bytes[0..16], &first);
    @memcpy(bytes[16..32], &quietIdent(1));

    var result = try runFdBytes("elf64_noisy_metadata.bin", &bytes);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 0), result.exit_code);
    try std.testing.expectEqualStrings(elfclass64_define, result.stdout.items);
    try std.testing.expectEqualStrings("", result.stderr.items);
}

test "fd-backed invalid class remains silent even with conventional metadata and later valid idents" {
    var first = quietIdent(3);
    first[5] = 1;
    first[6] = 1;
    first[7] = 0;

    var bytes: [48]u8 = undefined;
    @memcpy(bytes[0..16], &first);
    @memcpy(bytes[16..32], &quietIdent(1));
    @memcpy(bytes[32..48], &quietIdent(2));

    var result = try runFdBytes("invalid_class_metadata_tail.bin", &bytes);
    defer result.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(u8, 1), result.exit_code);
    try std.testing.expectEqualStrings("", result.stdout.items);
    try std.testing.expectEqualStrings("", result.stderr.items);
}
