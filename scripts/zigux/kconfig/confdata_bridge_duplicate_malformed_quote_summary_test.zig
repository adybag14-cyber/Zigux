const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    pub fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    pub fn deinit(self: *Capture) void {
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

fn expectEntry(summary: confdata_bridge.Summary, index: usize, name: []const u8, value: []const u8) !void {
    try std.testing.expectEqualStrings(name, summary.entries[index].name);
    try std.testing.expectEqualStrings(value, summary.entries[index].value);
}

test "confdata bridge preserves prior duplicate value after malformed quoted reassignment" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="unterminated
        \\# CONFIG_DEBUG is not set
        \\CONFIG_DEBUG="broken
        \\CONFIG_GAMMA="still-broken
        \\CONFIG_BETA=y
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try expectEntry(summary, 0, "CONFIG_ALPHA", "stable");
    try expectEntry(summary, 1, "CONFIG_DEBUG", "n");
    try expectEntry(summary, 2, "CONFIG_BETA", "y");
}

test "confdata bridge summary json keeps only preserved duplicate state after malformed quoted reassignment" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="unterminated
        \\# CONFIG_DEBUG is not set
        \\CONFIG_DEBUG="broken
        \\CONFIG_GAMMA="still-broken
        \\CONFIG_BETA=y
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_GAMMA") == null);
}
