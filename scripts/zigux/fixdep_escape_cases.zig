const std = @import("std");
const fixdep = @import("./fixdep.zig");

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

test "runFixdep preserves escaped colons in source and dependency tokens" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/escaped-colon.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "escaped-colon.d",
        .data = "sample.o: source\\:crate.rmeta dep\\:one.rmeta dep\\:two.rmeta\n",
    });

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample.o",
        "zig cc -MMD sample.c",
    );

    try std.testing.expectEqualStrings(
        "savedcmd_sample.o := zig cc -MMD sample.c\n\n" ++
            "source_sample.o := source:crate.rmeta\n\n" ++
            "deps_sample.o := \\\n" ++
            "  dep:one.rmeta \\\n" ++
            "  dep:two.rmeta \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        capture.list.items,
    );
}
