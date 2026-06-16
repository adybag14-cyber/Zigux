const std = @import("std");
const routes = @import("bootstrap_toolchain_route_contract.zig");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "Lane 05 bootstrap setup tries repo-local archive before all download fallbacks" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "try_local_archive() {");
    try requireContains(workflow, "try_download() {");
    try routes.requireRoute(workflow, routes.stage_python, routes.stage_zig);
    try requireContains(workflow, "--parts-dir \"$repo_archive_parts_dir\"");

    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl --fail");
    try requireOrder(workflow, "elif curl --fail", "https://ziglang.org/download/community-mirrors.txt");
    try requireOrder(workflow, "while IFS= read -r mirror_url; do", "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "Lane 05 staged parts path feeds the same policy archive validator before extraction" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const parts_index = std.mem.indexOf(u8, workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"") orelse return error.MissingPartsDir;
    const stage_index = routes.routeIndex(workflow, routes.stage_python, routes.stage_zig) orelse return error.MissingStageRoute;
    const archive_index = routes.routeIndex(workflow, routes.archive_check_python, routes.archive_check_zig) orelse return error.MissingArchiveRoute;
    const tar_index = std.mem.indexOf(u8, workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain") orelse return error.MissingTarStep;
    const zig_probe_index = routes.routeIndex(workflow, routes.zig_probe_python, routes.zig_probe_zig) orelse return error.MissingZigProbeRoute;
    try std.testing.expect(parts_index < stage_index);
    try std.testing.expect(stage_index < archive_index);
    try std.testing.expect(archive_index < tar_index);
    try std.testing.expect(tar_index < zig_probe_index);
}

test "Lane 05 fallback cleanup clears partial archive and extraction state" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "rm -f \"$archive_path\" \"$mirror_file\"");
    try requireContains(workflow, "rm -f \"$archive_path\"\n              rm -rf \"$extract_root\"");
    try std.testing.expect(countOccurrences(workflow, "rm -rf \"$extract_root\"") >= 3);

    try requireOrder(workflow, "rm -f \"$archive_path\" \"$mirror_file\"", "if try_local_archive; then");
    try requireOrder(workflow, "rm -rf \"$extract_root\"", "if try_local_archive; then");
}

test "Lane 05 workflow still runs the shipped local archive guards" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOrder(workflow, "Check current Zig toolchain policy packet", "Check current pinned Zig archive packet");
    try requireOrder(workflow, "Check current pinned Zig archive packet", "Self-test current Lane 05 local-first archive checker");
    try requireOrder(workflow, "Self-test current Lane 05 local-first archive checker", "Check current Lane 05 local-first archive packet");
    try requireOrder(workflow, "Check current Lane 05 local archive README packet", "Self-test current Lane 05 install-zig archive verification checker");
    try requireOrder(workflow, "Check current Lane 05 install-zig archive verification packet", "Self-test current staged pinned Zig archive helper");
    try requireOrder(workflow, "Self-test current Lane 05 stage helper contract checker", "Check current Lane 05 stage helper contract packet");
    try requireOrder(workflow, "Self-test current Lane 05 stage helper selftest checker", "Check current Lane 05 stage helper selftest packet");
}
