const std = @import("std");
const bridge = @import("conf_bridge.zig");

test "conf bridge mode parse rejects unsupported and near-miss names" {
    const invalid = [_][]const u8{
        "",
        "oldconfig ",
        " oldconfig",
        "oldconfig\n",
        "--oldconfig",
        "Oldconfig",
        "silentoldconfig",
        "allnoconfig=",
        "randconfig=seed",
        "mod2yesconfig/",
        "helpnewconfig?",
        "sync config",
        "savedefconfig\tsuffix",
        "listnewconfig-extra",
    };

    for (invalid) |name| {
        try std.testing.expect(bridge.Mode.parse(name) == null);
    }
}

test "conf bridge mode parse stays exact for canonical spellings" {
    const expected = [_]struct {
        mode: bridge.Mode,
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

    inline for (expected) |entry| {
        try std.testing.expectEqual(entry.mode, bridge.Mode.parse(entry.text).?);
        try std.testing.expectEqualStrings(entry.text, entry.mode.text());
        try std.testing.expectEqualStrings(entry.flag, entry.mode.flag());
    }
}
