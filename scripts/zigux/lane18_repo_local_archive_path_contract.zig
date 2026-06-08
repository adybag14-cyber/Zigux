const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const max_workflow_bytes = 256 * 1024;

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, max_workflow_bytes);
    defer allocator.free(workflow);
    try verifyWorkflow(workflow);
}

fn verifyWorkflow(workflow: []const u8) !void {
    try expectContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try expectContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectContains(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try expectContains(workflow, "--parts-dir \"$repo_archive_parts_dir\" || return 1");
    try expectContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectContains(workflow, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");

    try expectBefore(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"", "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try expectBefore(workflow, "if [ ! -f \"$repo_archive_path\" ]; then", "if [ ! -d \"$repo_archive_parts_dir\" ]; then");
    try expectBefore(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) return error.MissingWorkflowMarker;
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingWorkflowMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingWorkflowMarker;
    if (before_index >= after_index) return error.WorkflowMarkerOutOfOrder;
}

test "repo-local archive path markers are required" {
    const workflow =
        \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\try_local_archive() {
        \\  if [ ! -f "$repo_archive_path" ]; then
        \\    if [ ! -d "$repo_archive_parts_dir" ]; then
        \\      return 1
        \\    fi
        \\    python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
        \\  fi
        \\  if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
        \\    tar -xJf "$repo_archive_path" -C .zig-toolchain
        \\  fi
        \\}
        \\if try_local_archive; then
        \\  download_success=1
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\  download_success=1
        \\fi
    ;

    try verifyWorkflow(workflow);
}

test "repo-local archive verification must precede extraction" {
    const bad_workflow =
        \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\if [ ! -f "$repo_archive_path" ]; then
        \\  if [ ! -d "$repo_archive_parts_dir" ]; then
        \\    return 1
        \\  fi
        \\  python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
        \\fi
        \\tar -xJf "$repo_archive_path" -C .zig-toolchain
        \\python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
        \\if try_local_archive; then
        \\  download_success=1
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\  download_success=1
        \\fi
    ;

    try std.testing.expectError(error.WorkflowMarkerOutOfOrder, verifyWorkflow(bad_workflow));
}

test "download fallback must stay after repo-local archive attempt" {
    const bad_workflow =
        \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\if try_local_archive; then
        \\if [ ! -f "$repo_archive_path" ]; then
        \\  if [ ! -d "$repo_archive_parts_dir" ]; then
        \\    return 1
        \\  fi
        \\  python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
        \\fi
        \\python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
        \\tar -xJf "$repo_archive_path" -C .zig-toolchain
    ;

    try std.testing.expectError(error.WorkflowMarkerOutOfOrder, verifyWorkflow(bad_workflow));
}
