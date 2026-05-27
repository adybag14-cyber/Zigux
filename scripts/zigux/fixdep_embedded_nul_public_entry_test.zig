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
        defer self.allocator.free(rendered);
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

test "runFixdep ignores bytes after the first embedded NUL" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try tmpBasePath(tmp);
    defer std.testing.allocator.free(base_path);

    const visible_source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/visible_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(visible_source_path);

    const visible_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/visible_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(visible_dep_path);

    const hidden_source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/hidden_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(hidden_source_path);

    const hidden_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/hidden_dep.so",
        .{base_path},
    );
    defer std.testing.allocator.free(hidden_dep_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_embedded_nul.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const cmdline = try std.fmt.allocPrint(
        std.testing.allocator,
        "clang -c {s} -o sample_embedded_nul.o",
        .{visible_source_path},
    );
    defer std.testing.allocator.free(cmdline);

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_embedded_nul.o: {s} {s}\x00sample_embedded_nul.o: {s} {s}\n",
        .{ visible_source_path, visible_dep_path, hidden_source_path, hidden_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_embedded_nul.d",
        .data = depfile_text,
    });

    var capture = try Capture.init(std.testing.allocator, 512);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        "sample_embedded_nul.o",
        cmdline,
    );

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_embedded_nul.o := {s}\n\n" ++
            "source_sample_embedded_nul.o := {s}\n\n" ++
            "deps_sample_embedded_nul.o := \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "sample_embedded_nul.o: $(deps_sample_embedded_nul.o)\n\n" ++
            "$(deps_sample_embedded_nul.o):\n",
        .{ cmdline, visible_source_path, visible_dep_path },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, capture.list.items);
}
