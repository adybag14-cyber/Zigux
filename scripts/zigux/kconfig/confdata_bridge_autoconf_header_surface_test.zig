const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 512),
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
};

test "confdata bridge autoconf header emits final public states" {
    var summary = try confdata_bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\CONFIG_COUNT=7
        \\CONFIG_NAME="zigux\"bridge\\"
        \\CONFIG_EMPTY=
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\CONFIG_DUP=m
        \\# CONFIG_DUP is not set
        \\CONFIG_DUP=y
        \\# CONFIG_FINAL is not set
        \\
    );
    defer confdata_bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.emitAutoconfHeaderExports(&capture, summary);

    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA 1\n" ++
            "#define CONFIG_BETA_MODULE 1\n" ++
            "#define CONFIG_COUNT 7\n" ++
            "#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n" ++
            "#define CONFIG_EMPTY \n" ++
            "#define CONFIG_DUP 1\n",
        capture.bytes.items,
    );
}
