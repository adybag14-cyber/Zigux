const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const setup_markers = [_][]const u8{
    "      - name: Setup pinned Zig toolchain",
    "          canonical_repo = \"adybag14-cyber/zig\"",
    "          canonical_tag = \"upstream-748e7c5e39fc\"",
    "          url = f\"https://ziglang.org/builds/{filename}\"",
    "          canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"",
    "          archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"",
    "          mirror_file=\".zig-toolchain/community-mirrors.txt\"",
    "          repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "          repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
};

const local_archive_markers = [_][]const u8{
    "              if [ ! -d \"$repo_archive_parts_dir\" ]; then",
    "              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root \"$GITHUB_WORKSPACE\"                 --parts-dir \"$repo_archive_parts_dir\" || return 1",
    "            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then",
    "              tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
};

const fallback_order_markers = [_][]const u8{
    "          if try_local_archive; then",
    "          elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "              if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
    "            if try_download \"$ZIGUX_ZIG_URL\"; then",
    "            echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
};

fn readWorkflowSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn markerIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingWorkflowMarker;
}

fn markerIndexAfter(source: []const u8, start: usize, marker: []const u8) !usize {
    return std.mem.indexOfPos(u8, source, start, marker) orelse error.MissingWorkflowMarker;
}

fn countOccurrences(source: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, source, offset, marker)) |index| {
        count += 1;
        offset = index + marker.len;
    }
    return count;
}

fn expectUnique(source: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(source, marker));
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        try expectUnique(source, marker);
        const current = try markerIndex(source, marker);
        if (previous) |prev| {
            try std.testing.expect(current > prev);
        }
        previous = current;
    }
}

test "setup step keeps pinned source derivation and local archive paths explicit" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &setup_markers);
}

test "repo-local archive and parts staging stay verified before extraction" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &local_archive_markers);

    const local_start = try markerIndex(workflow_source, "          try_local_archive() {");
    const local_end = try markerIndex(workflow_source, "          try_download() {");
    const parts_check = try markerIndex(workflow_source, local_archive_markers[0]);
    const stage_helper = try markerIndex(workflow_source, local_archive_markers[1]);
    const archive_verify = try markerIndex(workflow_source, local_archive_markers[2]);
    const zig_verify = try markerIndexAfter(
        workflow_source,
        archive_verify,
        "              if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then",
    );

    try std.testing.expect(local_start < parts_check);
    try std.testing.expect(parts_check < stage_helper);
    try std.testing.expect(stage_helper < archive_verify);
    try std.testing.expect(archive_verify < zig_verify);
    try std.testing.expect(zig_verify < local_end);
}

test "download fallback order remains local canonical mirrors then ziglang fail-closed" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &fallback_order_markers);

    const local_fallback = try markerIndex(workflow_source, fallback_order_markers[0]);
    const canonical_fallback = try markerIndex(workflow_source, fallback_order_markers[1]);
    const mirror_list = try markerIndex(workflow_source, fallback_order_markers[2]);
    const mirror_download = try markerIndex(workflow_source, fallback_order_markers[3]);
    const ziglang_fallback = try markerIndex(workflow_source, fallback_order_markers[4]);
    const failure_message = try markerIndex(workflow_source, fallback_order_markers[5]);
    const path_export = try markerIndex(workflow_source, "          echo \"$extract_root\" >> \"$GITHUB_PATH\"");

    try std.testing.expect(local_fallback < canonical_fallback);
    try std.testing.expect(canonical_fallback < mirror_list);
    try std.testing.expect(mirror_list < mirror_download);
    try std.testing.expect(mirror_download < ziglang_fallback);
    try std.testing.expect(ziglang_fallback < failure_message);
    try std.testing.expect(failure_message < path_export);
}
