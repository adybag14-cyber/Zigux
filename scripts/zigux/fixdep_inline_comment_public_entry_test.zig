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

test "runFixdep skips inline comments after real dependencies" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/inline_comment_source.c",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/inline_comment_config.h",
        .{base_path},
    );
    defer std.testing.allocator.free(header_path);

    const so_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/inline_comment_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(so_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/inline_comment.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o inline_comment.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "inline_comment_source.c",
        .data = "int inline_comment_source(void) { return CONFIG_ZIGUX_INLINE_SOURCE; }\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "inline_comment_config.h",
        .data = "#define CONFIG_ZIGUX_INLINE_HEADER_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "inline_comment_dep.so",
        .data = "CONFIG_ZIGUX_INLINE_SO_SHOULD_NOT_PARSE=y\n",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "inline_comment.o: {s} {s} {s} # CONFIG_ZIGUX_INLINE_COMMENT_SHOULD_NOT_PARSE \\\n" ++
            " {s} CONFIG_ZIGUX_CONTINUED_COMMENT_SHOULD_NOT_PARSE\n",
        .{ source_path, header_path, so_path, source_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "inline_comment.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "inline_comment.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_inline_comment.o := {s}\n\n" ++
            "source_inline_comment.o := {s}\n\n" ++
            "deps_inline_comment.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_INLINE_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_INLINE_HEADER) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "inline_comment.o: $(deps_inline_comment.o)\n\n" ++
            "$(deps_inline_comment.o):\n",
        .{ cmdline, source_path, header_path, so_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expectEqual(
        @as(?usize, null),
        std.mem.indexOf(u8, capture.list.items, "INLINE_COMMENT_SHOULD_NOT_PARSE"),
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        std.mem.indexOf(u8, capture.list.items, "CONTINUED_COMMENT_SHOULD_NOT_PARSE"),
    );
    try std.testing.expectEqual(
        @as(?usize, null),
        std.mem.indexOf(u8, capture.list.items, "INLINE_SO_SHOULD_NOT_PARSE"),
    );
}
