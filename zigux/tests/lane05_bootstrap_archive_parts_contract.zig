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

fn expectMarkersInOrder(haystack: []const u8, markers: []const Marker) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, haystack[cursor..], marker.needle) orelse {
            std.debug.print("missing Lane 05 archive-parts marker: {s}\n", .{marker.label});
            return error.MissingArchivePartsMarker;
        };
        cursor += found + marker.needle.len;
    }
}

fn expectMarkersPresent(haystack: []const u8, markers: []const Marker) !void {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker.needle) == null) {
            std.debug.print("missing Lane 05 archive-parts marker: {s}\n", .{marker.label});
            return error.MissingArchivePartsMarker;
        }
    }
}

test "bootstrap workflow tries repo archive parts before remote downloads" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectMarkersInOrder(workflow, &.{
        .{
            .needle = "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
            .label = "repo archive parts directory",
        },
        .{
            .needle = "python3 scripts/zigux/stage-pinned-zig-archive.py",
            .label = "archive-parts staging helper",
        },
        .{
            .needle = "--parts-dir \"$repo_archive_parts_dir\"",
            .label = "parts-dir staging argument",
        },
        .{
            .needle = "if try_local_archive; then",
            .label = "local archive attempt before mirrors",
        },
        .{
            .needle = "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt",
            .label = "community mirror fallback",
        },
        .{
            .needle = "if try_download \"$ZIGUX_ZIG_URL\"; then",
            .label = "official Zig fallback",
        },
    });
}

test "archive staging helper exposes parts mode and fail-closed shard checks" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, "scripts/zigux/stage-pinned-zig-archive.py");
    defer allocator.free(helper);

    try expectMarkersPresent(helper, &.{
        .{ .needle = "parser.add_argument(\"--parts-dir\"", .label = "parts-dir CLI" },
        .{ .needle = "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE", .label = "input-mode output" },
        .{ .needle = "input_mode == \"parts_dir\"", .label = "parts-dir self-test" },
        .{ .needle = "missing shard manifest", .label = "missing manifest failure" },
        .{ .needle = "expected shard manifest sha256", .label = "manifest sha check" },
        .{ .needle = "missing expected shard", .label = "missing shard failure" },
        .{ .needle = "invalid base64 shard", .label = "invalid shard failure" },
    });
}

test "toolchain policy keeps one bootstrap archive target pinned" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectMarkersPresent(policy, &.{
        .{ .needle = "\"channel\": \"0.17.0-dev.87+9b177a7d2\"", .label = "pinned channel" },
        .{ .needle = "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"", .label = "minimum version lockstep" },
        .{ .needle = "\"archive_target_scope\": [", .label = "archive target scope" },
        .{ .needle = "\"x86_64-linux\"", .label = "bootstrap archive target" },
    });
}
