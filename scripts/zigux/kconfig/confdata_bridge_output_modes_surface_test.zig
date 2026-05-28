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

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

fn sampleInput() []const u8 {
    return
    \\CONFIG_ALPHA=y
    \\CONFIG_MODULE=M
    \\CONFIG_NAME="zigux\"bridge\\"
    \\CONFIG_EMPTY=
    \\CONFIG_EXPLICIT_N=n
    \\# CONFIG_DEBUG is not set
    \\
    ;
}

test "standalone confdata bridge keeps json as the default output surface" {
    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.runConfdataBridge(std.testing.allocator, sampleInput(), &output);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"counts\":{\"set\":5,\"unset\":1}") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_MODULE\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_EXPLICIT_N\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
}

test "standalone confdata bridge emits auto.conf through the explicit mode surface" {
    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.runConfdataBridgeWithMode(std.testing.allocator, sampleInput(), .auto_conf, &output);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_MODULE=m\n" ++
            "CONFIG_NAME=\"zigux\\\"bridge\\\\\"\n" ++
            "CONFIG_EMPTY=\n" ++
            "CONFIG_EXPLICIT_N=n\n",
        output.list.items,
    );
}

test "standalone confdata bridge emits autoconf header through the explicit mode surface" {
    var output = try Capture.init(std.testing.allocator);
    defer output.deinit();

    try bridge.runConfdataBridgeWithMode(std.testing.allocator, sampleInput(), .autoconf_header, &output);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA 1\n" ++
            "#define CONFIG_MODULE_MODULE 1\n" ++
            "#define CONFIG_NAME \"zigux\\\"bridge\\\\\"\n" ++
            "#define CONFIG_EMPTY \n",
        output.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "CONFIG_EXPLICIT_N") == null);
    try std.testing.expect(std.mem.indexOf(u8, output.list.items, "CONFIG_DEBUG") == null);
}
