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
};

const ValidateModeArgError = error{
    MissingModeArg,
    UnexpectedModeArg,
};

fn writeJsonEscaped(writer: anytype, text: []const u8) !void {
    for (text) |c| switch (c) {
        '\\' => try writer.writeAll("\\\\"),
        '"' => try writer.writeAll("\\\""),
        '\n' => try writer.writeAll("\\n"),
        '\r' => try writer.writeAll("\\r"),
        '\t' => try writer.writeAll("\\t"),
        else => try writer.writeByte(c),
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
    if (request.mode == .syncconfig) {
        try writer.writeAll(",\"KCONFIG_AUTOCONFIG\":\"include/config/auto.conf\",\"KCONFIG_AUTOHEADER\":\"include/generated/autoconf.h\"");
    }
    try writer.writeAll("}}\n");
}

fn validateModeArg(mode: Mode, mode_arg: ?[]const u8) ValidateModeArgError!void {
    if ((mode == .defconfig or mode == .savedefconfig) and mode_arg == null) {
        return error.MissingModeArg;
    }
    if (mode != .defconfig and mode != .savedefconfig and mode_arg != null) {
        return error.UnexpectedModeArg;
    }
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    if (args.len < 5 or args.len > 6) {
        var stderr_buffer: [160]u8 = undefined;
        var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
        try stderr_writer.interface.writeAll("Usage: conf_bridge <mode> <Kconfig> <.config> <arch> [mode-arg]\n");
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

    const mode_arg = if (args.len == 6) args[5] else null;
    validateModeArg(mode, mode_arg) catch |err| switch (err) {
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
    };

    var stdout_buffer: [1024]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    try runConfBridge(&stdout_writer.interface, .{
        .mode = mode,
        .kconfig = args[2],
        .config = args[3],
        .arch = args[4],
        .mode_arg = mode_arg,
    });
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

test "conf bridge requires mode arg for defconfig modes" {
    try std.testing.expectError(error.MissingModeArg, validateModeArg(.defconfig, null));
    try std.testing.expectError(error.MissingModeArg, validateModeArg(.savedefconfig, null));
}

test "conf bridge rejects mode arg for non-argument modes" {
    try std.testing.expectError(error.UnexpectedModeArg, validateModeArg(.olddefconfig, "unexpected"));
    try std.testing.expectError(error.UnexpectedModeArg, validateModeArg(.syncconfig, "unexpected"));
}

test "conf bridge accepts valid mode arg combinations" {
    try validateModeArg(.defconfig, "arch/arm64/configs/defconfig");
    try validateModeArg(.savedefconfig, "arch/arm64/configs/minimal_defconfig");
    try validateModeArg(.oldconfig, null);
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
