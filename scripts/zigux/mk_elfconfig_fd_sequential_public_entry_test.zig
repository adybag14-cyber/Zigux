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
            .list = try std.ArrayList(u8).initCapacity(allocator, 128),
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

fn elfIdent(class: u8) [16]u8 {
    return .{ 0x7f, 'E', 'L', 'F', class, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn nonElfIdent() [16]u8 {
    return .{ 'n', 'o', 't', '!', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
}

fn writeChunks(file: anytype, first: []const u8, second: []const u8) !void {
    const io = std.testing.io;
    try file.writePositionalAll(io, first, 0);
    try file.writePositionalAll(io, second, first.len);
}

test "fd-backed repeated calls consume one ident per call" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "two-valid-idents.bin", .{ .read = true });
    defer file.close(io);

    const first = elfIdent(2);
    const second = elfIdent(1);
    try writeChunks(file, &first, &second);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    stdout.list.clearRetainingCapacity();
    stderr.list.clearRetainingCapacity();

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "fd-backed second call reports the next ident failure only" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "valid-then-not-elf.bin", .{ .read = true });
    defer file.close(io);

    const first = elfIdent(2);
    const second = nonElfIdent();
    try writeChunks(file, &first, &second);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    stdout.list.clearRetainingCapacity();
    stderr.list.clearRetainingCapacity();

    try std.testing.expectEqual(@as(u8, 1), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(not_elf_text, stderr.list.items);
}

test "fd-backed second call sees short trailing ident as truncation" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "valid-then-short.bin", .{ .read = true });
    defer file.close(io);

    const first = elfIdent(1);
    const short_second = [_]u8{ 0x7f, 'E', 'L', 'F', 2, 1, 1 };
    try writeChunks(file, &first, &short_second);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings(elfclass32_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    stdout.list.clearRetainingCapacity();
    stderr.list.clearRetainingCapacity();

    try std.testing.expectEqual(@as(u8, 1), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "fd-backed invalid first class still advances to a later valid ident" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "invalid-then-valid.bin", .{ .read = true });
    defer file.close(io);

    const first = elfIdent(0);
    const second = elfIdent(2);
    try writeChunks(file, &first, &second);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectEqual(@as(u8, 1), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);

    try std.testing.expectEqual(@as(u8, 0), try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr));
    try std.testing.expectEqualStrings(elfclass64_define, stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}
