const std = @import("std");
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

test "runFixdep preserves hash bytes in saved command lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "zigux_fixdep_hash_cmdline_source.c",
        .data = "int hash_cmdline_source = CONFIG_ZIGUX_CMDLINE_HASH_SOURCE;\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/zigux_fixdep_hash_cmdline_source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "hash.o: {s}\n",
        .{source_path},
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "hash.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/hash.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const cmdline = "cc -DVALUE#fragment=1 -c zigux_fixdep_hash_cmdline_source.c";
    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "hash.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_hash.o := {s}\n\n" ++
            "source_hash.o := {s}\n\n" ++
            "deps_hash.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_CMDLINE_HASH_SOURCE) \\\n" ++
            "\n" ++
            "hash.o: $(deps_hash.o)\n\n" ++
            "$(deps_hash.o):\n",
        .{ cmdline, source_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "VALUE#fragment") != null);
    try std.testing.expectEqualStrings(expected, capture.list.items);
}
