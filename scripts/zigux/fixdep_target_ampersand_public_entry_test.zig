const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "runFixdep preserves ampersand target names in public output" {
    const allocator = std.testing.allocator;
    const target = "zigux&target.o";
    const depfile_path = "zigux_fixdep_target_ampersand_public_entry.d";
    const source_path = "zigux_fixdep_target_ampersand_source.c";
    const header_path = "zigux_fixdep_target_ampersand_header.h";
    const cmdline = "zig cc -DTARGET_AMPERSAND=1 -c zigux_fixdep_target_ampersand_source.c";

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_path,
        .data = "/* CONFIG_ZIGUX_TARGET_AMPERSAND_SOURCE */\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, source_path) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = header_path,
        .data = "#define CONFIG_ZIGUX_TARGET_AMPERSAND_HEADER 1\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, header_path) catch {};

    try std.Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_path,
        .data = target ++ ": " ++ source_path ++ " " ++ header_path ++ "\n",
    });
    defer std.Io.Dir.cwd().deleteFile(std.testing.io, depfile_path) catch {};

    var capture = try Capture.init(allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    );

    try std.testing.expectEqualStrings(
        "savedcmd_zigux&target.o := " ++ cmdline ++ "\n\n" ++
            "source_zigux&target.o := " ++ source_path ++ "\n\n" ++
            "deps_zigux&target.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_AMPERSAND_SOURCE) \\\n" ++
            "  " ++ header_path ++ " \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_AMPERSAND_HEADER) \\\n" ++
            "\n" ++
            "zigux&target.o: $(deps_zigux&target.o)\n\n" ++
            "$(deps_zigux&target.o):\n",
        capture.list.items,
    );
}
