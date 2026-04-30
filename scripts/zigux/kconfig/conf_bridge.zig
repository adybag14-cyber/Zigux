const std = @import("std");
const Io = std.Io;

pub const Mode = enum {
    oldaskconfig,
    olddefconfig,
    oldconfig,
    listnewconfig,
    helpnewconfig,
    yes2modconfig,
    mod2yesconfig,
    defconfig,
    savedefconfig,
    mod2noconfig,
    allnoconfig,
    allyesconfig,
    allmodconfig,
    alldefconfig,
    randconfig,
    syncconfig,

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
            .olddefconfig => "--olddefconfig",
            .oldconfig => "--oldconfig",
            .listnewconfig => "--listnewconfig",
            .helpnewconfig => "--helpnewconfig",
            .yes2modconfig => "--yes2modconfig",
            .mod2yesconfig => "--mod2yesconfig",
            .defconfig => "--defconfig",
            .savedefconfig => "--savedefconfig",
            .mod2noconfig => "--mod2noconfig",
            .allnoconfig => "--allnoconfig",
            .allyesconfig => "--allyesconfig",
            .allmodconfig => "--allmodconfig",
            .alldefconfig => "--alldefconfig",
            .randconfig => "--randconfig",
            .syncconfig => "--syncconfig",
        };
    }

    pub fn text(self: Mode) []const u8 {
        return switch (self) {
            .oldaskconfig => "oldaskconfig",
            .olddefconfig => "olddefconfig",
            .oldconfig => "oldconfig",
            .listnewconfig => "listnewconfig",
            .helpnewconfig => "helpnewconfig",
            .yes2modconfig => "yes2modconfig",
            .mod2yesconfig => "mod2yesconfig",
            .defconfig => "defconfig",
            .savedefconfig => "savedefconfig",
            .mod2noconfig => "mod2noconfig",
            .allnoconfig => "allnoconfig",
            .allyesconfig => "allyesconfig",
            .allmodconfig => "allmodconfig",
            .alldefconfig => "alldefconfig",
            .randconfig => "randconfig",
            .syncconfig => "syncconfig",
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
};

const ValidateExtraArgError = error{
    MissingModeArg,
    UnexpectedModeArg,
    EmptyModeArg,
};

const ValidateRequiredArgError = error{
    EmptyKconfig,
    EmptyConfig,
    EmptyArch,
};

const ParseRequestArgsError = ValidateExtraArgError || ValidateRequiredArgError || error{
    InvalidArity,
    UnsupportedMode,
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
    if (request.mode == .syncconfig) {
        try writer.writeAll(",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
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
        return;
    }

    if (extra_arg != null) {
        return error.UnexpectedModeArg;
    }
}

fn validateRequiredArgs(kconfig: []const u8, config: []const u8, arch: []const u8) ValidateRequiredArgError!void {
    if (kconfig.len == 0) {
        return error.EmptyKconfig;
    }
    if (config.len == 0) {
        return error.EmptyConfig;
    }
    if (arch.len == 0) {
        return error.EmptyArch;
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
    try validateRequiredArgs(args[kconfig_index], args[kconfig_index + 1], args[kconfig_index + 2]);

    return .{
        .mode = mode,
        .kconfig = args[kconfig_index],
        .config = args[kconfig_index + 1],
        .arch = args[kconfig_index + 2],
        .mode_arg = if (requiresModeArg(mode)) extra_arg.? else null,
        .allconfig = if (supportsAllConfig(mode)) extra_arg else null,
    };
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    const request = parseRequestArgs(args) catch |err| switch (err) {
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
        error.EmptyKconfig => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: Kconfig path must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyConfig => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: .config path must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
        error.EmptyArch => {
            var stderr_buffer: [160]u8 = undefined;
            var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
            try stderr_writer.interface.writeAll("Error: arch must not be empty\n");
            try stderr_writer.interface.flush();
            std.process.exit(1);
        },
    };

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

test "conf bridge emits allconfig env for allconfig family modes" {
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

    const cases = [_]struct {
        mode: Mode,
        mode_text: []const u8,
    }{
        .{ .mode = .allnoconfig, .mode_text = "allnoconfig" },
        .{ .mode = .allyesconfig, .mode_text = "allyesconfig" },
        .{ .mode = .allmodconfig, .mode_text = "allmodconfig" },
        .{ .mode = .alldefconfig, .mode_text = "alldefconfig" },
        .{ .mode = .randconfig, .mode_text = "randconfig" },
    };

    inline for (cases) |case| {
        var capture = try Capture.init(std.testing.allocator);
        defer capture.deinit();

        try runConfBridge(&capture, .{
            .mode = case.mode,
            .kconfig = "Kconfig",
            .config = "seed/.config",
            .arch = "arm64",
            .allconfig = "arch/arm64/configs/all.config",
        });

        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, case.mode_text) != null);
        try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"arch/arm64/configs/all.config\"") != null);
    }
}

test "conf bridge requires mode arg for defconfig modes" {
    try std.testing.expectError(error.MissingModeArg, validateExtraArg(.defconfig, null));
    try std.testing.expectError(error.MissingModeArg, validateExtraArg(.savedefconfig, null));
}

test "conf bridge rejects mode arg for non-argument modes" {
    try std.testing.expectError(error.UnexpectedModeArg, validateExtraArg(.olddefconfig, "unexpected"));
    try std.testing.expectError(error.UnexpectedModeArg, validateExtraArg(.syncconfig, "unexpected"));
}

test "conf bridge accepts valid mode arg combinations" {
    try validateExtraArg(.defconfig, "arch/arm64/configs/defconfig");
    try validateExtraArg(.savedefconfig, "arch/arm64/configs/minimal_defconfig");
    try validateExtraArg(.allnoconfig, "");
    try validateExtraArg(.allnoconfig, "arch/arm64/configs/all.config");
    try validateExtraArg(.oldconfig, null);
}

test "conf bridge rejects empty extra arguments" {
    try std.testing.expectError(error.EmptyModeArg, validateExtraArg(.defconfig, ""));
    try std.testing.expectError(error.EmptyModeArg, validateExtraArg(.savedefconfig, ""));
}

test "conf bridge rejects empty required positional arguments" {
    try std.testing.expectError(error.EmptyKconfig, validateRequiredArgs("", ".config", "x86_64"));
    try std.testing.expectError(error.EmptyConfig, validateRequiredArgs("Kconfig", "", "x86_64"));
    try std.testing.expectError(error.EmptyArch, validateRequiredArgs("Kconfig", ".config", ""));
}

test "conf bridge defaults to oldaskconfig when mode is omitted" {
    const args = [_][]const u8{
        "conf_bridge",
        "Kconfig",
        ".config",
        "x86_64",
    };

    const request = try parseRequestArgs(&args);
    try std.testing.expectEqual(Mode.oldaskconfig, request.mode);
    try std.testing.expectEqualStrings("Kconfig", request.kconfig);
    try std.testing.expectEqualStrings(".config", request.config);
    try std.testing.expectEqualStrings("x86_64", request.arch);
    try std.testing.expect(request.mode_arg == null);
    try std.testing.expect(request.allconfig == null);
}

test "conf bridge parses explicit mode arguments" {
    const args = [_][]const u8{
        "conf_bridge",
        "defconfig",
        "Kconfig",
        "out/.config",
        "arm64",
        "arch/arm64/configs/defconfig",
    };

    const request = try parseRequestArgs(&args);
    try std.testing.expectEqual(Mode.defconfig, request.mode);
    try std.testing.expectEqualStrings("arch/arm64/configs/defconfig", request.mode_arg.?);
}

test "conf bridge rejects unsupported explicit modes" {
    const args = [_][]const u8{
        "conf_bridge",
        "bogusmode",
        "Kconfig",
        ".config",
        "x86_64",
    };

    try std.testing.expectError(error.UnsupportedMode, parseRequestArgs(&args));
}

test "conf bridge rejects empty required args while parsing requests" {
    const missing_kconfig = [_][]const u8{
        "conf_bridge",
        "oldconfig",
        "",
        ".config",
        "x86_64",
    };
    const missing_config = [_][]const u8{
        "conf_bridge",
        "Kconfig",
        "",
        "x86_64",
    };
    const missing_arch = [_][]const u8{
        "conf_bridge",
        "defconfig",
        "Kconfig",
        ".config",
        "",
        "arch/x86/configs/defconfig",
    };

    try std.testing.expectError(error.EmptyKconfig, parseRequestArgs(&missing_kconfig));
    try std.testing.expectError(error.EmptyConfig, parseRequestArgs(&missing_config));
    try std.testing.expectError(error.EmptyArch, parseRequestArgs(&missing_arch));
}

test "conf bridge mode text and flag stay aligned with enum tags" {
    inline for (std.meta.fields(Mode)) |field| {
        const mode = @field(Mode, field.name);
        try std.testing.expectEqual(mode, Mode.parse(field.name).?);
        try std.testing.expectEqualStrings(field.name, mode.text());
        try std.testing.expectEqualStrings("--" ++ field.name, mode.flag());
    }
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

test "conf bridge preserves empty KCONFIG_ALLCONFIG for default seed lookup" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{ .list = try std.ArrayList(u8).initCapacity(allocator, 176), .allocator = allocator };
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
        .mode = .allnoconfig,
        .kconfig = "Kconfig",
        .config = "none/.config",
        .arch = "arm64",
        .allconfig = "",
    });

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"--allnoconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "\"KCONFIG_ALLCONFIG\":\"\"") != null);
}
