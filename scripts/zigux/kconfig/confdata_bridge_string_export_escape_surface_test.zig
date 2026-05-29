const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) TestCapture {
        return .{
            .allocator = allocator,
            .list = .empty,
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn parseStringExportSummary(allocator: std.mem.Allocator) !confdata_bridge.Summary {
    return confdata_bridge.parseConfig(allocator,
        \\CONFIG_QUOTED="quote\"slash\\tab\tcr\rnl\n"
        \\CONFIG_KEEP=y
        \\# CONFIG_SKIP is not set
        \\
    );
}

test "standalone confdata string exports escape auto.conf quoted bytes" {
    const allocator = std.testing.allocator;
    var summary = try parseStringExportSummary(allocator);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    var capture = TestCapture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.emitAutoConfExports(&capture, summary);

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "CONFIG_QUOTED=\"quote\\\"slash\\\\tabtcrrnln\"\n",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_KEEP=y\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_SKIP") == null);
}

test "standalone confdata string exports escape autoconf header quoted bytes" {
    const allocator = std.testing.allocator;
    var summary = try parseStringExportSummary(allocator);
    defer confdata_bridge.deinitSummary(allocator, &summary);

    var capture = TestCapture.init(allocator);
    defer capture.deinit();

    try confdata_bridge.emitAutoconfHeaderExports(&capture, summary);

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "#define CONFIG_QUOTED \"quote\\\"slash\\\\tabtcrrnln\"\n",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "#define CONFIG_KEEP 1\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_SKIP") == null);
}
