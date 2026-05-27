const std = @import("std");
const Io = std.Io;
const conf_bridge = @import("conf_bridge.zig");

const rewrite_cases = [_]struct {
    mode: conf_bridge.Mode,
    config: []const u8,
    expected_path: []const u8,
}{
    .{
        .mode = .yes2modconfig,
        .config = "rewrite/.config",
        .expected_path = "../../../zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json",
    },
    .{
        .mode = .mod2yesconfig,
        .config = "promote/.config",
        .expected_path = "../../../zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json",
    },
    .{
        .mode = .mod2noconfig,
        .config = "demote/.config",
        .expected_path = "../../../zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json",
    },
};

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
};

test "standalone conf bridge rewrite modes emit the expected public surface" {
    inline for (rewrite_cases) |case| {
        var capture = try TestCapture.init(std.testing.allocator);
        defer capture.deinit();

        try conf_bridge.runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = case.config,
            .arch = "x86",
        });

        const expected = try Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            case.expected_path,
            std.testing.allocator,
            .limited(std.math.maxInt(usize)),
        );
        defer std.testing.allocator.free(expected);

        try std.testing.expectEqualStrings(expected, capture.list.items);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"allconfig_fallbacks\"") == null);
    }
}
