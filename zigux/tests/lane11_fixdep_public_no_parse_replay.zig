const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep");

test "fixdep public entry keeps Rust no-parse deps while scanning normal headers" {
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

    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.rmeta",
        .data = "CONFIG_ZIGUX_SOURCE_SHOULD_NOT_BE_SCANNED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "artifact.so",
        .data = "CONFIG_ZIGUX_SO_SHOULD_NOT_BE_SCANNED\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "normal.h",
        .data = "CONFIG_ZIGUX_NORMAL_HEADER CONFIG_ZIGUX_NORMAL_HEADER_MODULE\n",
    });

    const root = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(root);

    const source_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/source.rmeta", .{root});
    defer std.testing.allocator.free(source_path);
    const so_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/artifact.so", .{root});
    defer std.testing.allocator.free(so_path);
    const header_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/normal.h", .{root});
    defer std.testing.allocator.free(header_path);
    const depfile_path = try std.fmt.allocPrint(std.testing.allocator, "{s}/sample.d", .{root});
    defer std.testing.allocator.free(depfile_path);

    const depfile = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s}\n",
        .{ source_path, so_path, header_path },
    );
    defer std.testing.allocator.free(depfile);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.d",
        .data = depfile,
    });

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
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_NORMAL_HEADER) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, so_path, header_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SOURCE_SHOULD_NOT_BE_SCANNED") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "SO_SHOULD_NOT_BE_SCANNED") == null);
}
