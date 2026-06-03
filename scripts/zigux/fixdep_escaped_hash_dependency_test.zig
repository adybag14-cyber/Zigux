const std = @import("std");

const fixdep = @import("fixdep.zig");

test "runFixdep deduplicates escaped hash dependencies through the public entry path" {
    const Capture = struct {
        list: std.ArrayList(u8),
        allocator: std.mem.Allocator,

        fn init(allocator: std.mem.Allocator) !@This() {
            return .{
                .list = try std.ArrayList(u8).initCapacity(allocator, 256),
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
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "dep#crate.h",
        .data = "CONFIG_ZIGUX_HASH CONFIG_ZIGUX_HASH_MODULE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "later.rmeta",
        .data = "",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/dep#crate.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(hash_dep_path);

    const escaped_hash_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/dep\\#crate.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(escaped_hash_dep_path);

    const later_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/later.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(later_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s} {s}\n",
        .{ source_path, escaped_hash_dep_path, escaped_hash_dep_path, later_path },
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
        "rustc --emit dep-info=sample.d",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := rustc --emit dep-info=sample.d\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HASH) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, hash_dep_path, later_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
