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
    \\CONFIG_ALPHA=Y
    \\CONFIG_BETA=M
    \\CONFIG_EXPLICIT_N=N
    \\# CONFIG_DEBUG is not set
    \\
    ;
}

test "confdata bridge canonicalizes uppercase tristates in json output" {
    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.runConfdataBridge(std.testing.allocator, sampleInput(), &capture);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_ALPHA\",\"kind\":\"tristate\",\"value\":\"y\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"m\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"name\":\"CONFIG_EXPLICIT_N\",\"kind\":\"tristate\",\"value\":\"n\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"Y\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"M\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"value\":\"N\"") == null);
}

test "confdata bridge canonicalizes uppercase tristates in auto.conf exports" {
    var summary = try bridge.parseConfig(std.testing.allocator, sampleInput());
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.emitAutoConfExports(&capture, summary);
    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=y\n" ++
            "CONFIG_BETA=m\n" ++
            "CONFIG_EXPLICIT_N=n\n",
        capture.list.items,
    );
}

test "confdata bridge canonicalizes uppercase tristates in autoconf header exports" {
    var summary = try bridge.parseConfig(std.testing.allocator, sampleInput());
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator);
    defer capture.deinit();

    try bridge.emitAutoconfHeaderExports(&capture, summary);
    try std.testing.expectEqualStrings(
        "#define CONFIG_ALPHA 1\n" ++
            "#define CONFIG_BETA_MODULE 1\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_EXPLICIT_N") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "CONFIG_DEBUG") == null);
}
