const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        var buffer: [32]u8 = undefined;
        const text = try std.fmt.bufPrint(&buffer, fmt, args);
        try self.writeAll(text);
    }
};

test "standalone confdata bridge keeps unset comments strict" {
    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();

    const input =
        "# CONFIG_ALPHA is not set\n" ++
        "#\tCONFIG_BETA is not set\n" ++
        "#  CONFIG_GAMMA is not set\n" ++
        "# CONFIG_DELTA is not set \n" ++
        "CONFIG_EPSILON=m\n";

    try confdata_bridge.runConfdataBridge(std.testing.allocator, input, &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"counts\":{\"set\":1,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"unset\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_EPSILON\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_BETA") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_GAMMA") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_DELTA") == null);
}
