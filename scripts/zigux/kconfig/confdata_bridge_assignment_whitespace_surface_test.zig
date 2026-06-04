const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.bytes.appendSlice(self.allocator, rendered);
    }
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "standalone confdata bridge ignores assignment names with whitespace" {
    const input =
        "CONFIG_BEFORE=y\n" ++
        " CONFIG_LEADING=m\n" ++
        "CONFIG_TRAILING =7\n" ++
        "CONFIG_TAB\t=8\n" ++
        "CONFIG_AFTER=\"kept\"\n";

    var summary = try confdata_bridge.parseConfig(std.testing.allocator, input);
    defer confdata_bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 2), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_BEFORE", summary.entries[0].name);
    try std.testing.expectEqualStrings("tristate", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_AFTER", summary.entries[1].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("kept", summary.entries[1].value);
}

test "standalone confdata bridge keeps clean json after whitespace rejects" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_BEFORE=y\n" ++
            " CONFIG_LEADING=m\n" ++
            "CONFIG_TRAILING =7\n" ++
            "CONFIG_TAB\t=8\n" ++
            "CONFIG_AFTER=\"kept\"\n",
        &capture,
    );

    try expectContains(capture.bytes.items, "\"set\":2");
    try expectContains(capture.bytes.items, "\"unset\":0");
    try expectContains(capture.bytes.items, "\"name\":\"CONFIG_BEFORE\",\"kind\":\"tristate\",\"value\":\"y\"");
    try expectContains(capture.bytes.items, "\"name\":\"CONFIG_AFTER\",\"kind\":\"string\",\"value\":\"kept\"");
    try expectAbsent(capture.bytes.items, "CONFIG_LEADING");
    try expectAbsent(capture.bytes.items, "CONFIG_TRAILING");
    try expectAbsent(capture.bytes.items, "CONFIG_TAB");
}
