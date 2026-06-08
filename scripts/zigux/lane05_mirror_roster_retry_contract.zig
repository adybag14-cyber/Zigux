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

fn expectMirrorRosterRetryContract(workflow: []const u8) !void {
    try expectContains(workflow, "- name: Setup pinned Zig toolchain");
    try expectContains(workflow, "mirror_file=\".zig-toolchain/community-mirrors.txt\"");
    try expectContains(workflow, "https://ziglang.org/download/community-mirrors.txt");
    try expectContains(workflow, "-o \"$mirror_file\"");
    try expectContains(workflow, "--fail");
    try expectContains(workflow, "--location");
    try expectContains(workflow, "--retry");
    try expectContains(workflow, "--retry-all-errors");
    try expectContains(workflow, "--retry-delay");
    try expectContains(workflow, "--connect-timeout");
    try expectContains(workflow, "--speed-limit");
    try expectContains(workflow, "--speed-time");
    try expectContains(workflow, "while IFS= read -r mirror_url; do");
    try expectContains(workflow, "[ -n \"$mirror_url\" ] || continue");
    try expectContains(workflow, "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectContains(workflow, "done < \"$mirror_file\"");
    try expectContains(workflow, "try_download \"$ZIGUX_ZIG_URL\"");
    try expectNotContains(workflow, "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"");
    try expectBefore(workflow, "https://ziglang.org/download/community-mirrors.txt", "while IFS= read -r mirror_url; do");
    try expectBefore(workflow, "while IFS= read -r mirror_url; do", "try_download \"${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap\"");
    try expectBefore(workflow, "done < \"$mirror_file\"", "try_download \"$ZIGUX_ZIG_URL\"");
}

const hardened_mirror_roster_block =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          mirror_file=".zig-toolchain/community-mirrors.txt"
    \\          elif curl \
    \\            --fail \
    \\            --location \
    \\            --retry 5 \
    \\            --retry-all-errors \
    \\            --retry-delay 3 \
    \\            --connect-timeout 20 \
    \\            --speed-limit 1024 \
    \\            --speed-time 30 \
    \\            https://ziglang.org/download/community-mirrors.txt \
    \\            -o "$mirror_file"; then
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

const single_shot_mirror_roster_block =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          mirror_file=".zig-toolchain/community-mirrors.txt"
    \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
    \\              [ -n "$mirror_url" ] || continue
    \\              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
    \\                download_success=1
    \\              fi
    \\            done < "$mirror_file"
    \\          fi
    \\          if try_download "$ZIGUX_ZIG_URL"; then
    \\            download_success=1
    \\          fi
;

test "community mirror roster fetch carries retry and stall guards" {
    try expectMirrorRosterRetryContract(hardened_mirror_roster_block);
}

test "single-shot mirror roster fetch is rejected" {
    try std.testing.expectError(error.TestUnexpectedResult, expectMirrorRosterRetryContract(single_shot_mirror_roster_block));
}

test "mirror roster must be fetched before iterating mirror urls" {
    const bad_order =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          mirror_file=".zig-toolchain/community-mirrors.txt"
        \\          while IFS= read -r mirror_url; do
        \\            [ -n "$mirror_url" ] || continue
        \\            try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"
        \\          done < "$mirror_file"
        \\          curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"
        \\          if try_download "$ZIGUX_ZIG_URL"; then
        \\            download_success=1
        \\          fi
    ;

    try std.testing.expectError(error.TestUnexpectedResult, expectMirrorRosterRetryContract(bad_order));
}

test "direct ziglang fallback must remain after mirror roster loop" {
    const bad_fallback_order =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          mirror_file=".zig-toolchain/community-mirrors.txt"
        \\          if try_download "$ZIGUX_ZIG_URL"; then
        \\            download_success=1
        \\          elif curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\            while IFS= read -r mirror_url; do
        \\              [ -n "$mirror_url" ] || continue
        \\              try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"
        \\            done < "$mirror_file"
        \\          fi
    ;

    try std.testing.expectError(error.TestUnexpectedResult, expectMirrorRosterRetryContract(bad_fallback_order));
}
