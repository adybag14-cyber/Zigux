const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep.zig");

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

test "runFixdep preserves backticks in saved command public entry" {
    const depfile_name = "zigux_fixdep_backtick_cmdline_test.d";
    const source_name = "zigux_fixdep_backtick_cmdline_source.c";
    const target = "backtick.o";
    const cmdline = "cc -Dzigux_token=`phase2` -Dzigux_pair=`left``right` -c zigux_fixdep_backtick_cmdline_source.c -o backtick-output.o";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = "backtick.o: zigux_fixdep_backtick_cmdline_source.c\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "int value = CONFIG_ZIGUX_CMDLINE_BACKTICK_SOURCE;\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_name,
        target,
        cmdline,
    );

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "savedcmd_backtick.o := cc -Dzigux_token=`phase2` ") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "-Dzigux_pair=`left``right`") != null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "include/config/ZIGUX_CMDLINE_BACKTICK_SOURCE") != null);
    try std.testing.expectEqualStrings(
        "savedcmd_backtick.o := cc -Dzigux_token=`phase2` -Dzigux_pair=`left``right` -c zigux_fixdep_backtick_cmdline_source.c -o backtick-output.o\n\n" ++
            "source_backtick.o := zigux_fixdep_backtick_cmdline_source.c\n\n" ++
            "deps_backtick.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_CMDLINE_BACKTICK_SOURCE) \\\n" ++
            "\n" ++
            "backtick.o: $(deps_backtick.o)\n\n" ++
            "$(deps_backtick.o):\n",
        capture.list.items,
    );
}
