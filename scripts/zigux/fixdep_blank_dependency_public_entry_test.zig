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

test "runFixdep skips blank dependency continuation lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "visible.h",
        .data = "#define CONFIG_ZIGUX_BLANK_CONTINUATION_VISIBLE_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sentinel.so",
        .data = "CONFIG_ZIGUX_BLANK_CONTINUATION_SO_SHOULD_NOT_PARSE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/visible.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const sentinel_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/sentinel.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(sentinel_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} \\\n" ++
            "    \\\n" ++
            "  {s} \\\n" ++
            "\t\\\n" ++
            "  {s}\n",
        .{ source_path, header_path, sentinel_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/sample.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample.o",
        "cc -c source.c -o sample.o",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := cc -c source.c -o sample.o\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_BLANK_CONTINUATION_VISIBLE) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, header_path, sentinel_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_BLANK_CONTINUATION_VISIBLE_MODULE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_BLANK_CONTINUATION_SO_SHOULD_NOT_PARSE") == null);
}
