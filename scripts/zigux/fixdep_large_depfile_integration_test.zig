const std = @import("std");
const fixdep = @import("fixdep.zig");

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator, capacity: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, capacity),
            .allocator = allocator,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) !void {
        const rendered = try std.fmt.allocPrint(self.allocator, fmt, args);
        defer std.testing.allocator.free(rendered);
        try self.list.appendSlice(self.allocator, rendered);
    }

    pub fn flush(_: *@This()) !void {}
};

fn tmpBasePath(tmp: anytype) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
}

test "runFixdep keeps later dependencies after the legacy one mebibyte ceiling" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_large_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const first_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/dep-first.so",
        .{base_path},
    );
    defer std.testing.allocator.free(first_dep_path);

    const ignored_source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/ignored-source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(ignored_source_path);

    const later_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/later-dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(later_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_large_depfile.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_large_depfile.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    var depfile_bytes = try std.ArrayList(u8).initCapacity(std.testing.allocator, (1024 * 1024) + 512);
    defer depfile_bytes.deinit(std.testing.allocator);

    const header = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_large_depfile.o: {s} {s} \\\n",
        .{ source_path, first_dep_path },
    );
    defer std.testing.allocator.free(header);
    try depfile_bytes.appendSlice(std.testing.allocator, header);
    try depfile_bytes.appendSlice(std.testing.allocator, "# ");
    try depfile_bytes.appendNTimes(std.testing.allocator, 'a', (1024 * 1024) + 64);
    try depfile_bytes.append(std.testing.allocator, '\n');
    const tail = try std.fmt.allocPrint(
        std.testing.allocator,
        "module/sample_large_depfile.o: {s} {s}\n",
        .{ ignored_source_path, later_dep_path },
    );
    defer std.testing.allocator.free(tail);
    try depfile_bytes.appendSlice(std.testing.allocator, tail);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_large_depfile.d",
        .data = depfile_bytes.items,
    });

    var capture = try Capture.init(std.testing.allocator, 1024);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_large_depfile.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_large_depfile.o := {s}\n\n" ++
            "source_sample_large_depfile.o := {s}\n\n" ++
            "deps_sample_large_depfile.o := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_large_depfile.o: $(deps_sample_large_depfile.o)\n\n" ++
            "$(deps_sample_large_depfile.o):\n",
        .{ cmdline, source_path, first_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
