const std = @import("std");
const routes = @import("bootstrap_toolchain_route_contract.zig");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], marker) orelse return error.MissingOrderedMarker;
        cursor += relative + marker.len;
    }
}

test "pinned toolchain setup keeps fallback sources ordered" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    const setup_index = try requireContains(workflow, "- name: Setup pinned Zig toolchain");
    const local_index = try requireContains(workflow, "try_local_archive()");
    const stage_index = routes.routeIndex(workflow, routes.stage_python, routes.stage_zig) orelse return error.MissingStageRoute;
    const archive_index = routes.routeIndex(workflow, routes.archive_check_python, routes.archive_check_zig) orelse return error.MissingArchiveRoute;
    const canonical_index = try requireContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    const mirrors_index = try requireContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    const mirror_try_index = try requireContains(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    const retry_guard_index = try requireContains(workflow, "if [ \"$download_success\" -ne 1 ]; then");
    const direct_index = try requireContains(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try std.testing.expect(setup_index < local_index);
    try std.testing.expect(local_index < stage_index);
    try std.testing.expect(stage_index < archive_index);
    try std.testing.expect(archive_index < canonical_index);
    try std.testing.expect(canonical_index < mirrors_index);
    try std.testing.expect(mirrors_index < mirror_try_index);
    try std.testing.expect(mirror_try_index < retry_guard_index);
    try std.testing.expect(retry_guard_index < direct_index);
}

test "download attempts verify archives before extraction" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    const download_index = try requireContains(workflow, "try_download() {");
    const download_end = std.mem.indexOf(u8, workflow[download_index..], "return 1\n          }") orelse return error.MissingDownloadEnd;
    const download_block = workflow[download_index .. download_index + download_end];
    const curl_if_index = std.mem.indexOf(u8, download_block, "if curl --fail") orelse return error.MissingCurlProbe;
    const archive_rel = routes.routeIndex(download_block, routes.archive_check_python, routes.archive_check_zig) orelse return error.MissingArchiveRoute;
    const tar_rel = std.mem.indexOf(u8, download_block, "tar -xJf \"$archive_path\" -C .zig-toolchain") orelse return error.MissingTarStep;
    const zig_probe_rel = routes.routeIndex(download_block, routes.zig_probe_python, routes.zig_probe_zig) orelse return error.MissingZigProbeRoute;
    const rm_archive_rel = std.mem.indexOf(u8, download_block, "rm -f \"$archive_path\"") orelse return error.MissingArchiveCleanup;
    const rm_extract_rel = std.mem.indexOf(u8, download_block, "rm -rf \"$extract_root\"") orelse return error.MissingExtractCleanup;
    try std.testing.expect(curl_if_index < archive_rel);
    try std.testing.expect(archive_rel < tar_rel);
    try std.testing.expect(tar_rel < zig_probe_rel);
    try std.testing.expect(zig_probe_rel < rm_archive_rel);
    try std.testing.expect(rm_archive_rel < rm_extract_rel);
}

test "failed fallback emits explicit verified archive failure" {
    const allocator = std.testing.allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);

    _ = try requireContains(workflow, "download_success=0");
    try requireOrdered(workflow, &.{
        "if [ \"$download_success\" -ne 1 ]; then",
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2",
        "exit 1",
    });
    _ = try requireContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    _ = try requireContains(workflow, "\"$zig_path\" version");
}
