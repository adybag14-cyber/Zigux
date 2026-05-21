const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !Capture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
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

test "confdata bridge canonicalizes uppercase tristates to lowercase in emitted summaries" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_ALPHA=Y
        \\CONFIG_BETA=M
        \\CONFIG_DEBUG=N trailing
        \\
    ;

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_ALPHA", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_BETA", summary.entries[1].name);
    try std.testing.expectEqualStrings("m", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEBUG", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"tristate\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}

test "confdata bridge lets uppercase tristates replace earlier visible states canonically" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_SWITCH is not set
        \\CONFIG_SWITCH=Y
        \\CONFIG_MODE=\"quoted\"
        \\CONFIG_MODE=M #comment
        \\CONFIG_DEPTH=7
        \\CONFIG_DEPTH=N trailing
        \\
    ;

    var summary = try bridge.parseConfig(allocator, input);
    defer bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[0].name);
    try std.testing.expectEqualStrings("y", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_MODE", summary.entries[1].name);
    try std.testing.expectEqualStrings("m", summary.entries[1].value);
    try std.testing.expectEqualStrings("CONFIG_DEPTH", summary.entries[2].name);
    try std.testing.expectEqualStrings("n", summary.entries[2].value);

    var capture = try Capture.init(allocator, 320);
    defer capture.deinit();

    try bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_SWITCH\",\"kind\":\"tristate\",\"value\":\"y\"},{\"name\":\"CONFIG_MODE\",\"kind\":\"tristate\",\"value\":\"m\"},{\"name\":\"CONFIG_DEPTH\",\"kind\":\"tristate\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
