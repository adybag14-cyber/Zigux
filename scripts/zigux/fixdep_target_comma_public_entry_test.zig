const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer self.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *@This()) !void {}
};

test "runFixdep preserves comma target names through public entry output" {
    const depfile_path = "zigux_fixdep_target_comma.d";
    const source_path = "zigux_fixdep_target_comma_source.c";
    const header_path = "zigux_fixdep_target_comma_config.h";
    const so_path = "zigux_fixdep_target_comma_dep.so";
    const target = "zigux,target,module.o";
    const cmdline = "cc -DZIGUX_TARGET_COMMA=1 -c zigux_fixdep_target_comma_source.c -o zigux,target,module.o";

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_path,
        .data = "/* CONFIG_ZIGUX_TARGET_COMMA_SOURCE */\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, source_path) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = header_path,
        .data = "#define CONFIG_ZIGUX_TARGET_COMMA_HEADER 1\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, header_path) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_path,
        .data = target ++ ": " ++ source_path ++ " " ++ header_path ++ " " ++ so_path ++ "\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, depfile_path) catch {};

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(
        "savedcmd_" ++ target ++ " := " ++ cmdline ++ "\n\n" ++
            "source_" ++ target ++ " := " ++ source_path ++ "\n\n" ++
            "deps_" ++ target ++ " := \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_COMMA_SOURCE) \\\n" ++
            "  " ++ header_path ++ " \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_COMMA_HEADER) \\\n" ++
            "  " ++ so_path ++ " \\\n" ++
            "\n" ++
            target ++ ": $(deps_" ++ target ++ ")\n\n" ++
            "$(deps_" ++ target ++ "):\n",
        capture.list.items,
    );
}
