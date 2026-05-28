const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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

    pub fn print(self: *TestCapture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }
};

fn sampleInput() []const u8 {
    return
    \\CONFIG_ALPHA=y
    \\CONFIG_ALPHA=n
    \\CONFIG_NAME="zigux"
    \\# CONFIG_DEBUG is not set
    \\
    ;
}

test "confdata bridge keeps explicit n visible on the json surface" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator, sampleInput(), &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"set\":2") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"unset\":1") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_NAME\",\"kind\":\"string\",\"value\":\"zigux\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"") != null);
}

test "confdata bridge keeps explicit n visible in auto.conf exports" {
    var summary = try bridge.parseConfig(std.testing.allocator, sampleInput());
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.emitAutoConfExports(&capture, summary);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=n\n" ++
            "CONFIG_NAME=\"zigux\"\n",
        capture.list.items,
    );
}

test "confdata bridge omits explicit n from autoconf header exports" {
    var summary = try bridge.parseConfig(std.testing.allocator, sampleInput());
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.emitAutoconfHeaderExports(&capture, summary);
    try std.testing.expectEqualStrings(
        "#define CONFIG_NAME \"zigux\"\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_ALPHA") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_DEBUG") == null);
}
