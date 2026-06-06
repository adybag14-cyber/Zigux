const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const workflow_excerpt =
    \\          try_download() {
    \\            local url="$1"
    \\            if curl -L --fail "$url" -o "$archive_path"; then
    \\              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\                tar -xJf "$archive_path" -C .zig-toolchain
    \\                zig_path="$extract_root/zig"
    \\                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\                  return 0
    \\                fi
    \\              fi
    \\              rm -f "$archive_path"
    \\              rm -rf "$extract_root"
    \\            fi
    \\            return 1
    \\          }
    \\          download_success=0
    \\          if try_local_archive; then
    \\            download_success=1
    \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\            download_success=1
    \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
    \\              [ -n "$mirror_url" ] || continue
    \\              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\                download_success=1
    \\                break
    \\              fi
    \\            done < "$mirror_file"
    \\          fi
    \\          if [ "$download_success" -ne 1 ]; then
    \\            if try_download "$ZIGUX_ZIG_URL"; then
    \\              download_success=1
    \\            fi
    \\          fi
;

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn requireExactCount(text: []const u8, marker: []const u8, expected: usize) ContractError!void {
    var count: usize = 0;
    var cursor = text;
    while (std.mem.indexOf(u8, cursor, marker)) |index| {
        count += 1;
        cursor = cursor[index + marker.len ..];
    }
    if (count != expected) return error.MissingMarker;
}

fn checkTryDownloadCleanup(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "try_download() {");
    try requireContains(workflow, "local url=\"$1\"");
    try requireContains(workflow, "curl -L --fail \"$url\" -o \"$archive_path\"");
    try requireContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireContains(workflow, "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try requireContains(workflow, "zig_path=\"$extract_root/zig\"");
    try requireContains(workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");
    try requireContains(workflow, "rm -f \"$archive_path\"");
    try requireContains(workflow, "rm -rf \"$extract_root\"");
    try requireContains(workflow, "return 1");

    try requireOrder(workflow, "curl -L --fail \"$url\" -o \"$archive_path\"", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireOrder(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try requireOrder(workflow, "tar -xJf \"$archive_path\" -C .zig-toolchain", "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");
    try requireOrder(workflow, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"", "rm -f \"$archive_path\"");
    try requireOrder(workflow, "rm -f \"$archive_path\"", "rm -rf \"$extract_root\"");
    try requireOrder(workflow, "rm -rf \"$extract_root\"", "return 1");

    try requireOrder(workflow, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try requireOrder(workflow, "https://ziglang.org/download/community-mirrors.txt", "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try requireOrder(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"", "try_download \"$ZIGUX_ZIG_URL\"");

    try requireExactCount(workflow, "rm -f \"$archive_path\"", 1);
    try requireExactCount(workflow, "rm -rf \"$extract_root\"", 1);
}

test "lane05 try_download cleans failed archive and extraction state before fallback" {
    try checkTryDownloadCleanup(workflow_excerpt);
}

test "lane05 try_download cleanup rejects archive cleanup after returning failure" {
    const stale_workflow =
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
        \\    rm -rf "$extract_root"
        \\  fi
        \\  return 1
        \\  rm -f "$archive_path"
        \\}
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkTryDownloadCleanup(stale_workflow));
}

test "lane05 try_download cleanup rejects extraction cleanup before archive cleanup" {
    const stale_workflow =
        \\try_download() {
        \\  local url="$1"
        \\  if curl -L --fail "$url" -o "$archive_path"; then
        \\    python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
        \\    tar -xJf "$archive_path" -C .zig-toolchain
        \\    zig_path="$extract_root/zig"
        \\    python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"
        \\    rm -rf "$extract_root"
        \\    rm -f "$archive_path"
        \\  fi
        \\  return 1
        \\}
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkTryDownloadCleanup(stale_workflow));
}

test "lane05 try_download cleanup keeps canonical mirror and direct attempts ordered" {
    const stale_workflow =
        \\try_download() {
        \\  local url="$1"
        \\  curl -L --fail "$url" -o "$archive_path"
        \\  python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
        \\  tar -xJf "$archive_path" -C .zig-toolchain
        \\  zig_path="$extract_root/zig"
        \\  python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"
        \\  rm -f "$archive_path"
        \\  rm -rf "$extract_root"
        \\  return 1
        \\}
        \\try_download "$ZIGUX_ZIG_URL"
        \\https://ziglang.org/download/community-mirrors.txt
        \\try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"
        \\elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkTryDownloadCleanup(stale_workflow));
}
