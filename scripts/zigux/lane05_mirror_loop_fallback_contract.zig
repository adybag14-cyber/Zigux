const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
    DuplicateMarker,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

fn findMarker(source: []const u8, marker: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, source, marker) orelse ContractError.MissingMarker;
}

fn findMarkerAfter(source: []const u8, marker: []const u8, after: usize) ContractError!usize {
    if (after > source.len) return ContractError.OutOfOrderMarker;
    const relative = std.mem.indexOf(u8, source[after..], marker) orelse return ContractError.MissingMarker;
    return after + relative;
}

fn countOccurrences(source: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (cursor <= source.len) {
        const relative = std.mem.indexOf(u8, source[cursor..], marker) orelse break;
        count += 1;
        cursor += relative + marker.len;
    }
    return count;
}

fn expectExactlyOnce(source: []const u8, marker: []const u8) !void {
    const count = countOccurrences(source, marker);
    if (count == 0) return ContractError.MissingMarker;
    if (count != 1) return ContractError.DuplicateMarker;
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = try findMarkerAfter(source, marker, cursor);
        cursor = found + marker.len;
    }
}

fn checkLane05MirrorLoopFallback(workflow: []const u8) !void {
    try expectExactlyOnce(workflow, "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"");
    try expectExactlyOnce(workflow, "while IFS= read -r mirror_url; do");
    try expectExactlyOnce(workflow, "[ -n \"$mirror_url\" ] || continue");
    try expectExactlyOnce(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectExactlyOnce(workflow, "done < \"$mirror_file\"");
    try expectExactlyOnce(workflow, "try_download \"$ZIGUX_ZIG_URL\"");

    try expectOrdered(workflow, &.{
        "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
        "while IFS= read -r mirror_url; do",
        "[ -n \"$mirror_url\" ] || continue",
        "if try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"; then",
        "download_success=1",
        "break",
        "done < \"$mirror_file\"",
        "if [ \"$download_success\" -ne 1 ]; then",
        "if try_download \"$ZIGUX_ZIG_URL\"; then",
    });

    const loop_start = try findMarker(workflow, "while IFS= read -r mirror_url; do");
    const loop_end = try findMarkerAfter(workflow, "done < \"$mirror_file\"", loop_start);
    const direct_fallback = try findMarker(workflow, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try std.testing.expect(loop_end < direct_fallback);
}

const positive_workflow =
    \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\  while IFS= read -r mirror_url; do
    \\    [ -n "$mirror_url" ] || continue
    \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\      download_success=1
    \\      break
    \\    fi
    \\  done < "$mirror_file"
    \\fi
    \\if [ "$download_success" -ne 1 ]; then
    \\  if try_download "$ZIGUX_ZIG_URL"; then
    \\    download_success=1
    \\  fi
    \\fi
;

test "current bootstrap workflow keeps mirror loop fallback fail-closed" {
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try checkLane05MirrorLoopFallback(workflow);
}

test "contract accepts the intended mirror loop shape" {
    try checkLane05MirrorLoopFallback(positive_workflow);
}

test "mirror loop rejects missing empty-line skip" {
    const bad_workflow = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        positive_workflow,
        "    [ -n \"$mirror_url\" ] || continue\n",
        "",
    ) catch unreachable;
    defer std.testing.allocator.free(bad_workflow);

    try std.testing.expectError(ContractError.MissingMarker, checkLane05MirrorLoopFallback(bad_workflow));
}

test "mirror loop rejects download URL without github bootstrap source tag" {
    const bad_workflow = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        positive_workflow,
        "?source=github-zigux-bootstrap",
        "",
    ) catch unreachable;
    defer std.testing.allocator.free(bad_workflow);

    try std.testing.expectError(ContractError.MissingMarker, checkLane05MirrorLoopFallback(bad_workflow));
}

test "mirror loop rejects direct fallback before mirror roster is exhausted" {
    const bad_workflow =
        \\elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\  if try_download "$ZIGUX_ZIG_URL"; then
        \\    download_success=1
        \\  fi
        \\  while IFS= read -r mirror_url; do
        \\    [ -n "$mirror_url" ] || continue
        \\    if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\      download_success=1
        \\      break
        \\    fi
        \\  done < "$mirror_file"
        \\fi
        \\if [ "$download_success" -ne 1 ]; then
        \\fi
    ;

    try std.testing.expectError(ContractError.MissingMarker, checkLane05MirrorLoopFallback(bad_workflow));
}
