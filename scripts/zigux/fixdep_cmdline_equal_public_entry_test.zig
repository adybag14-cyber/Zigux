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

test "runFixdep preserves equal signs in saved command line" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/equal_source.c", .{tmp.sub_path});
    defer std.testing.allocator.free(source_path);
    const depfile_path = try std.fmt.allocPrint(std.testing.allocator, ".zig-cache/tmp/{s}/equal.d", .{tmp.sub_path});
    defer std.testing.allocator.free(depfile_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "equal_source.c",
        .data = "int equal_source = 1;\n",
    });
    const depfile_text = try std.fmt.allocPrint(std.testing.allocator, "equal.o: {s}\n", .{source_path});
    defer std.testing.allocator.free(depfile_text);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "equal.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    const cmdline = "zig cc -DNAME=zigux -DVALUE=with=equals -c equal_source.c";
    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "equal.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(std.testing.allocator, "savedcmd_equal.o := {s}\n\n" ++
        "source_equal.o := {s}\n\n" ++
        "deps_equal.o := \\\n" ++
        "\n" ++
        "equal.o: $(deps_equal.o)\n\n" ++
        "$(deps_equal.o):\n", .{ cmdline, source_path });
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
