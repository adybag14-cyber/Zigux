const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

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

test "confdata bridge keeps explicit empty assignments distinct from quoted empty strings in summary state" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED=""
        \\# CONFIG_SWITCH is not set
        \\CONFIG_SWITCH=
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try std.testing.expectEqualStrings("CONFIG_EMPTY", summary.entries[0].name);
    try std.testing.expectEqual(.value, summary.entries[0].kind);
    try std.testing.expectEqualStrings("", summary.entries[0].value);

    try std.testing.expectEqualStrings("CONFIG_QUOTED", summary.entries[1].name);
    try std.testing.expectEqual(.string, summary.entries[1].kind);
    try std.testing.expectEqualStrings("", summary.entries[1].value);

    try std.testing.expectEqualStrings("CONFIG_SWITCH", summary.entries[2].name);
    try std.testing.expectEqual(.value, summary.entries[2].kind);
    try std.testing.expectEqualStrings("", summary.entries[2].value);
}

test "confdata bridge emits explicit empty assignments distinctly in json output" {
    const allocator = std.testing.allocator;
    const input =
        \\CONFIG_EMPTY=
        \\CONFIG_QUOTED=""
        \\# CONFIG_SWITCH is not set
        \\CONFIG_SWITCH=
        \\
    ;

    var capture = try Capture.init(allocator, 256);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":3,\"unset\":0},\"entries\":[{\"name\":\"CONFIG_EMPTY\",\"kind\":\"value\",\"value\":\"\"},{\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"\"},{\"name\":\"CONFIG_SWITCH\",\"kind\":\"value\",\"value\":\"\"}]}\n",
        capture.list.items,
    );
}
