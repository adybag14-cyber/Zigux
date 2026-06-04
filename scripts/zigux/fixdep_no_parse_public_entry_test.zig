const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep emits no-parse dependencies without scanning their config payloads" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 320),
                .allocator = allocator,
            };
        }

        pub fn deinit(self: *@This()) void {
            self.list.deinit(self.allocator);
        }

        pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
            const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
            defer self.allocator.free(rendered);
            try self.list.appendSlice(self.allocator, rendered);
        }

        pub fn flush(_: *@This()) !void {}
    };

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.c",
        .data = "CONFIG_ZIGUX_SOURCE CONFIG_ZIGUX_SHARED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "opaque.so",
        .data = "CONFIG_ZIGUX_SO_SHOULD_NOT_PARSE CONFIG_ZIGUX_SHARED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "opaque.rmeta",
        .data = "CONFIG_ZIGUX_RMETA_SHOULD_NOT_PARSE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "ordinary.h",
        .data = "CONFIG_ZIGUX_HEADER CONFIG_ZIGUX_SHARED\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const so_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/opaque.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(so_path);

    const rmeta_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/opaque.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(rmeta_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/ordinary.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s} {s}\n",
        .{ source_path, so_path, rmeta_path, header_path },
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
        "cc -Wp,-MMD,sample.d -c source.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := cc -Wp,-MMD,sample.d -c source.c\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_SOURCE) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HEADER) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, so_path, rmeta_path, header_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SO_SHOULD_NOT_PARSE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "RMETA_SHOULD_NOT_PARSE") == null);
}
