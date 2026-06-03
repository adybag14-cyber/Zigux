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

test "runFixdep treats rlib source and so dependency payloads as no-parse files" {
    const depfile_name = "zigux_fixdep_rlib_no_parse_public_entry.d";
    const source_name = "zigux_fixdep_rlib_no_parse_public_entry.rlib";
    const dependency_name = "zigux_fixdep_rlib_no_parse_public_entry.so";
    const target = "zigux_fixdep_rlib_no_parse_public_entry.o";
    const cmdline = "rustc --emit dep-info=zigux_fixdep_rlib_no_parse_public_entry.d";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "CONFIG_ZIGUX_RLIB_SOURCE_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = dependency_name,
        .data = "CONFIG_ZIGUX_SO_DEP_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, dependency_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = target ++ ": " ++ source_name ++ " " ++ dependency_name ++ "\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_name) catch {};

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

    try std.testing.expectEqualStrings(
        "savedcmd_zigux_fixdep_rlib_no_parse_public_entry.o := rustc --emit dep-info=zigux_fixdep_rlib_no_parse_public_entry.d\n\n" ++
            "source_zigux_fixdep_rlib_no_parse_public_entry.o := zigux_fixdep_rlib_no_parse_public_entry.rlib\n\n" ++
            "deps_zigux_fixdep_rlib_no_parse_public_entry.o := \\\n" ++
            "  zigux_fixdep_rlib_no_parse_public_entry.so \\\n" ++
            "\n" ++
            "zigux_fixdep_rlib_no_parse_public_entry.o: $(deps_zigux_fixdep_rlib_no_parse_public_entry.o)\n\n" ++
            "$(deps_zigux_fixdep_rlib_no_parse_public_entry.o):\n",
        capture.list.items,
    );
}
