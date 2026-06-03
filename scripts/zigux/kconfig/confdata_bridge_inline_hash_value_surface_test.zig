const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "standalone confdata keeps inline hash text in raw values" {
    const input =
        \\CONFIG_CMDLINE=root=/dev/vda # keep as value text
        \\# CONFIG_DEBUG is not set
        \\CONFIG_NEXT=42
        \\
    ;

    var summary = try confdata_bridge.parseConfig(std.testing.allocator, input);
    defer confdata_bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_CMDLINE", summary.entries[0].name);
    try std.testing.expectEqualStrings("root=/dev/vda # keep as value text", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[1].name);
    try std.testing.expectEqualStrings("n", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_NEXT", summary.entries[2].name);
    try std.testing.expectEqualStrings("42", summary.entries[2].value);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_CMDLINE\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "root=/dev/vda # keep as value text") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_DEBUG\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_NEXT\"") != null);
}
