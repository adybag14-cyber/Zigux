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

test "runFixdep keeps bare carriage-return escapes from continuing dependency lines" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_bare_cr_source.rmeta",
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
        "{s}/sample_bare_cr_escape.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_bare_cr_escape.o",
        .{source_path},
    );
    defer std.testing.allocator.free(cmdline);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_bare_cr_escape.o: {s} {s} \\\rmodule/sample_bare_cr_escape.o: {s} {s}\r",
        .{ source_path, first_dep_path, ignored_source_path, later_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_bare_cr_escape.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_bare_cr_escape.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_bare_cr_escape.o := {s}\n\n" ++
            "source_sample_bare_cr_escape.o := {s}\n\n" ++
            "deps_sample_bare_cr_escape.o := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_bare_cr_escape.o: $(deps_sample_bare_cr_escape.o)\n\n" ++
            "$(deps_sample_bare_cr_escape.o):\n",
        .{ cmdline, source_path, first_dep_path, later_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
