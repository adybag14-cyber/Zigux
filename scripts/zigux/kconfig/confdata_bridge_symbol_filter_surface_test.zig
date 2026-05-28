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

const filtered_input =
    \\CONFIG_GOOD=y
    \\CONFIG_BAD-NAME=m
    \\CONFIG_BAD TAB=value
    \\CONFIG_=ignored
    \\CONFIG_NEXT="visible"
    \\# CONFIG_SKIP-ME is not set
    \\# CONFIG_DISABLED is not set
    \\
;

test "confdata bridge json surface ignores malformed config symbol names" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator, filtered_input, &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_GOOD\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_NEXT\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_DISABLED\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_BAD-NAME") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_BAD TAB") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"CONFIG_SKIP-ME\"") == null);
}

test "confdata bridge parsed summary keeps only valid config symbols" {
    var summary = try bridge.parseConfig(std.testing.allocator, filtered_input);
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqualStrings("CONFIG_GOOD", summary.entries[0].name);
    try std.testing.expectEqualStrings("CONFIG_NEXT", summary.entries[1].name);
    try std.testing.expectEqualStrings("CONFIG_DISABLED", summary.entries[2].name);
}

test "confdata bridge malformed names do not replace adjacent valid duplicate states" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_GOOD=y
        \\CONFIG_GOOD-NEXT=m
        \\# CONFIG_GOOD-NEXT is not set
        \\# CONFIG_GOOD is not set
        \\CONFIG_GOOD=value
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 0), summary.unset_count);
    try std.testing.expectEqualStrings("CONFIG_GOOD", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", summary.entries[0].value);
}
