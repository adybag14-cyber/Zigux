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

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn expectContractFails(workflow: []const u8) !void {
    checkSetupDownloadSuccessContract(workflow) catch return;
    return error.ContractAcceptedInvalidWorkflow;
}

fn checkSetupDownloadSuccessContract(workflow: []const u8) !void {
    try requireContains(workflow, "download_success=0");
    try requireContains(workflow, "if try_local_archive; then");
    try requireContains(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireContains(workflow, "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then");
    try requireContains(workflow, "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then");
    try requireContains(workflow, "if [ \"$download_success\" -ne 1 ]; then");
    try requireContains(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireContains(workflow, "if [ \"$download_success\" -ne 1 ]; then\n            echo 'failed to install a verified pinned Zig archive");
    try requireContains(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try requireContains(workflow, "\"$zig_path\" version");

    try std.testing.expect(countOccurrences(workflow, "download_success=1") >= 3);
    try requireOrder(workflow, "download_success=0", "if try_local_archive; then");
    try requireOrder(workflow, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "while IFS= read -r mirror_url; do");
    try requireOrder(workflow, "while IFS= read -r mirror_url; do", "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireOrder(workflow, "if [ \"$download_success\" -ne 1 ]; then\n            if try_download \"$ZIGUX_ZIG_URL\"; then", "if [ \"$download_success\" -ne 1 ]; then\n            echo 'failed to install a verified pinned Zig archive");
    try requireOrder(
        workflow,
        "echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2\n            exit 1\n          fi\n          zig_path=\"$extract_root/zig\"",
        "echo \"$extract_root\" >> \"$GITHUB_PATH\"",
    );
    try requireOrder(workflow, "zig_path=\"$extract_root/zig\"", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
    try requireOrder(workflow, "echo \"$extract_root\" >> \"$GITHUB_PATH\"", "\"$zig_path\" version");
}

test "Lane 05 setup download success state gates the fallback ladder" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkSetupDownloadSuccessContract(workflow);
}

test "Lane 05 setup success contract rejects direct fallback before mirror exhaustion" {
    const invalid =
        \\download_success=0
        \\if try_local_archive; then
        \\  download_success=1
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\  download_success=1
        \\fi
        \\if [ "$download_success" -ne 1 ]; then
        \\  if try_download "$ZIGUX_ZIG_URL"; then
        \\    download_success=1
        \\  fi
        \\fi
        \\while IFS= read -r mirror_url; do
        \\  if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\    download_success=1
        \\    break
        \\  fi
        \\done
        \\if [ "$download_success" -ne 1 ]; then
        \\  echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
        \\fi
        \\zig_path="$extract_root/zig"
        \\echo "$extract_root" >> "$GITHUB_PATH"
        \\"$zig_path" version
    ;

    try expectContractFails(invalid);
}

test "Lane 05 setup success contract rejects activation before final failure gate" {
    const invalid =
        \\download_success=0
        \\if try_local_archive; then
        \\  download_success=1
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\  download_success=1
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  while IFS= read -r mirror_url; do
        \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\      download_success=1
        \\      break
        \\    fi
        \\  done
        \\fi
        \\if [ "$download_success" -ne 1 ]; then
        \\  if try_download "$ZIGUX_ZIG_URL"; then
        \\    download_success=1
        \\  fi
        \\fi
        \\zig_path="$extract_root/zig"
        \\echo "$extract_root" >> "$GITHUB_PATH"
        \\if [ "$download_success" -ne 1 ]; then
        \\  echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
        \\fi
        \\"$zig_path" version
    ;

    try expectContractFails(invalid);
}

test "Lane 05 setup success contract rejects missing failure diagnostic" {
    const invalid =
        \\download_success=0
        \\if try_local_archive; then
        \\  download_success=1
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\  download_success=1
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  while IFS= read -r mirror_url; do
        \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\      download_success=1
        \\      break
        \\    fi
        \\  done
        \\fi
        \\if [ "$download_success" -ne 1 ]; then
        \\  if try_download "$ZIGUX_ZIG_URL"; then
        \\    download_success=1
        \\  fi
        \\fi
        \\zig_path="$extract_root/zig"
        \\echo "$extract_root" >> "$GITHUB_PATH"
        \\"$zig_path" version
    ;

    try expectContractFails(invalid);
}
