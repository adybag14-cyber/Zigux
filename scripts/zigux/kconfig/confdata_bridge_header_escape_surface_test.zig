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

test "standalone confdata autoconf header escapes quoted string bytes" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(
        std.testing.allocator,
        "CONFIG_NAME=\"zigux\\\"bridge\\\\\"\n" ++
            "CONFIG_TAB=\"left\tfield\"\n" ++
            "CONFIG_EMPTY=\n" ++
            "CONFIG_MOD=m\n" ++
            "CONFIG_OFF=n\n" ++
            "# CONFIG_UNSET is not set\n",
        .autoconf_header,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n" ++
            "#define CONFIG_TAB \"left\\tfield\"\n" ++
            "#define CONFIG_EMPTY \n" ++
            "#define CONFIG_MOD_MODULE 1\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_OFF") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_UNSET") == null);
}

test "standalone confdata autoconf header uses last escaped string state" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(
        std.testing.allocator,
        "CONFIG_PATH=\"drivers/old\"\n" ++
            "CONFIG_PATH=\"drivers\\\\zigux\\\"bridge\"\n",
        .autoconf_header,
        &capture,
    );

    try std.testing.expectEqualStrings(
        "#define CONFIG_PATH \"drivers\\\\zigux\\\"bridge\"\n",
        capture.list.items,
    );
}
