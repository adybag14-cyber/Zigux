const std = @import("std");
const conf_bridge = @import("conf_bridge.zig");

const Capture = struct {
    allocator: std.mem.Allocator,
    list: std.ArrayList(u8),

    fn init(allocator: std.mem.Allocator) Capture {
        return .{
            .allocator = allocator,
            .list = .empty,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn writeAll(self: *Capture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *Capture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

fn render(mode: conf_bridge.Mode, allconfig: ?[]const u8) ![]const u8 {
    var capture = Capture.init(std.testing.allocator);
    defer capture.deinit();

    try conf_bridge.runConfBridge(&capture, .{
        .mode = mode,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86",
        .allconfig = allconfig,
    });

    return try std.testing.allocator.dupe(u8, capture.list.items);
}

test "standalone conf bridge sentinel modes emit fallback packets" {
    const cases = [_]struct {
        mode: conf_bridge.Mode,
        flag: []const u8,
        fallback: []const u8,
    }{
        .{ .mode = .allnoconfig, .flag = "--allnoconfig", .fallback = "[\"allno.config\",\"all.config\"]" },
        .{ .mode = .allyesconfig, .flag = "--allyesconfig", .fallback = "[\"allyes.config\",\"all.config\"]" },
        .{ .mode = .alldefconfig, .flag = "--alldefconfig", .fallback = "[\"alldef.config\",\"all.config\"]" },
    };

    for (cases) |case| {
        const output = try render(case.mode, null);
        defer std.testing.allocator.free(output);

        try std.testing.expect(std.mem.indexOf(u8, output, case.flag) != null);
        try std.testing.expect(std.mem.indexOf(u8, output, case.fallback) != null);
        try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
        try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_SEED\"") == null);
        try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_NOSILENTUPDATE\"") == null);
    }
}

test "standalone conf bridge sentinel modes keep explicit empty override distinct" {
    const output = try render(.allyesconfig, "");
    defer std.testing.allocator.free(output);

    try std.testing.expect(std.mem.indexOf(u8, output, "[\"allyes.config\",\"all.config\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}

test "standalone conf bridge sentinel modes omit fallbacks for named override" {
    const output = try render(.allnoconfig, "mini-all.config");
    defer std.testing.allocator.free(output);

    try std.testing.expect(std.mem.indexOf(u8, output, "\"allconfig_fallbacks\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\"KCONFIG_ALLCONFIG\":\"mini-all.config\"") != null);
}
