const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass32: u8 = 1;
const elfclass64: u8 = 2;

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

fn invalidClassHeader(class: u8) [16]u8 {
    return .{
        0x7f, 'E', 'L', 'F', class, 1, 1, 0,
        0,    0,   0,   0,   0,     0, 0, 0,
    };
}

fn validClassHeader(class: u8) [16]u8 {
    return .{
        0x7f, 'E', 'L', 'F', class, 1, 1, 0,
        0,    0,   0,   0,   0,     0, 0, 0,
    };
}

fn expectFdInvalidClass(bytes: []const u8) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();

    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "invalid-class.bin", .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, bytes, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "fd-backed invalid ELF class low boundary stays silent at EOF" {
    const header = invalidClassHeader(0);
    try expectFdInvalidClass(&header);
}

test "fd-backed invalid ELF class adjacent boundary stays silent at EOF" {
    const header = invalidClassHeader(3);
    try expectFdInvalidClass(&header);
}

test "fd-backed invalid ELF class high boundary stays silent at EOF" {
    const header = invalidClassHeader(255);
    try expectFdInvalidClass(&header);
}

test "fd-backed first invalid class remains authoritative before later valid header" {
    const invalid = invalidClassHeader(0);
    const valid32 = validClassHeader(elfclass32);
    const valid64 = validClassHeader(elfclass64);

    var bytes: [invalid.len + valid32.len + valid64.len]u8 = undefined;
    @memcpy(bytes[0..invalid.len], &invalid);
    @memcpy(bytes[invalid.len..][0..valid32.len], &valid32);
    @memcpy(bytes[invalid.len + valid32.len ..], &valid64);

    try expectFdInvalidClass(&bytes);
}
