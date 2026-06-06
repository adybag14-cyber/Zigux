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

test "runFixdep preserves FS byte in savedcmd prelude" {
    const depfile_name = "zigux_fixdep_fs_cmdline_test.d";
    const source_name = "zigux_fixdep_fs_cmdline_source.c";
    const target_name = "zigux_fixdep_fs_cmdline.o";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "int zigux_fixdep_fs_cmdline(void) { return CONFIG_ZIGUX_CMDLINE_FS_SOURCE; }\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = target_name ++ ": " ++ source_name ++ "\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

    const cmdline = "cc" ++ [_]u8{0x1c} ++ "-DZIGUX_CMDLINE_FS=1 -c " ++ source_name;

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_name,
        target_name,
        cmdline,
    );

    const expected =
        "savedcmd_" ++ target_name ++ " := " ++ cmdline ++ "\n\n" ++
        "source_" ++ target_name ++ " := " ++ source_name ++ "\n\n" ++
        "deps_" ++ target_name ++ " := \\\n" ++
        "    $(wildcard include/config/ZIGUX_CMDLINE_FS_SOURCE) \\\n" ++
        "\n" ++
        target_name ++ ": $(deps_" ++ target_name ++ ")\n\n" ++
        "$(deps_" ++ target_name ++ "):\n";

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOfScalar(u8, capture.list.items, 0x1c) != null);
}
