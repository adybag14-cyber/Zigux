const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

fn expectKind(entry: confdata_bridge.Entry, expected_name: []const u8, comptime expected_kind_name: []const u8, expected_value: []const u8) !void {
    try std.testing.expectEqualStrings(expected_name, entry.name);
    try std.testing.expectEqual(@field(@TypeOf(entry.kind), expected_kind_name), entry.kind);
    try std.testing.expectEqualStrings(expected_value, entry.value);
}

test "confdata bridge collapses duplicate unset lines on the public summary surface" {
    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_REPEAT is not set
        \\# CONFIG_REPEAT is not set
        \\CONFIG_KEEP=7
        \\# CONFIG_OTHER is not set
        \\# CONFIG_OTHER is not set
        \\
    ;

    var summary = try confdata_bridge.parseConfig(allocator, input);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.set_count);
    try std.testing.expectEqual(@as(usize, 2), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);

    try expectKind(summary.entries[0], "CONFIG_REPEAT", "unset", "n");
    try expectKind(summary.entries[1], "CONFIG_KEEP", "value", "7");
    try expectKind(summary.entries[2], "CONFIG_OTHER", "unset", "n");
}

test "confdata bridge emits duplicate unset lines as one final visible unset entry per symbol" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }

        pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    const allocator = std.testing.allocator;
    const input =
        \\# CONFIG_REPEAT is not set
        \\# CONFIG_REPEAT is not set
        \\CONFIG_KEEP=7
        \\# CONFIG_OTHER is not set
        \\# CONFIG_OTHER is not set
        \\
    ;

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(allocator, input, &capture);
    try std.testing.expectEqualStrings(
        "{\"counts\":{\"set\":1,\"unset\":2},\"entries\":[{\"name\":\"CONFIG_REPEAT\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_KEEP\",\"kind\":\"value\",\"value\":\"7\"},{\"name\":\"CONFIG_OTHER\",\"kind\":\"unset\",\"value\":\"n\"}]}\n",
        capture.list.items,
    );
}
