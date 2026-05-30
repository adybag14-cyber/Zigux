const std = @import("std");
const fixdep = @import("fixdep");

test "lane11 public fixdep entry ignores autoconf dependency contents" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 384),
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
        .sub_path = "source.rmeta",
        .data = "CONFIG_ZIGUX_SOURCE_SHOULD_NOT_PARSE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "config_dep.h",
        .data = "#define CONFIG_ZIGUX_HEADER 1\n#define CONFIG_ZIGUX_DUP_MODULE 1\n",
    });
    _ = try tmp.dir.createDirPathStatus(std.testing.io, "include/generated", .default_dir);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "include/generated/autoconf.h",
        .data = "#define CONFIG_ZIGUX_AUTOCONF_SHOULD_NOT_PARSE 1\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const config_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/config_dep.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(config_path);

    const autoconf_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/include/generated/autoconf.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(autoconf_path);

    const tail_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/tail.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(tail_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s} {s}\n",
        .{ source_path, config_path, autoconf_path, tail_path },
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
        "cc -c sample.c -o sample.o",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := cc -c sample.c -o sample.o\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HEADER) \\\n" ++
            "    $(wildcard include/config/ZIGUX_DUP) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, config_path, tail_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "autoconf") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "AUTOCONF_SHOULD_NOT_PARSE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SOURCE_SHOULD_NOT_PARSE") == null);
}
