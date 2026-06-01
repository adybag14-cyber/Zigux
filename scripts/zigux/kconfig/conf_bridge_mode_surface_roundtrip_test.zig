const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const expected_modes = [_]struct {
    mode: conf_bridge.Mode,
    text: []const u8,
    flag: []const u8,
}{
    .{ .mode = .oldaskconfig, .text = "oldaskconfig", .flag = "--oldaskconfig" },
    .{ .mode = .syncconfig, .text = "syncconfig", .flag = "--syncconfig" },
    .{ .mode = .oldconfig, .text = "oldconfig", .flag = "--oldconfig" },
    .{ .mode = .allnoconfig, .text = "allnoconfig", .flag = "--allnoconfig" },
    .{ .mode = .allyesconfig, .text = "allyesconfig", .flag = "--allyesconfig" },
    .{ .mode = .allmodconfig, .text = "allmodconfig", .flag = "--allmodconfig" },
    .{ .mode = .alldefconfig, .text = "alldefconfig", .flag = "--alldefconfig" },
    .{ .mode = .randconfig, .text = "randconfig", .flag = "--randconfig" },
    .{ .mode = .defconfig, .text = "defconfig", .flag = "--defconfig" },
    .{ .mode = .savedefconfig, .text = "savedefconfig", .flag = "--savedefconfig" },
    .{ .mode = .listnewconfig, .text = "listnewconfig", .flag = "--listnewconfig" },
    .{ .mode = .helpnewconfig, .text = "helpnewconfig", .flag = "--helpnewconfig" },
    .{ .mode = .olddefconfig, .text = "olddefconfig", .flag = "--olddefconfig" },
    .{ .mode = .yes2modconfig, .text = "yes2modconfig", .flag = "--yes2modconfig" },
    .{ .mode = .mod2yesconfig, .text = "mod2yesconfig", .flag = "--mod2yesconfig" },
    .{ .mode = .mod2noconfig, .text = "mod2noconfig", .flag = "--mod2noconfig" },
};

test "conf bridge standalone mode surface keeps canonical text and flags" {
    const field_names = comptime std.meta.fieldNames(conf_bridge.Mode);
    try std.testing.expectEqual(expected_modes.len, field_names.len);

    inline for (expected_modes, 0..) |entry, index| {
        try std.testing.expectEqualStrings(entry.text, field_names[index]);
        try std.testing.expectEqual(entry.mode, conf_bridge.Mode.parse(entry.text).?);
        try std.testing.expectEqualStrings(entry.text, entry.mode.text());
        try std.testing.expectEqualStrings(entry.flag, entry.mode.flag());
    }
}

test "conf bridge standalone mode surface rejects unsupported names and keeps flags unique" {
    try std.testing.expect(conf_bridge.Mode.parse("oldaskconfigx") == null);
    try std.testing.expect(conf_bridge.Mode.parse("--oldaskconfig") == null);
    try std.testing.expect(conf_bridge.Mode.parse("mod2noConfig") == null);
    try std.testing.expect(conf_bridge.Mode.parse("") == null);

    var seen_flags = std.StringHashMap(void).init(std.testing.allocator);
    defer seen_flags.deinit();

    inline for (expected_modes) |entry| {
        try std.testing.expect(!seen_flags.contains(entry.flag));
        try seen_flags.put(entry.flag, {});
    }
}
