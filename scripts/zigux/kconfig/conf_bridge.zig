const std = @import("std");
const Io = std.Io;

pub const Mode = enum {
    oldaskconfig,
    syncconfig,
    oldconfig,
    allnoconfig,
    allyesconfig,
    allmodconfig,
    alldefconfig,
    randconfig,
    defconfig,
    savedefconfig,
    listnewconfig,
    helpnewconfig,
    olddefconfig,
    yes2modconfig,
    mod2yesconfig,
    mod2noconfig,

    pub fn parse(input_text: []const u8) ?Mode {
        inline for (std.meta.fields(Mode)) |field| {
            if (std.mem.eql(u8, input_text, field.name)) {
                return @field(Mode, field.name);
            }
        }
        return null;
    }

    pub fn flag(self: Mode) []const u8 {
        return switch (self) {
            .oldaskconfig => "--oldaskconfig",
            .syncconfig => "--syncconfig",
            .oldconfig => "--oldconfig",
            .allnoconfig => "--allnoconfig",
            .allyesconfig => "--allyesconfig",
            .allmodconfig => "--allmodconfig",
            .alldefconfig => "--alldefconfig",
            .randconfig => "--randconfig",
            .defconfig => "--defconfig",
            .savedefconfig => "--savedefconfig",
            .listnewconfig => "--listnewconfig",
            .helpnewconfig => "--helpnewconfig",
            .olddefconfig => "--olddefconfig",
            .yes2modconfig => "--yes2modconfig",
            .mod2yesconfig => "--mod2yesconfig",
            .mod2noconfig => "--mod2noconfig",
        };
    }

    pub fn text(self: Mode) []const u8 {
        return switch (self) {
            .oldaskconfig => "oldaskconfig",
            .syncconfig => "syncconfig",
            .oldconfig => "oldconfig",
            .allnoconfig => "allnoconfig",
            .allyesconfig => "allyesconfig",
            .allmodconfig => "allmodconfig",
            .alldefconfig => "alldefconfig",
            .randconfig => "randconfig",
            .defconfig => "defconfig",
            .savedefconfig => "savedefconfig",
            .listnewconfig => "listnewconfig",
            .helpnewconfig => "helpnewconfig",
            .olddefconfig => "olddefconfig",
            .yes2modconfig => "yes2modconfig",
            .mod2yesconfig => "mod2yesconfig",
            .mod2noconfig => "mod2noconfig",
        };
    }
};

pub const Request = struct {
    mode: Mode,
    kconfig: []const u8,
    config: []const u8,
    arch: []const u8,
    mode_arg: ?[]const u8 = null,
    seed: ?[]const u8 = null,
    probability: ?[]const u8 = null,
};

const RandconfigTunables = struct {
    seed: ?[]const u8 = null,
    probability: ?[]const u8 = null,
};

const ParseRandconfigTunablesError = error{
    DuplicateSeed,
    DuplicateProbability,
    UnexpectedArgument,
};

fn modeRequiresArgument(mode: Mode) bool {
    return switch (mode) {
        .defconfig, .savedefconfig => true,
        else => false,
    };
}

fn missingModeArgumentMessage(mode: Mode) []const u8 {
    return switch (mode) {
        .defconfig => "Error: defconfig mode requires <defconfig>\n",
        .savedefconfig => "Error: savedefconfig mode requires <path>\n",
        else => unreachable,
    };
}

fn writeHexLower(writer: anytype, value: u8) !void {
    const digits = "0123456789abcdef";
    try writer.writeByte(digits[value >> 4]);
    try writer.writeByte(digits[value & 0x0f]);
}

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
        0...0x07, 0x0b, 0x0e...0x1f => {
            try writer.writeAll("\\u00");
            try writeHexLower(writer, c);
        },
        else => try writer.writeByte(c),
    };
}

fn parseRandconfigTunables(args: []const []const u8) ParseRandconfigTunablesError!RandconfigTunables {
    var tunables = RandconfigTunables{};
    var saw_seed = false;
    var saw_probability = false;

    for (args) |arg| {
        if (std.mem.startsWith(u8, arg, "seed=")) {
            if (saw_seed) return error.DuplicateSeed;
            saw_seed = true;
            const value = arg["seed=".len..];
            tunables.seed = if (value.len == 0) null else value;
            continue;
        }
        if (std.mem.startsWith(u8, arg, "probability=")) {
            if (saw_probability) return error.DuplicateProbability;
            saw_probability = true;
            const value = arg["probability=".len..];
            tunables.probability = if (value.len == 0) null else value;
            continue;
        }
        return error.UnexpectedArgument;
    }

    return tunables;
}

pub fn runConfBridge(writer: anytype, request: Request) !void {
    try writer.writeAll("{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"");
    try writer.writeAll(request.mode.text());
    try writer.writeAll("\",\"argv\":[\"scripts/kconfig/conf\",\"");
    try writer.writeAll(request.mode.flag());
    try writer.writeAll("\"");
    if (request.mode_arg) |mode_arg| {
        try writer.writeAll(",\"");
        try writeJsonEscaped(writer, mode_arg);
        try writer.writeAll("\"");
    }
    try writer.writeAll(",\"");
    try writeJsonEscaped(writer, request.kconfig);
    try writer.writeAll("\"],\"env\":{\"ARCH\":\"");
    try writeJsonEscaped(writer, request.arch);
    try writer.writeAll("\",\"KCONFIG_CONFIG\":\"");
    try writeJsonEscaped(writer, request.config);
    try writer.writeAll("\"");
    if (request.mode == .syncconfig) {
        try writer.writeAll(",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
    }
    if (request.mode == .randconfig) {
        if (request.seed) |seed| {
            try writer.writeAll(",\"KCONFIG_SEED\":\"");
            try writeJsonEscaped(writer, seed);
            try writer.writeAll("\"");
        }
        if (request.probability) |probability| {
            try writer.writeAll(",\"KCONFIG_PROBABILITY\":\"");
            try writeJsonEscaped(writer, probability);
            try writer.writeAll("\"");
        }
    }
    try writer.writeAll("}}\n");
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    if (args.len < 5 or args.len > 8) {
        var stderr_buffer: [200]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Usage: conf_bridge <mode> <Kconfig> <.config> <arch> [mode-arg] [seed=<value>] [probability=<value>]\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    }

    const mode = Mode.parse(args[1]) orelse {
        var stderr_buffer: [160]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Error: unsupported kconfig mode\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    };

    var next_index: usize = 5;
    const mode_arg = blk: {
        if (!modeRequiresArgument(mode)) break :blk null;
        if (args.len == next_index) {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll(missingModeArgumentMessage(mode));
            try stderr_writer.interface.flush();
            std.process.exit(1);
        }
        const value = args[next_index];
        next_index += 1;
        break :blk value;
    };

    var tunables = RandconfigTunables{};
    if (mode == .randconfig) {
        tunables = parseRandconfigTunables(args[next_index..]) catch |err| {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            const message = switch (err) {
                error.DuplicateSeed => "Error: duplicate randconfig seed option\n",
                error.DuplicateProbability => "Error: duplicate randconfig probability option\n",
                error.UnexpectedArgument => "Error: randconfig only accepts seed=<value> or probability=<value>\n",
            };
            try stderr_writer.interface.writeAll(message);
            try stderr_writer.interface.flush();
            std.process.exit(1);
        };
    } else if (args.len != next_index) {
        var stderr_buffer: [160]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Error: unexpected mode argument\n");
        try stderr_writer.interface.flush();
        std.process.exit(1);
    }

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfBridge(&stdout_writer.interface, .{
        .mode = mode,
        .kconfig = args[2],
        .config = args[3],
        .arch = args[4],
        .mode_arg = mode_arg,
        .seed = tunables.seed,
        .probability = tunables.probability,
    });
    try stdout_writer.interface.flush();
}

test "conf bridge mode surface stays aligned with conf.c long options" {
    const expected = [_]struct { mode: Mode, text: []const u8, flag: []const u8 }{
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

    const fields = std.meta.fields(Mode);
    try std.testing.expectEqual(expected.len, fields.len);

    inline for (expected, 0..) |entry, index| {
        try std.testing.expectEqualStrings(entry.text, fields[index].name);
        try std.testing.expectEqual(entry.mode, Mode.parse(entry.text).?);
        try std.testing.expectEqualStrings(entry.text, entry.mode.text());
        try std.testing.expectEqualStrings(entry.flag, entry.mode.flag());
    }
}

test "conf bridge emits olddefconfig argv and env" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 128), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .olddefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"olddefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--olddefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\".config\"") != null);
}

test "conf bridge emits syncconfig auto files" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 160), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"riscv64\"") != null);
}

test "conf bridge emits alldefconfig argv and env" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 128), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--alldefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"build/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"arm64\"") != null);
}

test "conf bridge emits allmodconfig argv and env" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 128), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"mod/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"arm\"") != null);
}

test "conf bridge emits randconfig tunables when present" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 192), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .seed = "0xC0FFEE",
        .probability = "15:25",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\":\"0xC0FFEE\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\":\"15:25\"") != null);
}

test "conf bridge emits yes2modconfig argv and env" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 144), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .yes2modconfig,
        .kconfig = "Kconfig",
        .config = "rewrite/.config",
        .arch = "x86",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"yes2modconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--yes2modconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"rewrite/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"x86\"") != null);
}

test "conf bridge emits defconfig mode argument before kconfig" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 192), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/arm64/configs/defconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"defconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/arm64/configs/defconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
}

test "conf bridge emits savedefconfig mode argument before kconfig" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 192), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .savedefconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .mode_arg = "defconfig.out",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"savedefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"defconfig.out\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\".config\"") != null);
}

test "conf bridge escapes low control bytes in JSON strings" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 32), .allocator = allocator };
        }

        fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        fn writeAll(self: *@This(), bytes: []const u8) !void {
            try self.list.appendSlice(self.allocator, bytes);
        }

        fn writeByte(self: *@This(), byte: u8) !void {
            try self.list.append(self.allocator, byte);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try writeJsonEscaped(&capture, "\x01\x08\x0c");
    try std.testing.expectEqualStrings("\\u0001\\b\\f", capture.list.items);
}

test "randconfig tunables parser accepts seed and probability" {
    const tunables = try parseRandconfigTunables(&.{ "seed=0xC0FFEE", "probability=15:25" });
    try std.testing.expectEqualStrings("0xC0FFEE", tunables.seed.?);
    try std.testing.expectEqualStrings("15:25", tunables.probability.?);
}

test "randconfig tunables parser treats empty values as absent" {
    const tunables = try parseRandconfigTunables(&.{ "seed=", "probability=" });
    try std.testing.expect(tunables.seed == null);
    try std.testing.expect(tunables.probability == null);
}

test "randconfig tunables parser rejects duplicate seed" {
    try std.testing.expectError(error.DuplicateSeed, parseRandconfigTunables(&.{ "seed=1", "seed=2" }));
}

test "randconfig tunables parser rejects unexpected argument" {
    try std.testing.expectError(error.UnexpectedArgument, parseRandconfigTunables(&.{"bogus"}));
}
