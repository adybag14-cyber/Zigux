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

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

test "standalone confdata bridge emits auto.conf export surface" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\CONFIG_NAME="zigux\"bridge\\"
        \\CONFIG_EMPTY=
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.emitAutoConfExports(&output, summary);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_BETA=m\n" ++
            "CONFIG_NAME=\"zigux\\\"bridge\\\\\"\n" ++
            "CONFIG_EMPTY=\n" ++
            "CONFIG_EXPLICIT_N=n\n",
        output.list.items,
    );
}

test "standalone confdata bridge emits autoconf header export surface" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ALPHA=y
        \\CONFIG_BETA=m
        \\CONFIG_NAME="zigux\"bridge\\"
        \\CONFIG_EMPTY=
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.emitAutoconfHeaderExports(&output, summary);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA 1\n" ++
            "#define CONFIG_BETA_MODULE 1\n" ++
            "#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n" ++
            "#define CONFIG_EMPTY \n",
        output.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "CONFIG_EXPLICIT_N") == null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "CONFIG_DEBUG") == null);
}
