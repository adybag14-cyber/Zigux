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

test "runFixdep preserves angle brackets in saved command line" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/angle_source.c", .{tmp.sub_path});
    defer std.testing.allocator.free(source_path);
    const depfile_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/angle.d", .{tmp.sub_path});
    defer std.testing.allocator.free(depfile_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "angle_source.c",
        .data = "int angle_source = 1;\n",
    });
    const depfile_text = try std.fmt.allocPrint(std.testing.allocator, "angle.o: {s}\n", .{source_path});
    defer std.testing.allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "angle.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const cmdline = "zig cc -DANGLE=<left> -DREDIRECT=>right angle_source.c";
    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "angle.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(std.testing.allocator, "savedcmd_angle.o := {s}\n\n" ++
        "source_angle.o := {s}\n\n" ++
        "deps_angle.o := \\\n" ++
        "\n" ++
        "angle.o: $(deps_angle.o)\n\n" ++
        "$(deps_angle.o):\n", .{ cmdline, source_path });
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
