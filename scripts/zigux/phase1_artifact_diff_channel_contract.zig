const std = @import("std");

const testing = std.testing;

fn writeFixture(dir: std.Io.Dir, name: []const u8, contents: []const u8) !void {
    const file = try dir.createFile(testing.io, name, .{ .read = true });
    defer file.close(testing.io);

    var buffer: [128]u8 = undefined;
    var writer: std.Io.File.Writer = .init(file, testing.io, &buffer);
    try writer.interface.writeAll(contents);
    try writer.interface.flush();
}

fn tempPath(allocator: std.mem.Allocator, tmp: *const std.testing.TmpDir, name: []const u8) ![]u8 {
    return std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp.sub_path, name });
}

fn runArtifactDiff(allocator: std.mem.Allocator, args: []const []const u8) !std.process.RunResult {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    var argv = try allocator.alloc([]const u8, args.len + 2);
    defer allocator.free(argv);
    argv[0] = "python3";
    argv[1] = "scripts/zigux/artifact_diff.py";
    @memcpy(argv[2..], args);

    return std.process.run(allocator, io_instance.io(), .{
        .argv = argv,
        .stdout_limit = .limited(64 * 1024),
        .stderr_limit = .limited(64 * 1024),
    });
}

fn expectExit(result: std.process.RunResult, expected: u8) !void {
    switch (result.term) {
        .exited => |code| try testing.expectEqual(expected, code),
        else => return error.UnexpectedProcessTermination,
    }
}

test "artifact diff success writes result envelope only to stdout" {
    var tmp = testing.tmpDir(.{});
    defer tmp.cleanup();

    try writeFixture(tmp.dir, "expected.txt", "alpha\nbeta\n");
    try writeFixture(tmp.dir, "actual.txt", "alpha\nbeta\n");

    const expected_path = try tempPath(testing.allocator, &tmp, "expected.txt");
    defer testing.allocator.free(expected_path);
    const actual_path = try tempPath(testing.allocator, &tmp, "actual.txt");
    defer testing.allocator.free(actual_path);

    const result = try runArtifactDiff(testing.allocator, &.{ "--mode", "text", expected_path, actual_path });
    defer testing.allocator.free(result.stdout);
    defer testing.allocator.free(result.stderr);

    try expectExit(result, 0);
    try testing.expectEqual(@as(usize, 0), result.stderr.len);
    try testing.expect(std.mem.startsWith(u8, result.stdout, "ARTIFACT_DIFF=pass\nMODE=text\n"));
    try testing.expect(std.mem.indexOf(u8, result.stdout, "EXPECTED=") != null);
    try testing.expect(std.mem.indexOf(u8, result.stdout, "ACTUAL=") != null);
}

test "artifact diff self-test writes summary only to stdout" {
    const result = try runArtifactDiff(testing.allocator, &.{"--self-test"});
    defer testing.allocator.free(result.stdout);
    defer testing.allocator.free(result.stderr);

    try expectExit(result, 0);
    try testing.expectEqual(@as(usize, 0), result.stderr.len);
    try testing.expect(std.mem.indexOf(u8, result.stdout, "ARTIFACT_DIFF_SELF_TEST=pass\n") != null);
    try testing.expect(std.mem.indexOf(u8, result.stdout, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=") != null);
}

test "artifact diff parser failures write diagnostics only to stderr" {
    const missing = try runArtifactDiff(testing.allocator, &.{"--mode"});
    defer testing.allocator.free(missing.stdout);
    defer testing.allocator.free(missing.stderr);

    try expectExit(missing, 2);
    try testing.expectEqual(@as(usize, 0), missing.stdout.len);
    try testing.expect(std.mem.indexOf(u8, missing.stderr, "artifact_diff.py") != null);
    try testing.expect(std.mem.indexOf(u8, missing.stderr, "--mode") != null);

    const invalid = try runArtifactDiff(testing.allocator, &.{ "--mode", "yaml", "expected.txt", "actual.txt" });
    defer testing.allocator.free(invalid.stdout);
    defer testing.allocator.free(invalid.stderr);

    try expectExit(invalid, 2);
    try testing.expectEqual(@as(usize, 0), invalid.stdout.len);
    try testing.expect(std.mem.indexOf(u8, invalid.stderr, "yaml") != null);
}
