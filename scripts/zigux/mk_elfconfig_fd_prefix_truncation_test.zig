const std = @import("std");
const mk_elfconfig = @import("mk_elfconfig.zig");

const elfclass64: u8 = 2;
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

fn expectFdTruncatedAtEof(prefix: []const u8, file_name: []const u8) !void {
    var temp_dir = std.testing.tmpDir(.{});
    defer temp_dir.cleanup();
    const io = std.testing.io;
    const file = try temp_dir.dir.createFile(io, file_name, .{ .read = true });
    defer file.close(io);
    try file.writePositionalAll(io, prefix, 0);

    var stdout = try Capture.init(std.testing.allocator);
    defer stdout.deinit();
    var stderr = try Capture.init(std.testing.allocator);
    defer stderr.deinit();

    const exit_code = try mk_elfconfig.runMkElfconfigFromFd(file.handle, &stdout, &stderr);
    try std.testing.expectEqual(@as(u8, 1), exit_code);
    try std.testing.expectEqualStrings("", stdout.list.items);
    try std.testing.expectEqualStrings(truncated_text, stderr.list.items);
}

test "fd-backed public entry reports every short ELF prefix as truncated at EOF" {
    const full_ident = [_]u8{
        0x7f, 'E', 'L', 'F', elfclass64, 1, 1, 0,
        0,    0,   0,   0,   0,          0, 0, 0,
    };

    var len: usize = 0;
    while (len < full_ident.len) : (len += 1) {
        var name_buf: [64]u8 = undefined;
        const name = try std.fmt.bufPrint(&name_buf, "short-elf-prefix-{d}.bin", .{len});
        try expectFdTruncatedAtEof(full_ident[0..len], name);
    }
}

test "fd-backed public entry reports every short non-ELF prefix as truncated at EOF" {
    const full_ident = [_]u8{
        0, 'N', 'O', 'T', elfclass64, 1, 1, 0,
        0, 0,   0,   0,   0,          0, 0, 0,
    };

    var len: usize = 0;
    while (len < full_ident.len) : (len += 1) {
        var name_buf: [64]u8 = undefined;
        const name = try std.fmt.bufPrint(&name_buf, "short-non-elf-prefix-{d}.bin", .{len});
        try expectFdTruncatedAtEof(full_ident[0..len], name);
    }
}
