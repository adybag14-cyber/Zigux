const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 384),
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

test "runFixdep treats a no-parse source as emitted but not scanned" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.rlib",
        .data = "CONFIG_ZIGUX_RLIB_SOURCE_SHOULD_NOT_PARSE\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "visible.h",
        .data = "CONFIG_ZIGUX_SOURCE_NO_PARSE_HEADER CONFIG_ZIGUX_SOURCE_NO_PARSE_SHARED\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.rlib",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const header_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/visible.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(header_path);

    const depfile_bytes = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s}\n",
        .{ source_path, header_path },
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
        "rustc --crate-type rlib --emit dep-info=sample.d",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := rustc --crate-type rlib --emit dep-info=sample.d\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_SOURCE_NO_PARSE_HEADER) \\\n" ++
            "    $(wildcard include/config/ZIGUX_SOURCE_NO_PARSE_SHARED) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, header_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "RLIB_SOURCE_SHOULD_NOT_PARSE") == null);
}
