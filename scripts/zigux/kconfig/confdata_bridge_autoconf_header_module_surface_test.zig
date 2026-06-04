const std = @import("std");
const confdata = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "standalone confdata autoconf header keeps module tristate suffix" {
    var summary = try confdata.parseConfig(std.testing.allocator,
        \\CONFIG_BUILTIN=y
        \\CONFIG_DRIVER=m
        \\CONFIG_DISABLED=n
        \\# CONFIG_UNSET is not set
        \\CONFIG_COUNT=7
        \\CONFIG_NAME="zigux"
        \\
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata.emitAutoconfHeaderExports(&capture, summary);
    try std.testing.expectEqualStrings(
        "#define CONFIG_BUILTIN 1\n" ++
            "#define CONFIG_DRIVER_MODULE 1\n" ++
            "#define CONFIG_COUNT 7\n" ++
            "#define CONFIG_NAME \"zigux\"\n",
        capture.list.items,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_DISABLED") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_UNSET") == null);
}
