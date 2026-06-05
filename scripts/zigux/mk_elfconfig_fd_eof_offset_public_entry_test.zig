const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass64_define = "#define KERNEL_ELFCLASS ELFCLASS64\n";
const truncated_text = "Error: input truncated\n";

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

fn expectFdOutcome(file: anytype, expected_exit: u8, expected_stdout: []const u8, expected_stderr: []const u8) !void {
    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(expected_exit, exit_code);
    try std.testing.expectEqualStrings(expected_stdout, stdout.list.items);
    try std.testing.expectEqualStrings(expected_stderr, stderr.list.items);
}

test "fd-backed empty current offset is truncated even after prior valid header" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "header_then_eof.bin", .{ .read = true });
    defer file.close(io);

    const header = [_]u8{
        0x7f, 'E', 'L', 'F', 2, 1, 1, 0,
        0,    0,   0,   0,   0, 0, 0, 0,
    };
    try file.writePositionalAll(io, &header, 0);

    try expectFdOutcome(file, 0, elfclass64_define, "");

    try expectFdOutcome(file, 1, "", truncated_text);
}

test "fd-backed empty file reports truncated output partition" {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, "empty.bin", .{ .read = true });
    defer file.close(io);

    try expectFdOutcome(file, 1, "", truncated_text);
}
