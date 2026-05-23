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

fn runFixdepReplay(
    depfile_name: []const u8,
    depfile_contents: []const u8,
    target: []const u8,
    cmdline: []const u8,
) !Capture {
    var tmp = std.testing.tmpDir(.{});
    errdefer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = depfile_contents,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path[0..], depfile_name },
    );
    defer std.testing.allocator.free(depfile_path);

    var capture = try Capture.init(std.testing.allocator);
    errdefer capture.deinit();

    fixdep.runFixdep(
        std.testing.allocator,
        std.testing.io,
        &capture,
        depfile_path,
        target,
        cmdline,
    ) catch |err| {
        tmp.cleanup();
        return err;
    };

    tmp.cleanup();
    return capture;
}

fn expectFixdepReplay(
    depfile_name: []const u8,
    depfile_contents: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_output: []const u8,
) !void {
    var capture = try runFixdepReplay(depfile_name, depfile_contents, target, cmdline);
    defer capture.deinit();

    try std.testing.expectEqualStrings(expected_output, capture.list.items);
}

fn zigExecutable(allocator: std.mem.Allocator) ![]const u8 {
    return std.testing.environ.getAlloc(allocator, "ZIG") catch |err| switch (err) {
        error.EnvironmentVariableMissing => try allocator.dupe(u8, "zig"),
        else => return err,
    };
}

fn expectFixdepMainReplayError(
    depfile_name: []const u8,
    depfile_contents: []const u8,
    target: []const u8,
    cmdline: []const u8,
    expected_exit_code: u8,
    expected_output: []const u8,
    expected_stderr: []const u8,
) !void {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = depfile_contents,
    });

    const depfile_path = try std.fmt.allocPrint(
        std.testing.allocator,
        ".zig-cache/tmp/{s}/{s}",
        .{ tmp.sub_path[0..], depfile_name },
    );
    defer std.testing.allocator.free(depfile_path);

    const zig_cmd = try zigExecutable(std.testing.allocator);
    defer std.testing.allocator.free(zig_cmd);

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            zig_cmd,
            "run",
            "scripts/zigux/fixdep.zig",
            "--",
            depfile_path,
            target,
            cmdline,
        },
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try std.testing.expectEqual(std.process.Child.Term{ .exited = expected_exit_code }, result.term);
    try std.testing.expectEqualStrings(expected_output, result.stdout);
    try std.testing.expectEqualStrings(expected_stderr, result.stderr);
}

test "fixdep fixture replay keeps ignored autoconf hops out of widened escaped-space fixtures" {
    try expectFixdepReplay(
        "sample_escaped_space.d",
        "sample_escaped_space.o: zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\ name.rmeta \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\ name.rmeta\n",
        "sample_escaped_space.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o",
        "savedcmd_sample_escaped_space.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_space_source.c -o sample_escaped_space.o\n\n" ++
            "source_sample_escaped_space.o := zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta\n\n" ++
            "deps_sample_escaped_space.o := \\\n" ++
            "  zigux/tests/fixtures/fixdep/dep\\ name.rmeta \\\n" ++
            "\n" ++
            "sample_escaped_space.o: $(deps_sample_escaped_space.o)\n\n" ++
            "$(deps_sample_escaped_space.o):\n",
    );
}

test "fixdep fixture replay keeps escaped colons literal across widened repeated dependency tails" {
    try expectFixdepReplay(
        "sample_escaped_colon.d",
        "sample_escaped_colon.o: zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\:colon.so \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/dep\\:colon.so\n",
        "sample_escaped_colon.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o",
        "savedcmd_sample_escaped_colon.o := clang -c zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c -o sample_escaped_colon.o\n\n" ++
            "source_sample_escaped_colon.o := zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta\n\n" ++
            "deps_sample_escaped_colon.o := \\\n" ++
            "  zigux/tests/fixtures/fixdep/dep:colon.so \\\n" ++
            "\n" ++
            "sample_escaped_colon.o: $(deps_sample_escaped_colon.o)\n\n" ++
            "$(deps_sample_escaped_colon.o):\n",
    );
}

test "fixdep fixture replay keeps the first source across widened concatenated target tails" {
    try expectFixdepReplay(
        "sample_concatenated.d",
        "sample_concatenated.o: zigux/tests/fixtures/fixdep/sample_concatenated_source.c zigux/tests/fixtures/fixdep/sample_concatenated_dep.h \\\n" ++
            "# generated by rustc\\\\\n" ++
            "  still comment\n" ++
            "module/sample_concatenated.o: zigux/tests/fixtures/fixdep/sample_concatenated_temp.c zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h",
        "sample_concatenated.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o",
        "savedcmd_sample_concatenated.o := clang -c zigux/tests/fixtures/fixdep/sample_concatenated_source.c -o sample_concatenated.o\n\n" ++
            "source_sample_concatenated.o := zigux/tests/fixtures/fixdep/sample_concatenated_source.c\n\n" ++
            "deps_sample_concatenated.o := \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_SOURCE) \\\n" ++
            "  zigux/tests/fixtures/fixdep/sample_concatenated_dep.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_HEADER) \\\n" ++
            "  zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h \\\n" ++
            "    $(wildcard include/config/ZIGUX_DT_SECONDARY) \\\n" ++
            "\n" ++
            "sample_concatenated.o: $(deps_sample_concatenated.o)\n\n" ++
            "$(deps_sample_concatenated.o):\n",
    );
}

test "fixdep fixture replay keeps partial stdout before widened missing dependency tails" {
    try expectFixdepMainReplayError(
        "sample_missing_dep.d",
        "sample_missing_dep.o: zigux/tests/fixtures/fixdep/sample_missing_dep_source.c \\\n" ++
            " include/generated/autoconf.h \\\n" ++
            " zigux/tests/fixtures/fixdep/sample_missing_dep.h \\\n" ++
            " zigux/tests/fixtures/fixdep/sample_missing_dep.h",
        "sample_missing_dep.o",
        "clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o",
        2,
        "savedcmd_sample_missing_dep.o := clang -c zigux/tests/fixtures/fixdep/sample_missing_dep_source.c -o sample_missing_dep.o\n\n" ++
            "source_sample_missing_dep.o := zigux/tests/fixtures/fixdep/sample_missing_dep_source.c\n\n" ++
            "deps_sample_missing_dep.o := \\\n" ++
            "    $(wildcard include/config/MISSING_SOURCE) \\\n" ++
            "  zigux/tests/fixtures/fixdep/sample_missing_dep.h \\\n",
        "fixdep: error opening file: zigux/tests/fixtures/fixdep/sample_missing_dep.h: No such file or directory\n",
    );
}

test "fixdep fixture replay preserves double-backslash comment failure prefixes while widening tails" {
    try expectFixdepMainReplayError(
        "sample_double_backslash_comment.d",
        "sample_double_backslash_comment.o: zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta zigux/tests/fixtures/fixdep/missing\\\\#dep.h \\\n" ++
            "# generated by rustc\\\\\n" ++
            "  include/generated/autoconf.h zigux/tests/fixtures/fixdep/dep\\ name.rmeta",
        "sample_double_backslash_comment.o",
        "rustc --emit dep-info=sample_double_backslash_comment.d",
        2,
        "savedcmd_sample_double_backslash_comment.o := rustc --emit dep-info=sample_double_backslash_comment.d\n\n" ++
            "source_sample_double_backslash_comment.o := zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta\n\n" ++
            "deps_sample_double_backslash_comment.o := \\\n" ++
            "  zigux/tests/fixtures/fixdep/missing\\\\ \\\n",
        "fixdep: error opening file: zigux/tests/fixtures/fixdep/missing\\\\: No such file or directory\n",
    );
}
