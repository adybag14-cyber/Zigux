const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

test "standalone confdata bridge preserves BOM and CRLF json surface" {
    const allocator = std.testing.allocator;
    const input =
        "\xef\xbb\xbfCONFIG_ALPHA=y\r\n" ++
        "CONFIG_NAME=\"zigux\"\r\n" ++
        "# CONFIG_DEBUG is not set\r\n" ++
        "\xef\xbb\xbfCONFIG_BETA=m\r\n" ++
        "CONFIG_EMPTY=\r\n";

    var json = try Capture.init(allocator);
    defer json.deinit();
    try confdata_bridge.runConfdataBridge(allocator, input, &json);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":1},\"entries\":[" ++
            "{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"}," ++
            "{\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"}," ++
            "{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"}," ++
            "{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        json.list.items,
    );
}
