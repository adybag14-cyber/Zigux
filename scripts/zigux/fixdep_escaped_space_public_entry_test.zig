const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep.zig");

test "runFixdep preserves escaped-space dependencies through the public entry path" {
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

    const depfile_path = "zigux_fixdep_escaped_space_public_entry.d";
    const source_path = "zigux_fixdep_escaped\\ source.rmeta";
    const header_path = "zigux_fixdep_escaped\\ header.h";
    const no_parse_path = "zigux_fixdep_escaped\\ no_parse.so";

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = source_path,
        .data = "CONFIG_ZIGUX_ESCAPED_SOURCE_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, source_path) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = header_path,
        .data = "#define CONFIG_ZIGUX_ESCAPED_HEADER 1\n#define CONFIG_ZIGUX_ESCAPED_HEADER_MODULE 1\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, header_path) catch {};

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = no_parse_path,
        .data = "CONFIG_ZIGUX_ESCAPED_SO_SHOULD_NOT_PARSE\n",
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, no_parse_path) catch {};

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s} {s} {s}\n",
        .{ source_path, header_path, header_path, no_parse_path },
    );
    defer std.testing.allocator.free(depfile_bytes);

    try Io.Dir.cwd().writeFile(std.testing.io, .{
        .sub_path = depfile_path,
        .data = depfile_bytes,
    });
    defer Io.Dir.cwd().deleteFile(std.testing.io, depfile_path) catch {};

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
            "    $(wildcard include/config/ZIGUX_ESCAPED_HEADER) \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, header_path, no_parse_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ESCAPED_SOURCE_SHOULD_NOT_PARSE") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ESCAPED_SO_SHOULD_NOT_PARSE") == null);
}
