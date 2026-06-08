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

test "runFixdep preserves dot target through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "target.dot.source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "target.dot.config.h",
        .data = "CONFIG_ZIGUX_TARGET_DOT CONFIG_ZIGUX_TARGET_SHARED\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/target.dot.source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/target.dot.config.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "discarded.o: {s} {s}\n",
        .{ source_path, config_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "target.dot.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/target.dot.d",
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
        "zigux.target.dot.o",
        "cc -MD -MF target.dot.d -c target.dot.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_zigux.target.dot.o := cc -MD -MF target.dot.d -c target.dot.c\n\n" ++
            "source_zigux.target.dot.o := {s}\n\n" ++
            "deps_zigux.target.dot.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_DOT) \\\n" ++
            "    $(wildcard include/config/ZIGUX_TARGET_SHARED) \\\n" ++
            "\n" ++
            "zigux.target.dot.o: $(deps_zigux.target.dot.o)\n\n" ++
            "$(deps_zigux.target.dot.o):\n",
        .{ source_path, config_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
