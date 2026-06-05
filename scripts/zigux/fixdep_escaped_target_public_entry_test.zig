const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep ignores escaped depfile target names through the public entry path" {
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
        .sub_path = "escaped_target_source.c",
        .data = "CONFIG_ZIGUX_ESCAPED_TARGET_SOURCE CONFIG_ZIGUX_ESCAPED_TARGET_SHARED_MODULE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped_target_header.h",
        .data = "CONFIG_ZIGUX_ESCAPED_TARGET_HEADER CONFIG_ZIGUX_ESCAPED_TARGET_SHARED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped_target_payload.so",
        .data = "CONFIG_ZIGUX_ESCAPED_TARGET_SO_SHOULD_NOT_PARSE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/escaped_target_source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/escaped_target_header.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const so_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/escaped_target_payload.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(so_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "module/escaped\\ target.o module/other\\:target.o: {s} {s} {s}\n",
        .{ source_path, header_path, so_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped_target.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/escaped_target.d",
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
        "requested/target.o",
        "cc -Wp,-MMD,escaped_target.d -c escaped_target_source.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_requested/target.o := cc -Wp,-MMD,escaped_target.d -c escaped_target_source.c\n\n" ++
            "source_requested/target.o := {s}\n\n" ++
            "deps_requested/target.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_TARGET_SOURCE) \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_TARGET_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_ESCAPED_TARGET_HEADER) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "requested/target.o: $(deps_requested/target.o)\n\n" ++
            "$(deps_requested/target.o):\n",
        .{ source_path, header_path, so_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "module/escaped") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SO_SHOULD_NOT_PARSE") == null);
}
