const std = @import("std");
const bridge = @import("confdata_bridge.zig");

const TestCapture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator, capacity: usize) !TestCapture {
        return .{
            .allocator = allocator,
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
        };
    }

    fn deinit(self: *TestCapture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *TestCapture, bytes: []const u8) !void {
        try self.list.appendSlice(self.allocator, bytes);
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

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "standalone confdata bridge quoted suffix export surface trims trailing junk in auto.conf output" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ALPHA="zigux"suffix
        \\CONFIG_BETA=42
        \\CONFIG_MODULE=m
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();
    try bridge.emitAutoConfExports(&capture, summary);

    try std.testing.expectEqualStrings(
        "CONFIG_ALPHA=\"zigux\"\n" ++
            "CONFIG_BETA=42\n" ++
            "CONFIG_MODULE=m\n" ++
            "CONFIG_EXPLICIT_N=n\n",
        capture.list.items,
    );
    try expectAbsent(capture.list.items, "suffix");
    try expectAbsent(capture.list.items, "CONFIG_DEBUG");
}

test "standalone confdata bridge quoted suffix export surface keeps only the later trimmed value in autoconf header output" {
    var summary = try bridge.parseConfig(std.testing.allocator,
        \\CONFIG_ALPHA="stable"
        \\CONFIG_ALPHA="fresh"tail
        \\CONFIG_BETA=m
        \\CONFIG_COUNT=7
        \\CONFIG_EXPLICIT_N=n
        \\# CONFIG_DEBUG is not set
        \\
    );
    defer bridge.deinitSummary(std.testing.allocator, &summary);

    var capture = try TestCapture.init(std.testing.allocator, 256);
    defer capture.deinit();
    try bridge.emitAutoconfHeaderExports(&capture, summary);

    try expectContains(capture.list.items, "#define CONFIG_ALPHA \"fresh\"\n");
    try expectContains(capture.list.items, "#define CONFIG_BETA_MODULE 1\n");
    try expectContains(capture.list.items, "#define CONFIG_COUNT 7\n");
    try expectAbsent(capture.list.items, "\"stable\"");
    try expectAbsent(capture.list.items, "tail");
    try expectAbsent(capture.list.items, "CONFIG_EXPLICIT_N");
    try expectAbsent(capture.list.items, "CONFIG_DEBUG");
}
