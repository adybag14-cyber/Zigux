const std = @import("std");

const bridge = @import("confdata_bridge.zig");

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

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
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

const raw_control_input =
    "CONFIG_CTRL=prefix\x01\x08\x0csuffix\n" ++
    "CONFIG_NAME=\"zigux\"\n" ++
    "# CONFIG_DEBUG is not set\n";

test "confdata bridge json surface escapes low control bytes in raw value entries" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator, raw_control_input, &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_CTRL\",\"kind\":\"value\",\"value\":\"prefix\\u0001\\b\\fsuffix\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x01) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x08) == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x0c) == null);
}

test "confdata bridge parsed summary preserves raw low control bytes before json escaping" {
    var summary = try bridge.parseConfig(std.testing.allocator, raw_control_input);
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqualStrings("CONFIG_CTRL", summary.entries[0].name);
    try std.testing.expectEqualStrings("prefix\x01\x08\x0csuffix", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_NAME", summary.entries[1].name);
    try std.testing.expectEqualStrings("zigux", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);
}

test "confdata bridge duplicate raw control assignment replaces prior value and stays escaped in json" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_CTRL=stable\n" ++
            "CONFIG_CTRL=next\x01value\x08tail\x0c\n" ++
            "CONFIG_FLAG=m\n",
        &capture,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":0") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_CTRL\",\"kind\":\"value\",\"value\":\"next\\u0001value\\btail\\f\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_FLAG\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"stable\"") == null);
}
