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
    silent: bool = false,
    mode_arg: ?[]const u8 = null,
    allconfig: ?[]const u8 = null,
    seed: ?[]const u8 = null,
    probability: ?[]const u8 = null,
    nosilentupdate: ?[]const u8 = null,
};

const BridgeOptions = struct {
    silent: bool = false,
    allconfig: ?[]const u8 = null,
    seed: ?[]const u8 = null,
    probability: ?[]const u8 = null,
    nosilentupdate: ?[]const u8 = null,
};

const ParseBridgeOptionsError = error{
    DuplicateSilent,
    DuplicateAllConfig,
    DuplicateSeed,
    DuplicateProbability,
    DuplicateNoSilentUpdate,
    UnexpectedArgument,
};

const ModeArgumentError = error{
    MissingArgument,
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

fn modeUsesAllConfigSentinel(mode: Mode) bool {
    return switch (mode) {
        .allnoconfig, .allyesconfig, .allmodconfig, .alldefconfig => true,
        else => false,
    };
}

fn modeAcceptsAllConfigOverride(mode: Mode) bool {
    return switch (mode) {
        .allnoconfig, .allyesconfig, .allmodconfig, .alldefconfig, .randconfig => true,
        else => false,
    };
}

const bridge_option_prefixes = [_][]const u8{
    "allconfig=",
    "seed=",
    "probability=",
    "nosilentupdate=",
};

fn looksLikeBridgeOption(text: []const u8) bool {
    if (std.mem.eql(u8, text, "silent")) {
        return true;
    }
    for (bridge_option_prefixes) |prefix| {
        if (std.mem.startsWith(u8, text, prefix)) {
            return true;
        }
    }
    return false;
}

fn validateModeArgument(mode: Mode, value: []const u8) ModeArgumentError![]const u8 {
    if (!modeRequiresArgument(mode)) return value;
    if (value.len == 0 or looksLikeBridgeOption(value)) {
        return error.MissingArgument;
    }
    return value;
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

fn parseBridgeOptions(mode: Mode, args: []const []const u8) ParseBridgeOptionsError!BridgeOptions {
    var options = BridgeOptions{};
    var saw_silent = false;
    var saw_allconfig = false;
    var saw_seed = false;
    var saw_probability = false;
    var saw_nosilentupdate = false;

    for (args) |arg| {
        if (std.mem.eql(u8, arg, "silent")) {
            if (saw_silent) return error.DuplicateSilent;
            saw_silent = true;
            options.silent = true;
            continue;
        }
        if (std.mem.startsWith(u8, arg, "allconfig=")) {
            if (!modeAcceptsAllConfigOverride(mode)) return error.UnexpectedArgument;
            if (saw_allconfig) return error.DuplicateAllConfig;
            saw_allconfig = true;
            options.allconfig = arg["allconfig=".len..];
            continue;
        }
        if (std.mem.startsWith(u8, arg, "seed=")) {
            if (mode != .randconfig) return error.UnexpectedArgument;
            if (saw_seed) return error.DuplicateSeed;
            saw_seed = true;
            const value = arg["seed=".len..];
            options.seed = if (value.len == 0) null else value;
            continue;
        }
        if (std.mem.startsWith(u8, arg, "probability=")) {
            if (mode != .randconfig) return error.UnexpectedArgument;
            if (saw_probability) return error.DuplicateProbability;
            saw_probability = true;
            const value = arg["probability=".len..];
            options.probability = if (value.len == 0) null else value;
            continue;
        }
        if (std.mem.startsWith(u8, arg, "nosilentupdate=")) {
            if (mode != .syncconfig) return error.UnexpectedArgument;
            if (saw_nosilentupdate) return error.DuplicateNoSilentUpdate;
            saw_nosilentupdate = true;
            const value = arg["nosilentupdate=".len..];
            options.nosilentupdate = if (value.len == 0) null else value;
            continue;
        }
        return error.UnexpectedArgument;
    }

    return options;
}

pub fn runConfBridge(writer: anytype, request: Request) !void {
    try writer.writeAll("{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"");
    try writer.writeAll(request.mode.text());
    try writer.writeAll("\",\"argv\":[\"scripts/kconfig/conf\"");
    if (request.silent) {
        try writer.writeAll(",\"--silent\"");
    }
    try writer.writeAll(",\"");
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
    if (request.allconfig) |allconfig| {
        try writer.writeAll(",\"KCONFIG_ALLCONFIG\":\"");
        try writeJsonEscaped(writer, allconfig);
        try writer.writeAll("\"");
    } else if (modeUsesAllConfigSentinel(request.mode)) {
        try writer.writeAll(",\"KCONFIG_ALLCONFIG\":\"1\"");
    }
    if (request.mode == .syncconfig) {
        try writer.writeAll(",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
        if (request.nosilentupdate) |nosilentupdate| {
            if (nosilentupdate.len != 0) {
                try writer.writeAll(",\"KCONFIG_NOSILENTUPDATE\":\"");
                try writeJsonEscaped(writer, nosilentupdate);
                try writer.writeAll("\"");
            }
        }
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

    if (args.len < 5 or args.len > 9) {
        var stderr_buffer: [220]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Usage: conf_bridge <mode> <Kconfig> <.config> <arch> [mode-arg] [silent] [allconfig=<value>] [seed=<value>] [probability=<value>] [nosilentupdate=<value>]\n");
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
        const value = validateModeArgument(mode, args[next_index]) catch {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll(missingModeArgumentMessage(mode));
            try stderr_writer.interface.flush();
            std.process.exit(1);
        };
        next_index += 1;
        break :blk value;
    };

    const options = parseBridgeOptions(mode, args[next_index..]) catch |err| {
        var stderr_buffer: [192]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        const message = switch (err) {
            error.DuplicateSilent => "Error: duplicate silent option\n",
            error.DuplicateAllConfig => "Error: duplicate allconfig override option\n",
            error.DuplicateSeed => "Error: duplicate randconfig seed option\n",
            error.DuplicateProbability => "Error: duplicate randconfig probability option\n",
            error.DuplicateNoSilentUpdate => "Error: duplicate syncconfig nosilentupdate option\n",
            error.UnexpectedArgument => "Error: unexpected bridge option for mode\n",
        };
        try stderr_writer.interface.writeAll(message);
        try stderr_writer.interface.flush();
        std.process.exit(1);
    };

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfBridge(&stdout_writer.interface, .{
        .mode = mode,
        .kconfig = args[2],
        .config = args[3],
        .arch = args[4],
        .silent = options.silent,
        .mode_arg = mode_arg,
        .allconfig = options.allconfig,
        .seed = options.seed,
        .probability = options.probability,
        .nosilentupdate = options.nosilentupdate,
    });
    try stdout_writer.interface.flush();
}

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

    pub fn writeAll(self: *TestCapture, text: []const u8) !void {
        try self.list.appendSlice(self.allocator, text);
    }

    pub fn writeByte(self: *TestCapture, byte: u8) !void {
        try self.list.append(self.allocator, byte);
    }
};

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
    var capture = try TestCapture.init(std.testing.allocator, 128);
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
    var capture = try TestCapture.init(std.testing.allocator, 192);
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

test "conf bridge emits syncconfig nosilentupdate when present" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "1",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"1\"") != null);
}

test "conf bridge omits empty syncconfig nosilentupdate" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .nosilentupdate = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\"") == null);
}

test "conf bridge escapes quoted and backslashed syncconfig nosilentupdate in json output" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .silent = true,
        .nosilentupdate = "keep\\\"quoted\\\\path",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"syncconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"riscv64\",\"KCONFIG_CONFIG\":\"out/.config\",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\",\"KCONFIG_NOSILENTUPDATE\":\"keep\\\\\\\"quoted\\\\path\"}}\n",
        capture.list.items,
    );
}

test "conf bridge emits silent flag before mode flag" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .listnewconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "x86_64",
        .silent = true,
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--listnewconfig\",\"Kconfig\"]") != null);
}

test "conf bridge emits alldefconfig argv and env" {
    var capture = try TestCapture.init(std.testing.allocator, 160);
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
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}

test "conf bridge explicit allconfig override wins over alldefconfig sentinel" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .allconfig = "mini.config",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"mini.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}

test "conf bridge emits explicit empty allconfig override for alldefconfig" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .alldefconfig,
        .kconfig = "Kconfig",
        .config = "build/.config",
        .arch = "arm64",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") == null);
}

test "conf bridge emits explicit empty allconfig override for allmodconfig" {
    var capture = try TestCapture.init(std.testing.allocator, 160);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
}

test "conf bridge emits allyesconfig sentinel without explicit override" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .allyesconfig,
        .kconfig = "Kconfig",
        .config = "yes/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allyesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}

test "conf bridge emits allnoconfig sentinel without explicit override" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "no/.config",
        .arch = "arm64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allnoconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}

test "conf bridge emits allmodconfig sentinel without explicit override" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .allmodconfig,
        .kconfig = "Kconfig",
        .config = "mod/.config",
        .arch = "arm",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"allmodconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"1\"") != null);
}

test "conf bridge emits randconfig tunables when present" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
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

test "conf bridge emits explicit randconfig allconfig override when present" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .allconfig = "allrandom.config",
        .seed = "0xC0FFEE",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"allrandom.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\":\"0xC0FFEE\"") != null);
}

test "conf bridge emits explicit empty randconfig allconfig override" {
    var capture = try TestCapture.init(std.testing.allocator, 224);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .allconfig = "",
        .seed = "0xC0FFEE",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\":\"0xC0FFEE\"") != null);
}

test "conf bridge omits randconfig allconfig sentinel without explicit override" {
    var capture = try TestCapture.init(std.testing.allocator, 192);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\"") == null);
}

test "conf bridge emits yes2modconfig argv and env" {
    var capture = try TestCapture.init(std.testing.allocator, 144);
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
    var capture = try TestCapture.init(std.testing.allocator, 192);
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
    var capture = try TestCapture.init(std.testing.allocator, 192);
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

test "conf bridge escapes quoted and backslashed defconfig request fields in json output" {
    var capture = try TestCapture.init(std.testing.allocator, 320);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig \\\"quoted\\\"\\path",
        .config = "out/\\\"quoted\\\\.config",
        .arch = "arm64\\\\\\\"lab",
        .mode_arg = "arch/arm64/configs/zigux\\\"debug\\defconfig",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"defconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--defconfig\",\"arch/arm64/configs/zigux\\\\\\\"debug\\\\defconfig\",\"Kconfig \\\\\\\"quoted\\\\\\\"\\path\"],\"env\":{\"ARCH\":\"arm64\\\\\\\\\\\\\\\"lab\",\"KCONFIG_CONFIG\":\"out/\\\\\\\"quoted\\\\.config\"}}\n",
        capture.list.items,
    );
}

test "conf bridge escapes quoted and backslashed randconfig env overrides in json output" {
    var capture = try TestCapture.init(std.testing.allocator, 384);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86_64",
        .silent = true,
        .allconfig = "all\\\"random\\.config",
        .seed = "0xC0\\\"FFEE\\42",
        .probability = "15:25\\\"mix\\cap",
    });

    try std.testing.expectEqualStrings(
        "{\"tool\":\"scripts/kconfig/conf\",\"mode\":\"randconfig\",\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"],\"env\":{\"ARCH\":\"x86_64\",\"KCONFIG_CONFIG\":\"rand/.config\",\"KCONFIG_ALLCONFIG\":\"all\\\\\\\"random\\\\.config\",\"KCONFIG_SEED\":\"0xC0\\\\\\\"FFEE\\\\42\",\"KCONFIG_PROBABILITY\":\"15:25\\\\\\\"mix\\\\cap\"}}\n",
        capture.list.items,
    );
}

test "conf bridge escapes low control bytes in JSON strings" {
    var capture = try TestCapture.init(std.testing.allocator, 32);
    defer capture.deinit();

    try writeJsonEscaped(&capture, "\x01\x08\x0c");
    try std.testing.expectEqualStrings("\\u0001\\b\\f", capture.list.items);
}

test "mode argument validation rejects bridge option shaped defconfig payload" {
    try std.testing.expectError(error.MissingArgument, validateModeArgument(.defconfig, "silent"));
    try std.testing.expectError(error.MissingArgument, validateModeArgument(.defconfig, "allconfig=mini.config"));
    try std.testing.expectError(error.MissingArgument, validateModeArgument(.savedefconfig, "nosilentupdate=1"));
}

test "mode argument validation accepts defconfig path that only starts with silent" {
    try std.testing.expectEqualStrings("silent-debug_defconfig", try validateModeArgument(.defconfig, "silent-debug_defconfig"));
    try std.testing.expectEqualStrings("silent=debug_defconfig", try validateModeArgument(.savedefconfig, "silent=debug_defconfig"));
}

test "mode argument validation still accepts ordinary path text with equals" {
    try std.testing.expectEqualStrings("arch/x86/configs/debug=1_defconfig", try validateModeArgument(.defconfig, "arch/x86/configs/debug=1_defconfig"));
}

test "bridge options parser accepts explicit allconfig override for allmodconfig" {
    const options = try parseBridgeOptions(.allmodconfig, &.{"allconfig="});
    try std.testing.expect(options.silent == false);
    try std.testing.expect(options.allconfig != null);
    try std.testing.expectEqual(@as(usize, 0), options.allconfig.?.len);
    try std.testing.expect(options.seed == null);
    try std.testing.expect(options.probability == null);
    try std.testing.expect(options.nosilentupdate == null);
}

test "bridge options parser accepts explicit empty allconfig override for alldefconfig" {
    const options = try parseBridgeOptions(.alldefconfig, &.{"allconfig="});
    try std.testing.expect(options.silent == false);
    try std.testing.expect(options.allconfig != null);
    try std.testing.expectEqual(@as(usize, 0), options.allconfig.?.len);
    try std.testing.expect(options.seed == null);
    try std.testing.expect(options.probability == null);
    try std.testing.expect(options.nosilentupdate == null);
}

test "bridge options parser accepts explicit empty allconfig override for randconfig" {
    const options = try parseBridgeOptions(.randconfig, &.{ "allconfig=", "seed=0xC0FFEE" });
    try std.testing.expect(options.silent == false);
    try std.testing.expect(options.allconfig != null);
    try std.testing.expectEqual(@as(usize, 0), options.allconfig.?.len);
    try std.testing.expectEqualStrings("0xC0FFEE", options.seed.?);
    try std.testing.expect(options.probability == null);
    try std.testing.expect(options.nosilentupdate == null);
}

test "bridge options parser accepts syncconfig nosilentupdate" {
    const options = try parseBridgeOptions(.syncconfig, &.{"nosilentupdate=1"});
    try std.testing.expect(options.silent == false);
    try std.testing.expect(options.nosilentupdate != null);
    try std.testing.expectEqualStrings("1", options.nosilentupdate.?);
}

test "bridge options parser keeps empty syncconfig nosilentupdate unset" {
    const options = try parseBridgeOptions(.syncconfig, &.{"nosilentupdate="});
    try std.testing.expect(options.silent == false);
    try std.testing.expect(options.nosilentupdate == null);
}

test "bridge options parser accepts silent alongside syncconfig nosilentupdate" {
    const options = try parseBridgeOptions(.syncconfig, &.{ "silent", "nosilentupdate=keep\\\"quoted\\path" });
    try std.testing.expect(options.silent);
    try std.testing.expectEqualStrings("keep\\\"quoted\\path", options.nosilentupdate.?);
    try std.testing.expect(options.allconfig == null);
    try std.testing.expect(options.seed == null);
    try std.testing.expect(options.probability == null);
}

test "bridge options parser accepts generic silent flag" {
    const options = try parseBridgeOptions(.helpnewconfig, &.{"silent"});
    try std.testing.expect(options.silent);
    try std.testing.expect(options.allconfig == null);
}

test "bridge options parser accepts silent alongside randconfig options" {
    const options = try parseBridgeOptions(.randconfig, &.{
        "silent",
        "allconfig=allrandom.config",
        "seed=0xC0FFEE",
        "probability=10:20",
    });
    try std.testing.expect(options.silent);
    try std.testing.expectEqualStrings("allrandom.config", options.allconfig.?);
    try std.testing.expectEqualStrings("0xC0FFEE", options.seed.?);
    try std.testing.expectEqualStrings("10:20", options.probability.?);
}

test "bridge options parser rejects duplicate silent flag" {
    try std.testing.expectError(error.DuplicateSilent, parseBridgeOptions(.oldconfig, &.{
        "silent",
        "silent",
    }));
}

test "bridge options parser rejects duplicate randconfig probability" {
    try std.testing.expectError(error.DuplicateProbability, parseBridgeOptions(.randconfig, &.{
        "probability=10",
        "probability=20",
    }));
}

test "bridge options parser rejects unexpected options for mode" {
    try std.testing.expectError(error.UnexpectedArgument, parseBridgeOptions(.oldconfig, &.{"allconfig=mini.config"}));
    try std.testing.expectError(error.UnexpectedArgument, parseBridgeOptions(.oldconfig, &.{"nosilentupdate=1"}));
    try std.testing.expectError(error.UnexpectedArgument, parseBridgeOptions(.syncconfig, &.{"seed=0xC0FFEE"}));
}

test "bridge options parser keeps empty randconfig tunables unset" {
    const options = try parseBridgeOptions(.randconfig, &.{
        "seed=",
        "probability=",
    });
    try std.testing.expect(options.seed == null);
    try std.testing.expect(options.probability == null);
}

test "bridge options parser rejects duplicate mode specific options" {
    try std.testing.expectError(error.DuplicateAllConfig, parseBridgeOptions(.randconfig, &.{
        "allconfig=one",
        "allconfig=two",
    }));
    try std.testing.expectError(error.DuplicateSeed, parseBridgeOptions(.randconfig, &.{
        "seed=1",
        "seed=2",
    }));
    try std.testing.expectError(error.DuplicateProbability, parseBridgeOptions(.randconfig, &.{
        "probability=1:2",
        "probability=3:4",
    }));
    try std.testing.expectError(error.DuplicateNoSilentUpdate, parseBridgeOptions(.syncconfig, &.{
        "nosilentupdate=1",
        "nosilentupdate=0",
    }));
}
