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
};

test "standalone confdata auto.conf string exports escape C-visible bytes" {
    var summary = try confdata.parseConfig(
        std.testing.allocator,
        "CONFIG_PROMPT=\"alpha\\\"beta\\\\gamma\t\r\"\n" ++
            "CONFIG_RAW=42\n" ++
            "CONFIG_MODULE=m\n" ++
            "CONFIG_DISABLED=n\n" ++
            "# CONFIG_UNSET is not set\n",
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata.emitAutoConfExports(&capture, summary);

    try std.testing.expectEqualStrings(
        "CONFIG_PROMPT=\"alpha\\\"beta\\\\gamma\\t\\r\"\n" ++
            "CONFIG_RAW=42\n" ++
            "CONFIG_MODULE=m\n" ++
            "CONFIG_DISABLED=n\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_UNSET") == null);
}

test "standalone confdata auto.conf keeps duplicate final string escape state" {
    var summary = try confdata.parseConfig(
        std.testing.allocator,
        "CONFIG_PROMPT=\"old\"\n" ++
            "CONFIG_PROMPT=\"new\\\"value\\\\tail\"\n" ++
            "# CONFIG_PROMPT is not set\n" ++
            "CONFIG_PROMPT=\"final\\tvalue\"\n",
    );
    defer confdata.deinitSummary(std.testing.allocator, &summary);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata.emitAutoConfExports(&capture, summary);

    try std.testing.expectEqualStrings(
        "CONFIG_PROMPT=\"finaltvalue\"\n",
        capture.list.items,
    );
}
