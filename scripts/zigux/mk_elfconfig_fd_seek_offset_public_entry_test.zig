const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32_define = "#define KERNEL_ELFCLASS ELFCLASS32\n";
const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";
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

const Header = [16]u8;

fn elfHeader(class: u8) Header {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn notElfHeader() Header {
    return .{ 0, 'E', 'L', 'F', 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn appendHeader(list: *std.ArrayList(u8), allocator: std.mem.Allocator, header: Header) !void {
    try list.appendSlice(allocator, &header);
}

fn advanceFd(fd: std.posix.fd_t, byte_count: usize) !void {
    var consumed: [64]u8 = undefined;
    var total: usize = 0;
    while (total < byte_count) {
        const want = @min(consumed.len, byte_count - total);
        const count = try std.posix.read(fd, consumed[0..want]);
        try std.testing.expect(count != 0);
        total += count;
    }
}

fn expectFdRunAfterPrefix(
    payload: []const u8,
    prefix_len: usize,
    expected_exit_code: u8,
    expected_stdout: []const u8,
    expected_stderr: []const u8,
) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "fd_offset.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, payload, 0);
    try advanceFd(file.handle, prefix_len);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit_code, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "fd-backed public entry reads ELF64 from current descriptor offset" {
    const allocator = std.testing.allocator;
    const prefix = "skip this prefix";
    var payload = try std.ArrayList(u8).initCapacity(allocator, 64);
    defer payload.deinit(allocator);

    try payload.appendSlice(allocator, prefix);
    try appendHeader(&payload, allocator, elfHeader(2));
    try appendHeader(&payload, allocator, notElfHeader());
    try appendHeader(&payload, allocator, elfHeader(1));

    try expectFdRunAfterPrefix(payload.items, prefix.len, 0, elfclass64_define, "");
}

test "fd-backed public entry reads invalid class from current descriptor offset" {
    const allocator = std.testing.allocator;
    const prefix = "discarded valid elf32";
    var payload = try std.ArrayList(u8).initCapacity(allocator, 64);
    defer payload.deinit(allocator);

    try payload.appendSlice(allocator, prefix);
    try appendHeader(&payload, allocator, elfHeader(3));
    try appendHeader(&payload, allocator, elfHeader(2));

    try expectFdRunAfterPrefix(payload.items, prefix.len, 1, "", "");
}

test "fd-backed public entry reports non-ELF at current descriptor offset" {
    const allocator = std.testing.allocator;
    const prefix = "ignored";
    var payload = try std.ArrayList(u8).initCapacity(allocator, 64);
    defer payload.deinit(allocator);

    try payload.appendSlice(allocator, prefix);
    try appendHeader(&payload, allocator, notElfHeader());
    try appendHeader(&payload, allocator, elfHeader(2));

    try expectFdRunAfterPrefix(payload.items, prefix.len, 1, "", not_elf_text);
}

test "fd-backed public entry reports truncation after current descriptor offset" {
    const allocator = std.testing.allocator;
    const prefix = "ignored complete prefix";
    var payload = try std.ArrayList(u8).initCapacity(allocator, 64);
    defer payload.deinit(allocator);

    try payload.appendSlice(allocator, prefix);
    try payload.appendSlice(allocator, &[_]u8{ 0x7f, 'E', 'L', 'F', 1, 1, 1 });

    try expectFdRunAfterPrefix(payload.items, prefix.len, 1, "", truncated_text);
}

test "fd-backed public entry can read ELF32 after a skipped valid ELF64 header" {
    const allocator = std.testing.allocator;
    const skipped = elfHeader(2);
    var payload = try std.ArrayList(u8).initCapacity(allocator, 64);
    defer payload.deinit(allocator);

    try appendHeader(&payload, allocator, skipped);
    try appendHeader(&payload, allocator, elfHeader(1));
    try appendHeader(&payload, allocator, notElfHeader());

    try expectFdRunAfterPrefix(payload.items, skipped.len, 0, elfclass32_define, "");
}
