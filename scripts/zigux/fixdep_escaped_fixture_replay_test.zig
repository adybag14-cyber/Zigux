const std = @import("std");
const fixdep = @import("fixdep.zig");

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

fn writeDepfile(tmp: std.testing.TmpDir, sub_path: []const u8, data: []const u8) ![]u8 {
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = sub_path,
        .data = data,
    });
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path[0..], sub_path },
    );
}

test "runFixdep replays the escaped-space fixture packet" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/sample_escaped_space_source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/dep\\ name.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(dep_path);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_space.o: {s} {s}\n",
        .{ source_path, dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    const depfile_path = try writeDepfile(tmp, "sample_escaped_space.d", depfile_text);
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_escaped_space.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_space.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o\n\n" ++
            "source_sample_escaped_space.o := {s}\n\n" ++
            "deps_sample_escaped_space.o := \\\n" ++
            "  {s} \\\n\n" ++
            "sample_escaped_space.o: $(deps_sample_escaped_space.o)\n\n" ++
            "$(deps_sample_escaped_space.o):\n",
        .{ source_path, dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}

test "runFixdep replays the escaped-colon fixture packet" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/sample_escaped_colon_source.rmeta",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(source_path);

    const dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/dep:colon.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(dep_path);

    const depfile_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/dep\\:colon.so",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(depfile_dep_path);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_colon.o: {s} {s}\n",
        .{ source_path, depfile_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    const depfile_path = try writeDepfile(tmp, "sample_escaped_colon.d", depfile_text);
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_escaped_colon.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_colon.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o\n\n" ++
            "source_sample_escaped_colon.o := {s}\n\n" ++
            "deps_sample_escaped_colon.o := \\\n" ++
            "  {s} \\\n\n" ++
            "sample_escaped_colon.o: $(deps_sample_escaped_colon.o)\n\n" ++
            "$(deps_sample_escaped_colon.o):\n",
        .{ source_path, dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
