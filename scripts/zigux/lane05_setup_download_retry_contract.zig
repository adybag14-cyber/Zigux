const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectSetupDownloadRetryContract(workflow: []const u8) !void {
    try expectContains(workflow, "- name: Setup pinned Zig toolchain");
    try expectContains(workflow, "try_download() {");
    try expectContains(workflow, "local url=\"$1\"");
    try expectContains(workflow, "curl");
    try expectContains(workflow, "--fail");
    try expectContains(workflow, "--location");
    try expectContains(workflow, "--retry");
    try expectContains(workflow, "--retry-all-errors");
    try expectContains(workflow, "--retry-delay");
    try expectContains(workflow, "--connect-timeout");
    try expectContains(workflow, "--speed-limit");
    try expectContains(workflow, "--speed-time");
    try expectContains(workflow, "\"$url\"");
    try expectContains(workflow, "-o \"$archive_path\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"");
    try expectContains(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectNotContains(workflow, "curl -L --fail \"$url\" -o \"$archive_path\"");
    try expectBefore(workflow, "curl", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\"");
    try expectBefore(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$archive_path\"", "tar -xJf \"$archive_path\" -C .zig-toolchain");
    try expectBefore(workflow, "try_download \"$ZIGUX_ZIG_CANONICAL_URL\"", "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectBefore(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"", "try_download \"$ZIGUX_ZIG_URL\"");
}

const hardened_setup_block =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          try_download() {
    \\            local url="$1"
    \\            if curl \
    \\              --fail \
    \\              --location \
    \\              --retry 5 \
    \\              --retry-all-errors \
    \\              --retry-delay 3 \
    \\              --connect-timeout 20 \
    \\              --speed-limit 1 \
    \\              --speed-time 60 \
    \\              "$url" \
    \\              -o "$archive_path"; then
    \\              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\                tar -xJf "$archive_path" -C .zig-toolchain
    \\              fi
    \\            fi
    \\          }
    \\          if try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\            download_success=1
    \\          elif curl --fail --location https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
    \\              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\                download_success=1
    \\              fi
    \\            done < "$mirror_file"
    \\          fi
    \\          if [ "$download_success" -ne 1 ]; then
    \\            if try_download "$ZIGUX_ZIG_URL"; then
    \\              download_success=1
    \\            fi
    \\          fi
;

const vulnerable_setup_block =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          try_download() {
    \\            local url="$1"
    \\            if curl -L --fail "$url" -o "$archive_path"; then
    \\              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\                tar -xJf "$archive_path" -C .zig-toolchain
    \\              fi
    \\            fi
    \\          }
    \\          if try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\            download_success=1
    \\          fi
;

test "setup archive downloads carry retry and stall guards" {
    try expectSetupDownloadRetryContract(hardened_setup_block);
}

test "single-shot setup archive download is rejected" {
    try std.testing.expectError(error.TestUnexpectedResult, expectSetupDownloadRetryContract(vulnerable_setup_block));
}

test "download verification must remain before extraction" {
    const bad_order =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          try_download() {
        \\            local url="$1"
        \\            if curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1 --speed-time 60 "$url" -o "$archive_path"; then
        \\              tar -xJf "$archive_path" -C .zig-toolchain
        \\              python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path"
        \\            fi
        \\          }
        \\          if try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\            download_success=1
        \\          elif try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\            download_success=1
        \\          fi
        \\          if try_download "$ZIGUX_ZIG_URL"; then
        \\            download_success=1
        \\          fi
    ;

    try std.testing.expectError(error.TestUnexpectedResult, expectSetupDownloadRetryContract(bad_order));
}

test "mirror fallback must remain before direct ziglang fallback" {
    const bad_fallback_order =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          try_download() {
        \\            local url="$1"
        \\            if curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1 --speed-time 60 "$url" -o "$archive_path"; then
        \\              python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path"
        \\              tar -xJf "$archive_path" -C .zig-toolchain
        \\            fi
        \\          }
        \\          if try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\            download_success=1
        \\          fi
        \\          if try_download "$ZIGUX_ZIG_URL"; then
        \\            download_success=1
        \\          elif try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
        \\            download_success=1
        \\          fi
    ;

    try std.testing.expectError(error.TestUnexpectedResult, expectSetupDownloadRetryContract(bad_fallback_order));
}
