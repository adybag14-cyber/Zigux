const std = @import("std");
const fixdep = @import("fixdep.zig");

const FailingCapture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,
    fail_after: usize,

    fn init(allocator: std.mem.Allocator, fail_after: usize) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, fail_after + 64),
            .allocator = allocator,
            .fail_after = fail_after,
        };
    }

    fn deinit(self: *@This()) void {
        self.list.deinit(self.allocator);
    }

    pub fn print(self: *@This(), comptime fmt: []const u8, args: anytype) error{OutputWrite}!void {
        const rendered = std.fmt.allocPrint(self.allocator, fmt, args) catch return error.OutputWrite;
        defer self.allocator.free(rendered);

        const remaining = self.fail_after -| self.list.items.len;
        const writable = @min(remaining, rendered.len);
        self.list.appendSlice(self.allocator, rendered[0..writable]) catch return error.OutputWrite;
        if (writable != rendered.len) {
            return error.OutputWrite;
        }
    }

    pub fn flush(_: *@This()) !void {}
};

test "runFixdep keeps the escaped-space prelude before output write failures" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_space_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_space.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const escaped_dep_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/dep\\ name.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_dep_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_space_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "dep name.rmeta",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_space_stdout_full.o: {s} {s}\n",
        .{ source_path, escaped_dep_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_space.d",
        .data = depfile_text,
    });

    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space_stdout_full.o";
    const expected_prefix = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_space_stdout_full.o := {s}\n\n" ++
            "source_sample_escaped_space_stdout_full.o := {s}\n\n" ++
            "deps_sample_escaped_space_stdout_full.o := \\\n" ++
            "  {s} \\\n",
        .{ cmdline, source_path, escaped_dep_path },
    );
    defer std.testing.allocator.free(expected_prefix);

    var capture = try FailingCapture.init(std.testing.allocator, expected_prefix.len);
    defer capture.deinit();

    try std.testing.expectError(
        error.OutputWrite,
        fixdep.runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_path,
            "sample_escaped_space_stdout_full.o",
            cmdline,
        ),
    );
    try std.testing.expectEqualStrings(expected_prefix, capture.list.items);
}

test "runFixdep keeps the escaped-colon prelude before output write failures" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const base_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}",
        .{tmp.sub_path[0..]},
    );
    defer std.testing.allocator.free(base_path);

    const source_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_colon_source.rmeta",
        .{base_path},
    );
    defer std.testing.allocator.free(source_path);

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/sample_escaped_colon.d",
        .{base_path},
    );
    defer std.testing.allocator.free(depfile_path);

    const escaped_depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/dep\\:colon.so",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_depfile_path);

    const escaped_visible_path = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}/dep:colon.so",
        .{base_path},
    );
    defer std.testing.allocator.free(escaped_visible_path);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_colon_source.rmeta",
        .data = "",
    });
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "dep:colon.so",
        .data = "",
    });

    const depfile_text = try std.fmt.allocPrint(
        std.testing.allocator,
        "sample_escaped_colon_stdout_full.o: {s} {s}\n",
        .{ source_path, escaped_depfile_path },
    );
    defer std.testing.allocator.free(depfile_text);

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = "sample_escaped_colon.d",
        .data = depfile_text,
    });

    const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon_stdout_full.o";
    const expected_prefix = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_sample_escaped_colon_stdout_full.o := {s}\n\n" ++
            "source_sample_escaped_colon_stdout_full.o := {s}\n\n" ++
            "deps_sample_escaped_colon_stdout_full.o := \\\n" ++
            "  {s} \\\n",
        .{ cmdline, source_path, escaped_visible_path },
    );
    defer std.testing.allocator.free(expected_prefix);

    var capture = try FailingCapture.init(std.testing.allocator, expected_prefix.len);
    defer capture.deinit();

    try std.testing.expectError(
        error.OutputWrite,
        fixdep.runFixdep(
            std.testing.allocator,
            std.testing.io,
            &capture,
            depfile_path,
            "sample_escaped_colon_stdout_full.o",
            cmdline,
        ),
    );
    try std.testing.expectEqualStrings(expected_prefix, capture.list.items);
}
