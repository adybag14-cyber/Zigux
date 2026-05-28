const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

test "conf bridge randconfig no-override surface keeps sentinel and tunables scoped" {
    var buffer: std.Io.Writer.Allocating = .init(std.testing.allocator);
    defer buffer.deinit();

    try conf_bridge.runConfBridge(&buffer.writer, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .seed = 42,
        .probability = "10:20",
    });

    const json = buffer.writer.buffered();
    try std.testing.expect(std.mem.indexOf(u8, json, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"argv\":[\"scripts/kconfig/conf\",\"--randconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"ARCH\":\"x86_64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_CONFIG\":\"rand/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_SEED\":\"0x2A\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_PROBABILITY\":\"10:20\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_AUTOCONFIG\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_AUTOHEADER\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, json, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}
