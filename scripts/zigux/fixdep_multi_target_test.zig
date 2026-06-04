const std = @import("std");
const fixdep = @import("fixdep.zig");

test "runFixdep keeps requested target separate from depfile target names" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 320),
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

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.c",
        .data = "/* CONFIG_ZIGUX_MULTI_SOURCE_MODULE */\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "hash#dep.h",
        .data = "#define CONFIG_ZIGUX_HASH_DEP 1\n#define CONFIG_ZIGUX_SHARED_MODULE 1\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "libzigux.so",
        .data = "CONFIG_ZIGUX_SO_SHOULD_NOT_PARSE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/hash#dep.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(hash_dep_path);

    const escaped_hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/hash\\#dep.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(escaped_hash_dep_path);

    const no_parse_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/libzigux.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(no_parse_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "depfile-first.o depfile-second.o: {s} {s} {s}\n",
        .{ source_path, escaped_hash_dep_path, no_parse_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "multi-target.d",
        .data = depfile_bytes,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/multi-target.d",
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
        "requested-target.o",
        "cc -c source.c -o requested-target.o",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_requested-target.o := cc -c source.c -o requested-target.o\n\n" ++
            "source_requested-target.o := {s}\n\n" ++
            "deps_requested-target.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_MULTI_SOURCE) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH_DEP) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SHARED) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "requested-target.o: $(deps_requested-target.o)\n\n" ++
            "$(deps_requested-target.o):\n",
        .{ source_path, hash_dep_path, no_parse_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "depfile-first.o") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "depfile-second.o") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SO_SHOULD_NOT_PARSE") == null);
}
