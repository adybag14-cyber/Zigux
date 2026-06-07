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

test "runFixdep preserves parenthesis bytes in saved command" {
    const depfile_path = "zigux_fixdep_parenthesis_cmdline.d";
    const source_path = "zigux_fixdep_parenthesis_cmdline_source.c";
    const target = "parenthesis.o";
    const cmdline = "cc -DPAIR=(left,right) -c zigux_fixdep_parenthesis_cmdline_source.c -o parenthesis.o";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_path,
        .data = "int zigux_fixdep_parenthesis_cmdline(void) { return CONFIG_ZIGUX_CMDLINE_PARENTHESIS_SOURCE; }\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_path) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_path,
        .data = target ++ ": " ++ source_path ++ "\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_path) catch {};

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
        "savedcmd_parenthesis.o := cc -DPAIR=(left,right) -c zigux_fixdep_parenthesis_cmdline_source.c -o parenthesis.o\n\n" ++
            "source_parenthesis.o := zigux_fixdep_parenthesis_cmdline_source.c\n\n" ++
            "deps_parenthesis.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_CMDLINE_PARENTHESIS_SOURCE) \\\n" ++
            "\nparenthesis.o: $(deps_parenthesis.o)\n\n" ++
            "$(deps_parenthesis.o):\n",
        capture.list.items,
    );
}
