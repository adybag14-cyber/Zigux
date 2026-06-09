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

fn expectCheckoutCodeloadRetryContract(workflow: []const u8) !void {
    try expectContains(workflow, "- name: Checkout workspace snapshot");
    try expectContains(workflow, "archive=\"$tmpdir/source.tar.gz\"");
    try expectContains(workflow, "\"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\"");
    try expectContains(workflow, "--fail");
    try expectContains(workflow, "--location");
    try expectContains(workflow, "--retry");
    try expectContains(workflow, "--retry-all-errors");
    try expectContains(workflow, "--retry-delay");
    try expectContains(workflow, "--connect-timeout");
    try expectContains(workflow, "--speed-limit");
    try expectContains(workflow, "--speed-time");
    try expectContains(workflow, "-o \"$archive\"");
    try expectNotContains(workflow, "uses: actions/checkout");
    try expectBefore(workflow, "curl", "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try expectBefore(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"", "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
    try expectBefore(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/", "- name: Setup Python");
}

const hardened_checkout_block =
    \\      - name: Checkout workspace snapshot
    \\        run: |
    \\          set -euxo pipefail
    \\          tmpdir="$(mktemp -d)"
    \\          archive="$tmpdir/source.tar.gz"
    \\          curl \
    \\            --fail \
    \\            --location \
    \\            --retry 5 \
    \\            --retry-all-errors \
    \\            --retry-delay 2 \
    \\            --connect-timeout 20 \
    \\            --speed-limit 1 \
    \\            --speed-time 60 \
    \\            "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" \
    \\            -o "$archive"
    \\          tar -xzf "$archive" -C "$tmpdir"
    \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
    \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    \\          shopt -s dotglob
    \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
    \\
    \\      - name: Setup Python
;

const vulnerable_single_shot_block =
    \\      - name: Checkout workspace snapshot
    \\        run: |
    \\          set -euxo pipefail
    \\          tmpdir="$(mktemp -d)"
    \\          archive="$tmpdir/source.tar.gz"
    \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
    \\          tar -xzf "$archive" -C "$tmpdir"
    \\          shopt -s dotglob
    \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
    \\
    \\      - name: Setup Python
;

test "hardened checkout codeload curl carries retry and stall guards" {
    try expectCheckoutCodeloadRetryContract(hardened_checkout_block);
}

test "single-shot codeload curl is rejected" {
    try std.testing.expectError(error.TestUnexpectedResult, expectCheckoutCodeloadRetryContract(vulnerable_single_shot_block));
}

test "actions checkout fallback is rejected" {
    const stale_checkout_action =
        \\      - name: Checkout workspace snapshot
        \\        uses: actions/checkout@v6.0.2
        \\        with:
        \\          fetch-depth: 0
        \\
        \\      - name: Setup Python
    ;

    try std.testing.expectError(error.TestUnexpectedResult, expectCheckoutCodeloadRetryContract(stale_checkout_action));
}
