const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    WrongOrder,
    WrongFunctionBoundary,
};

const expected_markers = [_][]const u8{
    "try_local_archive() {",
    "if [ ! -f \"$repo_archive_path\" ]; then",
    "if [ ! -d \"$repo_archive_parts_dir\" ]; then",
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
    "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
    "rm -rf \"$extract_root\"",
    "try_download() {",
    "if curl -L --fail \"$url\" -o \"$archive_path\"; then",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "tar -xJf \"$archive_path\" -C .zig-toolchain",
    "rm -f \"$archive_path\"",
    "rm -rf \"$extract_root\"",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "while IFS= read -r mirror_url; do",
    "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org'",
    "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
    "\"$zig_path\" version",
};

fn indexOfMarker(haystack: []const u8, marker: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, haystack, marker) orelse error.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) ContractError!void {
    var search_start: usize = 0;
    for (markers, 0..) |marker, i| {
        const relative = std.mem.indexOf(u8, haystack[search_start..], marker) orelse return error.MissingMarker;
        const position = search_start + relative;
        if (i != 0 and position < search_start) return error.WrongOrder;
        search_start = position + marker.len;
    }
}

fn sliceFromMarker(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ContractError![]const u8 {
    const start = try indexOfMarker(haystack, start_marker);
    const rest = haystack[start + start_marker.len ..];
    const end = std.mem.indexOf(u8, rest, end_marker) orelse return error.WrongFunctionBoundary;
    return rest[0..end];
}

fn requireContains(haystack: []const u8, marker: []const u8) ContractError!void {
    _ = try indexOfMarker(haystack, marker);
}

fn requireNotContains(haystack: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, haystack, marker) != null) return error.WrongFunctionBoundary;
}

fn validateSetupFunctionTopology(workflow: []const u8) ContractError!void {
    try requireOrdered(workflow, expected_markers[0..]);

    const first_mirror_fetch = try indexOfMarker(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    const first_direct_download = try indexOfMarker(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    if (first_direct_download < first_mirror_fetch) return error.WrongOrder;

    const local_archive_body = try sliceFromMarker(workflow, "try_local_archive() {", "try_download() {");
    try requireContains(local_archive_body, "stage-pinned-zig-archive.py");
    try requireContains(local_archive_body, "--archive \"$repo_archive_path\"");
    try requireContains(local_archive_body, "--zig \"$zig_path\"");
    try requireContains(local_archive_body, "rm -rf \"$extract_root\"");
    try requireNotContains(local_archive_body, "curl -L --fail \"$url\"");
    try requireNotContains(local_archive_body, "rm -f \"$archive_path\"");

    const download_body = try sliceFromMarker(workflow, "try_download() {", "download_success=0");
    try requireContains(download_body, "curl -L --fail \"$url\" -o \"$archive_path\"");
    try requireContains(download_body, "--archive \"$archive_path\"");
    try requireContains(download_body, "--zig \"$zig_path\"");
    try requireContains(download_body, "rm -f \"$archive_path\"");
    try requireContains(download_body, "rm -rf \"$extract_root\"");
    try requireNotContains(download_body, "stage-pinned-zig-archive.py");
    try requireNotContains(download_body, "--archive \"$repo_archive_path\"");
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    const workflow = try readWorkflow(allocator);
    defer allocator.free(workflow);
    try validateSetupFunctionTopology(workflow);
}

const valid_workflow =
    \\try_local_archive() {
    \\  if [ ! -f "$repo_archive_path" ]; then
    \\    if [ ! -d "$repo_archive_parts_dir" ]; then
    \\      return 1
    \\    fi
    \\    python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
    \\  fi
    \\  if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\    tar -xJf "$repo_archive_path" -C .zig-toolchain
    \\    zig_path="$extract_root/zig"
    \\    if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\      return 0
    \\    fi
    \\  fi
    \\  rm -rf "$extract_root"
    \\  return 1
    \\}
    \\try_download() {
    \\  local url="$1"
    \\  if curl -L --fail "$url" -o "$archive_path"; then
    \\    if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\      tar -xJf "$archive_path" -C .zig-toolchain
    \\      zig_path="$extract_root/zig"
    \\      if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\        return 0
    \\      fi
    \\    fi
    \\    rm -f "$archive_path"
    \\    rm -rf "$extract_root"
    \\  fi
    \\  return 1
    \\}
    \\download_success=0
    \\if try_local_archive; then
    \\  download_success=1
    \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\  download_success=1
    \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\  while IFS= read -r mirror_url; do
    \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\      break
    \\    fi
    \\  done < "$mirror_file"
    \\fi
    \\if try_download "$ZIGUX_ZIG_URL"; then
    \\  download_success=1
    \\fi
    \\echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
    \\echo "$extract_root" >> "$GITHUB_PATH"
    \\"$zig_path" version
;

test "lane05 setup function topology accepts current-shaped workflow" {
    try validateSetupFunctionTopology(valid_workflow);
}

test "lane05 setup function topology rejects download work inside local archive helper" {
    const invalid = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "try_download() {",
        "curl -L --fail \"$url\" -o \"$archive_path\"\ntry_download() {",
    ) catch unreachable;
    defer std.testing.allocator.free(invalid);
    try std.testing.expectError(error.WrongFunctionBoundary, validateSetupFunctionTopology(invalid));
}

test "lane05 setup function topology rejects staging work inside download helper" {
    const invalid = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "download_success=0",
        "python3 scripts/zigux/stage-pinned-zig-archive.py\n" ++
            "download_success=0",
    ) catch unreachable;
    defer std.testing.allocator.free(invalid);
    try std.testing.expectError(error.WrongFunctionBoundary, validateSetupFunctionTopology(invalid));
}

test "lane05 setup function topology rejects direct fallback before mirror loop" {
    const invalid = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then\n" ++
            "  download_success=1\n" ++
            "fi\n" ++
            "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    ) catch unreachable;
    defer std.testing.allocator.free(invalid);
    try std.testing.expectError(error.WrongOrder, validateSetupFunctionTopology(invalid));
}
