const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

test "syncconfig emits explicit nosilentupdate with silent ordering and no unrelated env" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 256),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/linux.config",
        .arch = "arm64",
        .silent = true,
        .nosilentupdate = "include/config/stale auto.conf",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_NOSILENTUPDATE\":\"include/config/stale auto.conf\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_ALLCONFIG\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_SEED\"",
    ) == null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_PROBABILITY\"",
    ) == null);
}

test "syncconfig escapes nosilentupdate json payload without changing auto files" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 256),
                .allocator = allocator,
            };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        pub fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/linux.config",
        .arch = "riscv64",
        .nosilentupdate = "quoted\\path\"watch",
    });

    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_NOSILENTUPDATE\":\"quoted\\\\path\\\"watch\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        capture.list.items,
        "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"",
    ) != null);
}
