const std = @import("std");
const Io = std.Io;

pub const Mode = enum {
    oldaskconfig,
    oldconfig,
    syncconfig,
    defconfig,
    savedefconfig,
    allnoconfig,
    allyesconfig,
    allmodconfig,
    alldefconfig,
    randconfig,
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
            .oldconfig => "--oldconfig",
            .syncconfig => "--syncconfig",
            .defconfig => "--defconfig",
            .savedefconfig => "--savedefconfig",
            .allnoconfig => "--allnoconfig",
            .allyesconfig => "--allyesconfig",
            .allmodconfig => "--allmodconfig",
            .alldefconfig => "--alldefconfig",
            .randconfig => "--randconfig",
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
            .oldconfig => "oldconfig",
            .syncconfig => "syncconfig",
            .defconfig => "defconfig",
            .savedefconfig => "savedefconfig",
            .allnoconfig => "allnoconfig",
            .allyesconfig => "allyesconfig",
            .allmodconfig => "allmodconfig",
            .alldefconfig => "alldefconfig",
            .randconfig => "randconfig",
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
    allconfig: ?[]const u8 = null,
    seed: ?[]const u8 = null,
    probability: ?[]const u8 = null,
    autoconfig: ?[]const u8 = null,
    autoheader: ?[]const u8 = null,
    nosilentupdate: ?[]const u8 = null,
};

const ValidateExtraArgError = error{
    MissingModeArg,
    UnexpectedModeArg,
    EmptyModeArg,
    EmptyAllConfigPath,
};

const ParseRequestArgsError = ValidateExtraArgError || error{
    InvalidArity,
    UnsupportedMode,
    EmptyKconfigPath,
    EmptyConfigPath,
    EmptyArch,
};

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\x08' => try writer.writeAll("\\b"),
        '\x0c' => try writer.writeAll("\\f"),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => {
            if (c < 0x20) {
                var escaped: [6]u8 = undefined;
                const rendered = try std.fmt.bufPrint(&escaped, "\\u00{x:0>2}", .{c});
                try writer.writeAll(rendered);
            } else {
                try writer.writeByte(c);
            }
        },
    };
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
    if (request.allconfig) |allconfig| {
        try writer.writeAll(",\"KCONFIG_ALLCONFIG\":\"");
        try writeJsonEscaped(writer, allconfig);
        try writer.writeAll("\"");
    }
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
    if (request.mode == .syncconfig) {
        try writer.writeAll(",\"KCONFIG_AUTOCONFIG\":\"");
        try writeJsonEscaped(writer, request.autoconfig orelse "include/config/auto.conf");
        try writer.writeAll("\",\"KCONFIG_AUTOHEADER\":\"");
        try writeJsonEscaped(writer, request.autoheader orelse "include/generated/autoconf.h");
        try writer.writeAll("\"");
        if (request.nosilentupdate) |nosilentupdate| {
            try writer.writeAll(",\"KCONFIG_NOSILENTUPDATE\":\"");
            try writeJsonEscaped(writer, nosilentupdate);
            try writer.writeAll("\"");
        }
    }
    try writer.writeAll("}}\n");
}

fn supportsAllConfig(mode: Mode) bool {
    return switch (mode) {
        .allnoconfig, .allyesconfig, .allmodconfig, .alldefconfig, .randconfig => true,
        else => false,
    };
}

fn requiresModeArg(mode: Mode) bool {
    return mode == .defconfig or mode == .savedefconfig;
}

fn validateExtraArg(mode: Mode, extra_arg: ?[]const u8) ValidateExtraArgError!void {
    if (requiresModeArg(mode)) {
        const mode_arg = extra_arg orelse return error.MissingModeArg;
        if (mode_arg.len == 0) {
            return error.EmptyModeArg;
        }
        return;
    }

    if (supportsAllConfig(mode)) {
        if (extra_arg) |allconfig| {
            if (allconfig.len == 0) {
                return error.EmptyAllConfigPath;
            }
        }
        return;
    }

    if (extra_arg != null) {
        return error.UnexpectedModeArg;
    }
}

fn validateRequiredArg(value: []const u8, comptime err: ParseRequestArgsError) ParseRequestArgsError!void {
    if (value.len == 0) {
        return err;
    }
}

fn parseRequestArgs(args: []const []const u8) ParseRequestArgsError!Request {
    if (args.len < 4 or args.len > 6) {
        return error.InvalidArity;
    }

    var mode: Mode = .oldaskconfig;
    var kconfig_index: usize = 1;

    if (args.len >= 5) {
        mode = Mode.parse(args[1]) orelse return error.UnsupportedMode;
        kconfig_index = 2;
    }

    const extra_arg = if (args.len > kconfig_index + 3) args[kconfig_index + 3] else null;
    try validateExtraArg(mode, extra_arg);

    try validateRequiredArg(args[kconfig_index], error.EmptyKconfigPath);
    try validateRequiredArg(args[kconfig_index + 1], error.EmptyConfigPath);
    try validateRequiredArg(args[kconfig_index + 2], error.EmptyArch);

    return .{
        .mode = mode,
        .kconfig = args[kconfig_index],
        .config = args[kconfig_index + 1],
        .arch = args[kconfig_index + 2],
        .mode_arg = if (requiresModeArg(mode)) extra_arg.? else null,
        .allconfig = if (supportsAllConfig(mode)) extra_arg else null,
    };
}

fn nonEmptyEnvValue(value: ?[:0]const u8) ?[]const u8 {
    const slice = value orelse return null;
    if (slice.len == 0) {
        return null;
    }
    return slice;
}

fn envValue(value: ?[:0]const u8) ?[]const u8 {
    const slice = value orelse return null;
    return slice;
}

fn envValueOrDefault(value: ?[:0]const u8, fallback: []const u8) []const u8 {
    return envValue(value) orelse fallback;
}

fn assignFallbackIfMissing(field: *?[]const u8, fallback: ?[]const u8) void {
    if (field.* == null) {
        field.* = fallback;
    }
}

fn applyModeEnvFallbacks(
    request: *Request,
    allconfig: ?[]const u8,
    seed: ?[]const u8,
    probability: ?[]const u8,
    autoconfig: []const u8,
    autoheader: []const u8,
    nosilentupdate: ?[]const u8,
) void {
    if (supportsAllConfig(request.mode)) {
        assignFallbackIfMissing(&request.allconfig, allconfig);
    }
    if (request.mode == .randconfig) {
        assignFallbackIfMissing(&request.seed, seed);
        assignFallbackIfMissing(&request.probability, probability);
    } else if (request.mode == .syncconfig) {
        assignFallbackIfMissing(&request.autoconfig, autoconfig);
        assignFallbackIfMissing(&request.autoheader, autoheader);
        assignFallbackIfMissing(&request.nosilentupdate, nosilentupdate);
    }
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const allconfig = envValue(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_ALLCONFIG"));
    const seed = nonEmptyEnvValue(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_SEED"));
    const probability = nonEmptyEnvValue(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_PROBABILITY"));
    const autoconfig = envValueOrDefault(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_AUTOCONFIG"), "include/config/auto.conf");
    const autoheader = envValueOrDefault(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_AUTOHEADER"), "include/generated/autoconf.h");
    const nosilentupdate = nonEmptyEnvValue(std.process.Environ.getPosix(init.minimal.environ, "KCONFIG_NOSILENTUPDATE"));

    var request = parseRequestArgs(args) catch |err| switch (err) {
        error.InvalidArity => {
            var stderr_buffer: [176]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Usage: conf_bridge [<mode>] <Kconfig> <.config> <arch> [mode-arg|allconfig]\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.UnsupportedMode => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: unsupported kconfig mode\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.MissingModeArg => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: mode requires <mode-arg>\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.UnexpectedModeArg => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: unexpected mode argument\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyModeArg => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: mode argument must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyAllConfigPath => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: KCONFIG_ALLCONFIG path must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyKconfigPath => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: <Kconfig> must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyConfigPath => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: <.config> must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyArch => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: <arch> must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
    };
    applyModeEnvFallbacks(&request, allconfig, seed, probability, autoconfig, autoheader, nosilentupdate);

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfBridge(&stdout_writer.interface, request);
    try stdout_writer.interface.flush();
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

test "conf bridge emits listnewconfig argv and env" {
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
        .mode = .listnewconfig,
        .kconfig = "Kconfig",
        .config = "pending/.config",
        .arch = "s390",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"listnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--listnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"pending/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"s390\"") != null);
}

test "conf bridge emits helpnewconfig argv and env" {
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
        .mode = .helpnewconfig,
        .kconfig = "Kconfig",
        .config = "help/.config",
        .arch = "powerpc64le",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"helpnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--helpnewconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"help/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"powerpc64le\"") != null);
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

test "conf bridge emits syncconfig nosilentupdate env when present" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
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
        .nosilentupdate = "1",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\"") != null);
}

test "conf bridge omits empty syncconfig nosilentupdate env values" {
    try std.testing.expectEqual(@as(?[]const u8, null), nonEmptyEnvValue(""));
    try std.testing.expectEqual(@as(?[]const u8, null), nonEmptyEnvValue(null));

    const nosilentupdate = nonEmptyEnvValue("1");
    try std.testing.expectEqualStrings("1", nosilentupdate.?);
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

test "conf bridge prefers explicit allconfig over env fallback" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "allnoconfig",
        "Kconfig",
        "none/.config",
        "arm64",
        "arch/arm64/configs/tiny.config",
    });
    applyModeEnvFallbacks(&request, "all.config", null, null, "include/config/auto.conf", "include/generated/autoconf.h", null);

    try std.testing.expectEqualStrings("arch/arm64/configs/tiny.config", request.allconfig.?);
}

test "conf bridge rejects explicit empty allconfig cli paths" {
    try std.testing.expectError(error.EmptyAllConfigPath, parseRequestArgs(&.{
        "conf_bridge",
        "allnoconfig",
        "Kconfig",
        "none/.config",
        "arm64",
        "",
    }));
}

test "conf bridge preserves empty allconfig env trigger for allconfig modes" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "allnoconfig",
        "Kconfig",
        "none/.config",
        "arm64",
    });
    applyModeEnvFallbacks(&request, envValue(""), null, null, "include/config/auto.conf", "include/generated/autoconf.h", null);

    try std.testing.expect(request.allconfig != null);
    try std.testing.expectEqual(@as(usize, 0), request.allconfig.?.len);
}

test "conf bridge uses allconfig env fallback for allconfig modes" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "allnoconfig",
        "Kconfig",
        "none/.config",
        "arm64",
    });
    applyModeEnvFallbacks(&request, "all.config", null, null, "include/config/auto.conf", "include/generated/autoconf.h", null);

    try std.testing.expectEqualStrings("all.config", request.allconfig.?);
}

test "conf bridge defaults to oldaskconfig when mode is omitted" {
    const request = try parseRequestArgs(&.{
        "conf_bridge",
        "Kconfig",
        ".config",
        "x86_64",
    });

    try std.testing.expectEqual(Mode.oldaskconfig, request.mode);
    try std.testing.expectEqualStrings("Kconfig", request.kconfig);
    try std.testing.expectEqualStrings(".config", request.config);
    try std.testing.expectEqualStrings("x86_64", request.arch);
    try std.testing.expectEqual(@as(?[]const u8, null), request.mode_arg);
    try std.testing.expectEqual(@as(?[]const u8, null), request.allconfig);
}

test "conf bridge uses randconfig env fallback for seed and probability" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "randconfig",
        "Kconfig",
        "rand/.config",
        "x86",
    });
    applyModeEnvFallbacks(
        &request,
        "seed/allrandom.config",
        "0xC0FFEE",
        "10:20:30",
        "include/config/auto.conf",
        "include/generated/autoconf.h",
        null,
    );

    try std.testing.expectEqualStrings("seed/allrandom.config", request.allconfig.?);
    try std.testing.expectEqualStrings("0xC0FFEE", request.seed.?);
    try std.testing.expectEqualStrings("10:20:30", request.probability.?);
}

test "conf bridge preserves explicit empty syncconfig autoconfig env" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "syncconfig",
        "Kconfig",
        "out/.config",
        "riscv64",
    });
    applyModeEnvFallbacks(
        &request,
        null,
        null,
        null,
        envValue("") orelse "include/config/auto.conf",
        "include/generated/autoconf.h",
        null,
    );

    try std.testing.expect(request.autoconfig != null);
    try std.testing.expectEqual(@as(usize, 0), request.autoconfig.?.len);
}

test "conf bridge preserves explicit empty syncconfig autoheader env" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "syncconfig",
        "Kconfig",
        "out/.config",
        "riscv64",
    });
    applyModeEnvFallbacks(
        &request,
        null,
        null,
        null,
        "include/config/auto.conf",
        envValue("") orelse "include/generated/autoconf.h",
        null,
    );

    try std.testing.expect(request.autoheader != null);
    try std.testing.expectEqual(@as(usize, 0), request.autoheader.?.len);
}

test "conf bridge keeps explicit randconfig seed and probability over env fallback" {
    var request: Request = .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = "rand/.config",
        .arch = "x86",
        .allconfig = "seed/explicit.config",
        .seed = "0xBEEF",
        .probability = "15:25:35",
    };
    applyModeEnvFallbacks(
        &request,
        "seed/allrandom.config",
        "0xC0FFEE",
        "10:20:30",
        "include/config/auto.conf",
        "include/generated/autoconf.h",
        null,
    );

    try std.testing.expectEqualStrings("seed/explicit.config", request.allconfig.?);
    try std.testing.expectEqualStrings("0xBEEF", request.seed.?);
    try std.testing.expectEqualStrings("15:25:35", request.probability.?);
}

test "conf bridge keeps explicit syncconfig outputs over env fallback" {
    var request: Request = .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = "out/.config",
        .arch = "riscv64",
        .autoconfig = "generated/explicit/auto.conf",
        .autoheader = "generated/explicit/autoconf.h",
        .nosilentupdate = "keep",
    };
    applyModeEnvFallbacks(
        &request,
        null,
        null,
        null,
        "generated/phase2/auto-sync.conf",
        "generated/phase2/autoconf-sync.h",
        "1",
    );

    try std.testing.expectEqualStrings("generated/explicit/auto.conf", request.autoconfig.?);
    try std.testing.expectEqualStrings("generated/explicit/autoconf.h", request.autoheader.?);
    try std.testing.expectEqualStrings("keep", request.nosilentupdate.?);
}

test "conf bridge uses syncconfig env fallbacks for output paths" {
    var request = try parseRequestArgs(&.{
        "conf_bridge",
        "syncconfig",
        "Kconfig",
        "out/.config",
        "riscv64",
    });
    applyModeEnvFallbacks(
        &request,
        null,
        null,
        null,
        "generated/phase2/auto-sync.conf",
        "generated/phase2/autoconf-sync.h",
        "1",
    );

    try std.testing.expectEqualStrings("generated/phase2/auto-sync.conf", request.autoconfig.?);
    try std.testing.expectEqualStrings("generated/phase2/autoconf-sync.h", request.autoheader.?);
    try std.testing.expectEqualStrings("1", request.nosilentupdate.?);
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

test "conf bridge emits mod2yesconfig argv and env" {
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
        .mode = .mod2yesconfig,
        .kconfig = "Kconfig",
        .config = "promote/.config",
        .arch = "loongarch",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"mod2yesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--mod2yesconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"promote/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"loongarch\"") != null);
}

test "conf bridge emits mod2noconfig argv and env" {
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
        .mode = .mod2noconfig,
        .kconfig = "Kconfig",
        .config = "demote/.config",
        .arch = "mips",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"mod2noconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--mod2noconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"demote/.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"ARCH\":\"mips\"") != null);
}

test "conf bridge emits randconfig seed and probability env when present" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 224), .allocator = allocator };
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
        .arch = "x86",
        .allconfig = "seed/allrandom.config",
        .seed = "0xC0FFEE",
        .probability = "10:20:30",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"seed/allrandom.config\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_SEED\":\"0xC0FFEE\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_PROBABILITY\":\"10:20:30\"") != null);
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
        .config = "out/.config",
        .arch = "arm64",
        .mode_arg = "arch/arm64/configs/minimal_defconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"mode\":\"savedefconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--savedefconfig\",\"arch/arm64/configs/minimal_defconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_CONFIG\":\"out/.config\"") != null);
}

test "conf bridge escapes JSON-sensitive argv and env values" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 256), .allocator = allocator };
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
        .kconfig = "Kconfig\"main",
        .config = "out\t/.config",
        .arch = "arm64\nbe",
        .mode_arg = "arch\\arm64/configs/mini\"defconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "Kconfig\\\"main") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "out\\t/.config") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "arm64\\nbe") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "arch\\\\arm64/configs/mini\\\"defconfig") != null);
}

test "conf bridge escapes low control bytes in argv and env values" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 256), .allocator = allocator };
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

        fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }
    };

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try runConfBridge(&capture, .{
        .mode = .defconfig,
        .kconfig = "Kconfig\x08main",
        .config = "out\x0c/.config",
        .arch = "arm64\x1dbe",
        .mode_arg = "arch/arm64/configs/mini\x1fdefconfig",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "Kconfig\\bmain") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "out\\f/.config") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "arm64\\u001dbe") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "mini\\u001fdefconfig") != null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x08') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x0c') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x1d') == null);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, '\x1f') == null);
}