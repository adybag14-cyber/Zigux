const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
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

fn expectContractFails(workflow: []const u8) !void {
    checkSetupCleanupHandoffContract(workflow) catch return;
    return error.ContractAcceptedInvalidWorkflow;
}

fn checkSetupCleanupHandoffContract(workflow: []const u8) !void {
    try requireContains(workflow, "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow, "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"");
    try requireContains(workflow, "mirror_file=\".zig-toolchain/community-mirrors.txt\"");
    try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
    try requireContains(workflow, "rm -f \"$archive_path\" \"$mirror_file\"");
    try requireContains(workflow, "rm -rf \"$extract_root\"");
    try requireContains(workflow, "try_local_archive() {");
    try requireContains(workflow, "try_download() {");
    try requireContains(workflow, "download_success=0");
    try requireContains(workflow, "if try_local_archive; then");
    try requireContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireContains(workflow, "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then");
    try requireContains(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");

    try requireOrder(workflow, "rm -f \"$archive_path\" \"$mirror_file\"", "try_local_archive() {");
    try requireOrder(workflow, "rm -rf \"$extract_root\"", "try_local_archive() {");
    try requireOrder(workflow, "rm -f \"$archive_path\" \"$mirror_file\"", "download_success=0");
    try requireOrder(workflow, "try_local_archive() {", "try_download() {");
    try requireOrder(workflow, "try_download() {", "download_success=0");
    try requireOrder(workflow, "download_success=0", "if try_local_archive; then");
    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireOrder(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then", "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then");
    try requireOrder(workflow, "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then", "if try_download \"$ZIGUX_ZIG_URL\"; then");

    try requireOrder(
        workflow,
        "tar -xJf \"$repo_archive_path\" -C .zig-toolchain",
        "rm -rf \"$extract_root\"\n            return 1\n          }\n          try_download() {",
    );
    try requireOrder(
        workflow,
        "if curl -L --fail \"$url\" -o \"$archive_path\"; then",
        "rm -f \"$archive_path\"\n              rm -rf \"$extract_root\"",
    );
    try requireOrder(
        workflow,
        "rm -f \"$archive_path\"\n              rm -rf \"$extract_root\"",
        "return 1\n          }\n          download_success=0",
    );
    try requireOrder(
        workflow,
        "return 1\n          }\n          download_success=0",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
    );
}

test "Lane 05 setup cleanup handoff guards stale fallback state" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkSetupCleanupHandoffContract(workflow);
}

test "Lane 05 setup cleanup handoff rejects missing initial stale-state reset" {
    const invalid =
        \\archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
        \\extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\mirror_file=".zig-toolchain/community-mirrors.txt"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\try_local_archive() {
        \\  tar -xJf "$repo_archive_path" -C .zig-toolchain
        \\  rm -rf "$extract_root"
        \\  return 1
        \\}
        \\try_download() {
        \\  if curl -L --fail "$url" -o "$archive_path"; then
        \\    rm -f "$archive_path"
        \\    rm -rf "$extract_root"
        \\  fi
        \\  return 1
        \\}
        \\download_success=0
        \\if try_local_archive; then
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\  fi
        \\fi
        \\if try_download "$ZIGUX_ZIG_URL"; then
        \\fi
        \\echo "$extract_root" >> "$GITHUB_PATH"
    ;

    try expectContractFails(invalid);
}

test "Lane 05 setup cleanup handoff rejects download retry without archive cleanup" {
    const invalid =
        \\archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
        \\extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\mirror_file=".zig-toolchain/community-mirrors.txt"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\rm -f "$archive_path" "$mirror_file"
        \\rm -rf "$extract_root"
        \\try_local_archive() {
        \\  tar -xJf "$repo_archive_path" -C .zig-toolchain
        \\  rm -rf "$extract_root"
        \\  return 1
        \\}
        \\try_download() {
        \\  if curl -L --fail "$url" -o "$archive_path"; then
        \\    rm -rf "$extract_root"
        \\  fi
        \\  return 1
        \\}
        \\download_success=0
        \\if try_local_archive; then
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\  fi
        \\fi
        \\if try_download "$ZIGUX_ZIG_URL"; then
        \\fi
        \\echo "$extract_root" >> "$GITHUB_PATH"
    ;

    try expectContractFails(invalid);
}

test "Lane 05 setup cleanup handoff rejects cleanup after path activation" {
    const invalid =
        \\archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
        \\extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\mirror_file=".zig-toolchain/community-mirrors.txt"
        \\repo_archive_parts_dir="${repo_archive_path}.parts"
        \\rm -f "$archive_path" "$mirror_file"
        \\try_local_archive() {
        \\  tar -xJf "$repo_archive_path" -C .zig-toolchain
        \\  return 1
        \\}
        \\try_download() {
        \\  if curl -L --fail "$url" -o "$archive_path"; then
        \\  fi
        \\  return 1
        \\}
        \\download_success=0
        \\if try_local_archive; then
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\  fi
        \\fi
        \\if try_download "$ZIGUX_ZIG_URL"; then
        \\fi
        \\echo "$extract_root" >> "$GITHUB_PATH"
        \\rm -f "$archive_path"
        \\rm -rf "$extract_root"
    ;

    try expectContractFails(invalid);
}
