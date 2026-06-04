const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep preserves absolute dependency paths through the public entry path" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        pub fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 384),
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
        .sub_path = "absolute_source.c",
        .data = "CONFIG_ZIGUX_ABSOLUTE_SOURCE CONFIG_ZIGUX_ABSOLUTE_SHARED_MODULE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "absolute_header.h",
        .data = "CONFIG_ZIGUX_ABSOLUTE_HEADER CONFIG_ZIGUX_ABSOLUTE_SHARED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "absolute_payload.so",
        .data = "CONFIG_ZIGUX_ABSOLUTE_SO_SHOULD_NOT_PARSE\n",
    });

    const tmp_root = try std.fmt.allocPrint(
        std.testing.allocator,
        "/proc/self/cwd/.zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(tmp_root);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/absolute_source.c",
        .{tmp_root},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/absolute_header.h",
        .{tmp_root},
    );
    defer std.testing.allocator.free(header_path);

    const so_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/absolute_payload.so",
        .{tmp_root},
    );
    defer std.testing.allocator.free(so_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/absolute_sample.d",
        .{tmp_root},
    );
    defer std.testing.allocator.free(depfile_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "absolute_sample.o: {s} {s} {s}\n",
        .{ source_path, header_path, so_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "absolute_sample.d",
        .data = depfile_bytes,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "absolute_sample.o",
        "cc -Wp,-MMD,absolute_sample.d -c absolute_source.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_absolute_sample.o := cc -Wp,-MMD,absolute_sample.d -c absolute_source.c\n\n" ++
            "source_absolute_sample.o := {s}\n\n" ++
            "deps_absolute_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_ABSOLUTE_SOURCE) \\\n" ++
            "    $(wildcard include/config/ZIGUX_ABSOLUTE_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_ABSOLUTE_HEADER) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "absolute_sample.o: $(deps_absolute_sample.o)\n\n" ++
            "$(deps_absolute_sample.o):\n",
        .{ source_path, header_path, so_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SO_SHOULD_NOT_PARSE") == null);
}
