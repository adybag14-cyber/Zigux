const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 96),
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

test "runFixdep reports NoTargets for comment-only depfiles through the public entry path" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "comment-only.d",
        .data = "# generated dependency file\n# CONFIG_ZIGUX_COMMENT_ONLY must stay ignored\n\n",
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/comment-only.d",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try std.testing.expectError(
        error.NoTargets,
        fixdep.runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_path,
            "comment-only.o",
            "cc -MD -MF comment-only.d -c source.c",
        ),
    );

    try std.testing.expectEqualStrings(
        "savedcmd_comment-only.o := cc -MD -MF comment-only.d -c source.c\n\n",
        capture.list.items,
    );
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_COMMENT_ONLY") == null);
}
