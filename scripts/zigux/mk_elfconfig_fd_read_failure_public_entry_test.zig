const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 32),
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

fn expectFdReadFailure(fd: std.posix.fd_t) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    try std.testing.expectError(
        error.Unexpected,
        mk_elfconfig.runMkElfconfigFromFd(fd, &stdout, &stderr),
    );
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings("", stderr.list.items);
}

test "fd-backed public entry propagates invalid fd read failure" {
    try expectFdReadFailure(-1);
}

test "fd-backed public entry propagates closed fd read failure" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "closed.bin", .{ .read = true });
    const fd = file.handle;
    file.close(io);

    try expectFdReadFailure(fd);
}
