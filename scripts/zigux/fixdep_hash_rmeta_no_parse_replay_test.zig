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

test "runFixdep preserves escaped hash rmeta paths without parsing no-parse payloads" {
    const depfile_name = "zigux_fixdep_hash_rmeta_no_parse_replay.d";
    const source_name = "zigux_fixdep_hash#source.rmeta";
    const dependency_name = "zigux_fixdep_hash#dep.so";
    const target = "zigux_fixdep_hash_rmeta_no_parse_replay.o";
    const cmdline = "rustc --emit dep-info=zigux_fixdep_hash_rmeta_no_parse_replay.d";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_name,
        .data = "CONFIG_ZIGUX_HASH_RMETA_SOURCE_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = dependency_name,
        .data = "CONFIG_ZIGUX_HASH_SO_DEP_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, dependency_name) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = target ++ ": zigux_fixdep_hash\\#source.rmeta zigux_fixdep_hash\\#dep.so\n",
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
        "savedcmd_zigux_fixdep_hash_rmeta_no_parse_replay.o := rustc --emit dep-info=zigux_fixdep_hash_rmeta_no_parse_replay.d\n\n" ++
            "source_zigux_fixdep_hash_rmeta_no_parse_replay.o := zigux_fixdep_hash#source.rmeta\n\n" ++
            "deps_zigux_fixdep_hash_rmeta_no_parse_replay.o := \\\n" ++
            "  zigux_fixdep_hash#dep.so \\\n" ++
            "\n" ++
            "zigux_fixdep_hash_rmeta_no_parse_replay.o: $(deps_zigux_fixdep_hash_rmeta_no_parse_replay.o)\n\n" ++
            "$(deps_zigux_fixdep_hash_rmeta_no_parse_replay.o):\n",
        capture.list.items,
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        std.mem.indexOf(u8, capture.list.items, "include/config/ZIGUX_HASH_"),
    );
}
