const std = @import("std");
const Io = std.Io;
const conf_bridge = @import("conf_bridge.zig");

const source_path = "scripts/zigux/kconfig/conf_bridge.zig";

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

fn expectSourceContains(source: []const u8, fragment: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, fragment) != null);
}

test "non-argument modes guard stray mode text before bridge options" {
    const source = try Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, std.testing.allocator, .limited(256 * 1024));
    defer std.testing.allocator.free(source);

    try expectSourceContains(source, "if (!modeRequiresArgument(mode))");
    try expectSourceContains(source, "args.len > next_index and !looksLikeBridgeOption(args[next_index])");
    try expectSourceContains(source, "Error: unexpected mode argument\\n");
    try expectSourceContains(source, "break :blk null;");
    try expectSourceContains(source, "const options = parseBridgeOptions(mode, args[next_index..])");
}

test "recognized bridge options still render without a mode argument" {
    var sync_capture = try TestCapture.init(std.testing.allocator, 256);
    defer sync_capture.deinit();

    try conf_bridge.runConfBridge(&sync_capture, .{
        .mode = .syncconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .silent = true,
        .nosilentupdate = "1",
    });

    try std.testing.expect(std.mem.indexOf(u8, sync_capture.list.items, "\"mode\":\"syncconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sync_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--syncconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, sync_capture.list.items, "\"KCONFIG_NOSILENTUPDATE\":\"1\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sync_capture.list.items, "\"mode_arg\"") == null);

    var rand_capture = try TestCapture.init(std.testing.allocator, 256);
    defer rand_capture.deinit();

    try conf_bridge.runConfBridge(&rand_capture, .{
        .mode = .randconfig,
        .kconfig = "Kconfig",
        .config = ".config",
        .arch = "x86_64",
        .silent = true,
        .probability = "15:25",
    });

    try std.testing.expect(std.mem.indexOf(u8, rand_capture.list.items, "\"mode\":\"randconfig\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, rand_capture.list.items, "\"argv\":[\"scripts/kconfig/conf\",\"--silent\",\"--randconfig\",\"Kconfig\"]") != null);
    try std.testing.expect(std.mem.indexOf(u8, rand_capture.list.items, "\"KCONFIG_PROBABILITY\":\"15:25\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, rand_capture.list.items, "\"KCONFIG_SEED\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, rand_capture.list.items, "\"mode_arg\"") == null);
}
