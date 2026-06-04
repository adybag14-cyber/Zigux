const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 256),
        };
    }

    fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.bytes.append(self.allocator, byte);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.bytes.appendSlice(self.allocator, rendered);
    }
};

test "standalone confdata bridge preserves equals bytes in raw values" {
    const input =
        "CONFIG_CMDLINE=root=/dev/vda1 console=ttyS0=115200n8\n" ++
        "# CONFIG_UNUSED is not set\n" ++
        "CONFIG_QUOTED=\"path=still-decoded\"\n";

    var summary = try confdata_bridge.parseConfig(std.testing.allocator, input);
    defer confdata_bridge.deinitSummary(std.testing.allocator, &summary);

    try std.testing.expectEqual(@as(usize, 2), summary.set_count);
    try std.testing.expectEqual(@as(usize, 1), summary.unset_count);
    try std.testing.expectEqual(@as(usize, 3), summary.entries.len);
    try std.testing.expectEqualStrings("CONFIG_CMDLINE", summary.entries[0].name);
    try std.testing.expectEqualStrings("value", @tagName(summary.entries[0].kind));
    try std.testing.expectEqualStrings("root=/dev/vda1 console=ttyS0=115200n8", summary.entries[0].value);
    try std.testing.expectEqualStrings("CONFIG_UNUSED", summary.entries[1].name);
    try std.testing.expectEqualStrings("unset", @tagName(summary.entries[1].kind));
    try std.testing.expectEqualStrings("CONFIG_QUOTED", summary.entries[2].name);
    try std.testing.expectEqualStrings("string", @tagName(summary.entries[2].kind));
    try std.testing.expectEqualStrings("path=still-decoded", summary.entries[2].value);
}

test "standalone confdata bridge emits equals-heavy values through public json" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridge(std.testing.allocator,
        \\CONFIG_CMDLINE=root=/dev/vda1 console=ttyS0=115200n8
        \\# CONFIG_UNUSED is not set
        \\CONFIG_QUOTED="path=still-decoded"
        \\
    , &capture);

    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_CMDLINE\",\"kind\":\"value\",\"value\":\"root=/dev/vda1 console=ttyS0=115200n8\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "\"name\":\"CONFIG_QUOTED\",\"kind\":\"string\",\"value\":\"path=still-decoded\"") != null);
}
