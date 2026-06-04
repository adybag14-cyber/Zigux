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

test "standalone confdata auto.conf surface exports final set states" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_ALPHA=m
        \\# CONFIG_DEBUG is not set
        \\CONFIG_EXPLICIT_N=n
        \\CONFIG_COUNT=42
        \\CONFIG_EMPTY=
        \\CONFIG_STRING="zigux\"bridge\\path"
        \\CONFIG_ESCAPED="line\n\tend"
        \\
    , .auto_conf, &capture);

    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=m\n" ++
            "CONFIG_EXPLICIT_N=n\n" ++
            "CONFIG_COUNT=42\n" ++
            "CONFIG_EMPTY=\n" ++
            "CONFIG_STRING=\"zigux\\\"bridge\\\\path\"\n" ++
            "CONFIG_ESCAPED=\"linentend\"\n",
        capture.bytes.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.bytes.items, "CONFIG_DEBUG") == null);
}
