const std = @import("std");
const fixdep = @import("fixdep.zig");
const Io = std.Io;

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 256),
            .allocator = allocator,
        };
    }

    fn deinit(self: *Capture) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *Capture, comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *Capture) !void {}
};

test "runFixdep preserves SO byte in savedcmd through public entry" {
    const depfile_name = "zigux_fixdep_cmdline_so_public_entry.d";
    const source_name = "zigux_fixdep_cmdline_so_public_entry.c";
    const target_name = "zigux_fixdep_cmdline_so_public_entry.o";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data =
        \\#define CONFIG_ZIGUX_CMDLINE_SO 1
        \\int zigux_fixdep_cmdline_so_public_entry(void) { return 0; }
        \\
        ,
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data =
        \\zigux_fixdep_cmdline_so_public_entry.o: zigux_fixdep_cmdline_so_public_entry.c
        \\
        ,
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    var cmdline = std.ArrayList(u8).empty;
    defer cmdline.deinit(std.testing.allocator);
    try cmdline.appendSlice(std.testing.allocator, "cc -D");
    try cmdline.append(std.testing.allocator, 0x0e);
    try cmdline.appendSlice(std.testing.allocator, "CONFIG_ZIGUX_CMDLINE_SO -c ");
    try cmdline.appendSlice(std.testing.allocator, source_name);
    try cmdline.appendSlice(std.testing.allocator, " -o ");
    try cmdline.appendSlice(std.testing.allocator, target_name);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_name,
        target_name,
        cmdline.items,
    );

    const output = capture.list.items;
    const saved_prefix = "savedcmd_zigux_fixdep_cmdline_so_public_entry.o := cc -D";
    const saved_start = std.mem.indexOf(u8, output, saved_prefix) orelse return error.MissingSavedcmdPrefix;
    const so_index = saved_start + saved_prefix.len;
    try std.testing.expect(so_index < output.len);
    try std.testing.expectEqual(@as(u8, 0x0e), output[so_index]);
    try std.testing.expect(std.mem.indexOf(u8, output, "CONFIG_ZIGUX_CMDLINE_SO") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "    $(wildcard include/config/ZIGUX_CMDLINE_SO) \\\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, output, "\nzigux_fixdep_cmdline_so_public_entry.o: $(deps_zigux_fixdep_cmdline_so_public_entry.o)\n") != null);
}
