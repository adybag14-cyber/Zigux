const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !Capture {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

test "runFixdep ignores depfile bytes after the first embedded NUL" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "source.c",
        .data = "CONFIG_ZIGUX_SOURCE_BEFORE_NUL\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "before-nul.h",
        .data = "CONFIG_ZIGUX_HEADER_BEFORE_NUL\n",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "after-nul.h",
        .data = "CONFIG_ZIGUX_AFTER_NUL_SHOULD_NOT_PARSE\n",
    });

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/source.c",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const before_nul_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/before-nul.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(before_nul_path);

    const after_nul_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/after-nul.h",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(after_nul_path);

    var depfile_bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, 256);
    defer depfile_bytes.deinit(std.testing.allocator);
    const before_nul_dep = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample.o: {s} {s}",
        .{ source_path, before_nul_path },
    );
    defer std.testing.allocator.free(before_nul_dep);
    try depfile_bytes.appendSlice(std.testing.allocator, before_nul_dep);
    try depfile_bytes.append(std.testing.allocator, 0);

    const after_nul_dep = try std.fmt.allocPrint(
        std.testing.allocator,
        "\nsample.o: {s}\n",
        .{after_nul_path},
    );
    defer std.testing.allocator.free(after_nul_dep);
    try depfile_bytes.appendSlice(std.testing.allocator, after_nul_dep);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample.d",
        .data = depfile_bytes.items,
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
        "cc -MD -MF sample.d -c source.c",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample.o := cc -MD -MF sample.d -c source.c\n\n" ++
            "source_sample.o := {s}\n\n" ++
            "deps_sample.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_SOURCE_BEFORE_NUL) \\\n" ++
            "  {s} \\\n" ++
            "    $(wildcard include/config/ZIGUX_HEADER_BEFORE_NUL) \\\n" ++
            "\n" ++
            "sample.o: $(deps_sample.o)\n\n" ++
            "$(deps_sample.o):\n",
        .{ source_path, before_nul_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "after-nul.h") == null);
    try std.testing.expect(std.mem.indexOf(u8, capture.list.items, "ZIGUX_AFTER_NUL_SHOULD_NOT_PARSE") == null);
}
