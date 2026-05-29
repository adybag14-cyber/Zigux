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

test "standalone confdata export modes preserve duplicate first-order with final states" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA="early"
        \\CONFIG_GAMMA=m
        \\# CONFIG_BETA is not set
        \\CONFIG_ALPHA="final"
        \\CONFIG_GAMMA=n
        \\
    ;

    var auto_conf = try Capture.init(allocator);
    defer auto_conf.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(allocator, input, .auto_conf, &auto_conf);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=\"final\"\n" ++
            "CONFIG_GAMMA=n\n",
        auto_conf.list.items,
    );

    var header = try Capture.init(allocator);
    defer header.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(allocator, input, .autoconf_header, &header);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA \"final\"\n",
        header.list.items,
    );
}
