const std = @import("std");

fn expectExit(term: std.process.Child.Term, expected_code: u8) !void {
    switch (term) {
        .exited => |code| try std.testing.expectEqual(expected_code, code),
        else => return error.UnexpectedChildTermination,
    }
}

fn cacheTmpPath(allocator: std.mem.Allocator, tmp_sub_path: []const u8, name: []const u8) ![]u8 {
    return std.fs.path.join(allocator, &.{
        ".zig-cache",
        "tmp",
        tmp_sub_path,
        name,
    });
}

fn escapeWhitespacePath(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var escaped = try std.ArrayList(u8).initCapacity(allocator, path.len + 8);
    defer escaped.deinit(allocator);

    for (path) |byte| {
        switch (byte) {
            ' ', '\t' => {
                try escaped.append(allocator, '\\');
                try escaped.append(allocator, byte);
            },
            else => try escaped.append(allocator, byte),
        }
    }

    return escaped.toOwnedSlice(allocator);
}

test "fixdep public entry preserves escaped whitespace paths" {
    var tmp = std.testing.tmpDir(.{});
    defer tmp.cleanup();

    const depfile_name = "escaped_whitespace.d";
    const target_name = "sample.o";
    const source_name = "source with space.rmeta";
    const space_dep_name = "dep with space.so";
    const tab_dep_name = "dep\twith\ttab.rmeta";

    const depfile_path = try cacheTmpPath(std.testing.allocator, tmp.sub_path[0..], depfile_name);
    defer std.testing.allocator.free(depfile_path);
    const source_path = try cacheTmpPath(std.testing.allocator, tmp.sub_path[0..], source_name);
    defer std.testing.allocator.free(source_path);
    const space_dep_path = try cacheTmpPath(std.testing.allocator, tmp.sub_path[0..], space_dep_name);
    defer std.testing.allocator.free(space_dep_path);
    const tab_dep_path = try cacheTmpPath(std.testing.allocator, tmp.sub_path[0..], tab_dep_name);
    defer std.testing.allocator.free(tab_dep_path);

    const escaped_source_path = try escapeWhitespacePath(std.testing.allocator, source_path);
    defer std.testing.allocator.free(escaped_source_path);
    const escaped_space_dep_path = try escapeWhitespacePath(std.testing.allocator, space_dep_path);
    defer std.testing.allocator.free(escaped_space_dep_path);
    const escaped_tab_dep_path = try escapeWhitespacePath(std.testing.allocator, tab_dep_path);
    defer std.testing.allocator.free(escaped_tab_dep_path);

    const depfile_data = try std.fmt.allocPrint(
        std.testing.allocator,
        "{s}: {s} {s} {s}\n",
        .{ target_name, escaped_source_path, escaped_space_dep_path, escaped_tab_dep_path },
    );
    defer std.testing.allocator.free(depfile_data);
    try tmp.dir.writeFile(std.testing.io, .{
        .sub_path = depfile_name,
        .data = depfile_data,
    });

    const result = try std.process.run(std.testing.allocator, std.testing.io, .{
        .argv = &.{
            "zig",
            "run",
            "fixdep.zig",
            "--",
            depfile_path,
            target_name,
            "cc -MMD -MF escaped_whitespace.d -c source.c",
        },
        .stdout_limit = .limited(4096),
        .stderr_limit = .limited(4096),
    });
    defer std.testing.allocator.free(result.stdout);
    defer std.testing.allocator.free(result.stderr);

    try expectExit(result.term, 0);
    try std.testing.expectEqualStrings("", result.stderr);

    const expected = try std.fmt.allocPrint(
        std.testing.allocator,
        "savedcmd_{s} := cc -MMD -MF escaped_whitespace.d -c source.c\n\n" ++
            "source_{s} := {s}\n\n" ++
            "deps_{s} := \\\n" ++
            "  {s} \\\n" ++
            "  {s} \\\n" ++
            "\n" ++
            "{s}: $(deps_{s})\n\n" ++
            "$(deps_{s}):\n",
        .{
            target_name,
            target_name,
            escaped_source_path,
            target_name,
            escaped_space_dep_path,
            escaped_tab_dep_path,
            target_name,
            target_name,
            target_name,
        },
    );
    defer std.testing.allocator.free(expected);

    try std.testing.expectEqualStrings(expected, result.stdout);
}
