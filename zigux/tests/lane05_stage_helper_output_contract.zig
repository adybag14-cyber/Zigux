const std = @import("std");

const Marker = struct {
    needle: []const u8,
    label: []const u8,
};

fn readRepoFile(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        relative_path,
        allocator,
        .limited(4 * 1024 * 1024),
    );
}

fn expectMarkersPresent(haystack: []const u8, markers: []const Marker) !void {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker.needle) == null) {
            std.debug.print("missing Lane 05 stage-helper output marker: {s}\n", .{marker.label});
            return error.MissingLane05StageHelperOutputMarker;
        }
    }
}

fn expectMarkersInOrder(haystack: []const u8, markers: []const Marker) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, haystack[cursor..], marker.needle) orelse {
            std.debug.print("missing ordered Lane 05 stage-helper output marker: {s}\n", .{marker.label});
            return error.MissingLane05StageHelperOutputMarker;
        };
        cursor += found + marker.needle.len;
    }
}

test "stage helper reports stable success fields for CI diagnostics" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(helper);

    try expectMarkersInOrder(helper, &.{
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE=pass", .label = "success sentinel" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_ROOT=", .label = "root output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=", .label = "input mode output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_TARGET=", .label = "target output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=", .label = "filename output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=", .label = "expected size output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=", .label = "expected sha output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=", .label = "actual sha output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=", .label = "destination output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_STATUS=", .label = "status output" },
    });
}

test "stage helper keeps source and parts-dir status vocabulary" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(helper);

    try expectMarkersPresent(helper, &.{
        .{ .needle = "return source, \"source\", None", .label = "source input mode" },
        .{ .needle = "return reconstructed_source, \"parts_dir\", temp_dir", .label = "parts-dir input mode" },
        .{ .needle = "\"checked\"", .label = "check-only status" },
        .{ .needle = "\"already_present\"", .label = "already-present status" },
        .{ .needle = "return metadata, \"staged\", staged_sha, destination, input_mode", .label = "staged status" },
        .{ .needle = "assert input_mode == \"source\"", .label = "source self-test assertion" },
        .{ .needle = "assert input_mode == \"parts_dir\"", .label = "parts-dir self-test assertion" },
    });
}

test "stage helper failure output preserves actionable note surface" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(helper);

    try expectMarkersInOrder(helper, &.{
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE=fail", .label = "failure sentinel" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_ROOT=", .label = "failure root output" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_NOTE=", .label = "failure note output" },
    });

    try expectMarkersPresent(helper, &.{
        .{ .needle = "missing shard manifest", .label = "missing manifest note" },
        .{ .needle = "expected shard manifest sha256", .label = "manifest sha note" },
        .{ .needle = "missing expected shard", .label = "missing shard note" },
        .{ .needle = "invalid base64 shard", .label = "invalid shard note" },
        .{ .needle = "duplicate toolchain policy keys", .label = "duplicate policy note" },
    });
}

test "bootstrap workflow exercises the stage helper before fallback downloads" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectMarkersInOrder(workflow, &.{
        .{ .needle = "repo_archive_parts_dir=\"${repo_archive_path}.parts\"", .label = "archive parts directory" },
        .{ .needle = "python3 scripts/zigux/stage-pinned-zig-archive.py", .label = "stage helper invocation" },
        .{ .needle = "--parts-dir \"$repo_archive_parts_dir\"", .label = "parts-dir argument" },
        .{ .needle = "if try_local_archive; then", .label = "local archive branch" },
        .{ .needle = "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt", .label = "community mirror fallback" },
        .{ .needle = "if try_download \"$ZIGUX_ZIG_URL\"; then", .label = "official fallback" },
    });
}
