const std = @import("std");
const cmdline = @import("cmdline");

fn expectOption(optionstr: []const u8, option: []const u8, expected: bool) !void {
    try std.testing.expectEqual(expected, cmdline.parseOptionStr(optionstr, option));
    try std.testing.expectEqual(expected, cmdline.parse_option_str(optionstr, option));
}

test "phase1 cmdline option terminator replay stops matching at the first embedded nul" {
    try expectOption("root=/dev/sda1,quiet\x00debug,nohlt", "root=/dev/sda1", true);
    try expectOption("root=/dev/sda1,quiet\x00debug,nohlt", "quiet", true);
    try expectOption("root=/dev/sda1,quiet\x00debug,nohlt", "debug", false);
    try expectOption("root=/dev/sda1,quiet\x00debug,nohlt", "nohlt", false);
}

test "phase1 cmdline option terminator replay counts only comma-terminated empty entries" {
    try expectOption(",quiet", "", true);
    try expectOption("debug,,quiet", "", true);
    try expectOption("debug,\x00quiet", "", false);
    try expectOption("debug,", "", false);
    try expectOption("quiet\x00,", "", false);
}

test "phase1 cmdline option terminator replay keeps exact bare boundaries around equals and prefixes" {
    try expectOption("debug,debug=1,debugger", "debug", true);
    try expectOption("debug=1,debugger", "debug", false);
    try expectOption("panic,panic_on_warn,panic=-1", "panic", true);
    try expectOption("panic_on_warn,panic=-1", "panic", false);
    try expectOption("rdinit=/init,rdinit,rdinit_extra", "rdinit", true);
}

test "phase1 cmdline option terminator replay keeps comma-walk alignment across repeated probes" {
    const optionstr = "audit,,quiet,rootwait\x00panic,nohlt";
    const probes = [_]struct {
        option: []const u8,
        expected: bool,
    }{
        .{ .option = "audit", .expected = true },
        .{ .option = "", .expected = true },
        .{ .option = "quiet", .expected = true },
        .{ .option = "rootwait", .expected = true },
        .{ .option = "panic", .expected = false },
        .{ .option = "nohlt", .expected = false },
    };

    for (probes) |probe| {
        try expectOption(optionstr, probe.option, probe.expected);
    }
}
