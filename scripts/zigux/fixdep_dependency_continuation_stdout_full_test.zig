const std = @import("std");
const Io = std.Io;

const fixdep = @import("fixdep.zig");

const fixture_depfile = "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d";
const fixture_stderr = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt";
const target = "sample_dependency_continuation_stdout_full.o";
const cmdline = "clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation_stdout_full.o";

const expected_stdout =
    "savedcmd_sample_dependency_continuation_stdout_full.o := clang -c zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c -o sample_dependency_continuation_stdout_full.o\n\n" ++
    "source_sample_dependency_continuation_stdout_full.o := sample_dependency_continuation_source.rmeta\n\n" ++
    "deps_sample_dependency_continuation_stdout_full.o := \\\n" ++
    "  sample_dependency_continuation_dep_one.so \\\n" ++
    "  sample_dependency_continuation_dep_two.so \\\n" ++
    "  sample_dependency_continuation_dep_three.so \\\n" ++
    "\n" ++
    "sample_dependency_continuation_stdout_full.o: $(deps_sample_dependency_continuation_stdout_full.o)\n\n" ++
    "$(deps_sample_dependency_continuation_stdout_full.o):\n";

const Capture = struct {
    list: std.ArrayList(u8),
    allocator: std.mem.Allocator,

    fn init(allocator: std.mem.Allocator) !@This() {
        return .{
            .list = try std.ArrayList(u8).initCapacity(allocator, 512),
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

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(4096));
}

test "runFixdep replays the dependency-continuation fixture on the stdout-full target" {
    var capture = try Capture.init(std.testing.allocator);
    defer capture.deinit();

    try fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        fixture_depfile,
        target,
        cmdline,
    );
    try capture.flush();

    try std.testing.expectEqualStrings(expected_stdout, capture.list.items);
}

test "fixdep main keeps the shared output-write stderr for the dependency-continuation fixture" {
    const shell_command = try std.fmt.allocPrint(
        std.testing.allocator,
        "zig run scripts/zigux/fixdep.zig -- {s} {s} '{s}' >/dev/full",
        .{ fixture_depfile, target, cmdline },
    );
    defer std.testing.allocator.free(shell_command);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{ "bash", "-lc", shell_command },
        .cwd = .{ .path = "." },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    switch (result.term) {
        .exited => |code| try std.testing.expectEqual(@as(u8, 1), code),
        else => return error.UnexpectedTerm,
    }

    const expected_stderr = try readFixture(std.testing.allocator, fixture_stderr);
    defer std.testing.allocator.free(expected_stderr);

    try std.testing.expectEqualStrings("", result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}
