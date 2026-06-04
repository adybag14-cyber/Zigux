const std = @import("std");
const confdata_bridge = @import("confdata_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    bytes: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .allocator = allocator,
            .bytes = try std.ArrayList(u8).initCapacity(allocator, 128),
        };
    }

    fn deinit(self: *Capture) void {
        self.bytes.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, bytes: []const u8) !void {
        try self.bytes.appendSlice(self.allocator, bytes);
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

const bom_export_input =
    "\xef\xbb\xbfCONFIG_BOOT=y\n" ++
    "\xef\xbb\xbfCONFIG_HIDDEN=m\n" ++
    "CONFIG_NAME=\"zigux\"\n" ++
    "# CONFIG_DROP is not set\n";

test "standalone confdata first-line BOM reaches auto.conf exports only once" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(std.testing.allocator, bom_export_input, .auto_conf, &capture);

    try std.testing.expectEqualStrings(
        "CONFIG_BOOT=y\n" ++
            "CONFIG_NAME=\"zigux\"\n",
        capture.bytes.items,
    );
}

test "standalone confdata first-line BOM reaches autoconf header exports only once" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try confdata_bridge.runConfdataBridgeWithMode(std.testing.allocator, bom_export_input, .autoconf_header, &capture);

    try std.testing.expectEqualStrings(
        "#define CONFIG_BOOT 1\n" ++
            "#define CONFIG_NAME \"zigux\"\n",
        capture.bytes.items,
    );
}
