const std = @import("std");
const confdata = @import("confdata_bridge.zig");

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

fn expectNoRawControlBytesExceptTrailingNewline(output: []const u8) !void {
    try std.testing.expect(output.len > 0);
    for (output, 0..) |byte, index| {
        if (index == output.len - 1) {
            try std.testing.expectEqual(@as(u8, '\n'), byte);
            continue;
        }
        try std.testing.expect(byte >= 0x20);
    }
}

test "standalone confdata quoted control bytes are json escaped" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata.runConfdataBridge(
        std.testing.allocator,
        "CONFIG_PROMPT=\"alpha\tbeta\rgamma\"\n" ++
            "CONFIG_VISIBLE=y\n" ++
            "# CONFIG_DISABLED is not set\n",
        &capture,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_PROMPT\",\"kind\":\"string\",\"value\":\"alpha\\tbeta\\rgamma\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_VISIBLE\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DISABLED\",\"kind\":\"unset\",\"value\":\"n\"") != null);
    try expectNoRawControlBytesExceptTrailingNewline(capture.list.items);
}

test "standalone confdata parse preserves quoted control bytes before json output" {
    var summary = try confdata.parseConfig(
        std.testing.allocator,
        "CONFIG_PROMPT=\"alpha\tbeta\rgamma\"\n",
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 1), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_PROMPT", summary.entries[0].name);
    try std.testing.expectEqualStrings("alpha\tbeta\rgamma", summary.entries[0].value);
}
