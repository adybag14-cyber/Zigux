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

test "runFixdep preserves pipe target names through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "pipe-target.h",
        .data = "CONFIG_ZIGUX_TARGET_PIPE=y\n",
    });

    const target = "module/zigux|target.o";
    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/pipe-target.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s} {s}\n",
        .{ target, source_path, header_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "pipe.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/pipe.d",
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
        target,
        "zig cc -DTARGET_PIPE=1 -c module/source.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_{s} := zig cc -DTARGET_PIPE=1 -c module/source.c\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_PIPE) \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{ target, target, source_path, target, header_path, target, target, target },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
