const std = @import("std");

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

const checkout_step = "Checkout workspace snapshot";
const setup_python_step = "Setup Python";
const setup_zig_step = "Setup pinned Zig toolchain";
const compile_step = "Compile current scripts";

fn requireContains(text: []const u8, marker: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, text, marker) == null) return error.MissingMarker;
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

fn checkCheckoutSnapshot(workflow: []const u8) ContractError!void {
    try requireContains(workflow, "- name: " ++ checkout_step);
    try requireContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");
    try requireContains(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try requireContains(workflow, "src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"");
    try requireContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try requireContains(workflow, "shopt -s dotglob");
    try requireContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");

    try requireOrder(workflow, "- name: " ++ checkout_step, "- name: " ++ setup_python_step);
    try requireOrder(workflow, "- name: " ++ setup_python_step, "- name: " ++ setup_zig_step);
    try requireOrder(workflow, "- name: " ++ setup_zig_step, "- name: " ++ compile_step);
}

const current_workflow =
    \\      - name: Checkout workspace snapshot
    \\        run: |
    \\          set -euxo pipefail
    \\          tmpdir="$(mktemp -d)"
    \\          archive="$tmpdir/source.tar.gz"
    \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
    \\          tar -xzf "$archive" -C "$tmpdir"
    \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
    \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    \\          shopt -s dotglob
    \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
    \\
    \\      - name: Setup Python
    \\        uses: actions/setup-python@v6.2.0
    \\
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          "$zig_path" version
    \\
    \\      - name: Compile current scripts
    \\        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py
;

test "lane05 checkout snapshot uses exact commit tarball before setup" {
    try checkCheckoutSnapshot(current_workflow);
}

test "lane05 checkout snapshot rejects branch-floating codeload URLs" {
    const stale_workflow =
        \\      - name: Checkout workspace snapshot
        \\        run: |
        \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/master" -o "$archive"
        \\          tar -xzf "$archive" -C "$tmpdir"
        \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\          shopt -s dotglob
        \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\      - name: Setup Python
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
    ;

    try std.testing.expectError(error.MissingMarker, checkCheckoutSnapshot(stale_workflow));
}

test "lane05 checkout snapshot rejects stale actions checkout path" {
    const stale_workflow =
        \\      - name: Checkout workspace snapshot
        \\        uses: actions/checkout@v4
        \\      - name: Setup Python
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
    ;

    try std.testing.expectError(error.MissingMarker, checkCheckoutSnapshot(stale_workflow));
}

test "lane05 checkout snapshot keeps setup steps in bootstrap order" {
    const stale_workflow =
        \\      - name: Setup Python
        \\      - name: Checkout workspace snapshot
        \\        run: |
        \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\          tar -xzf "$archive" -C "$tmpdir"
        \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\          shopt -s dotglob
        \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
    ;

    try std.testing.expectError(error.OutOfOrderMarker, checkCheckoutSnapshot(stale_workflow));
}

test "lane05 checkout snapshot rejects dotfile-losing move" {
    const stale_workflow =
        \\      - name: Checkout workspace snapshot
        \\        run: |
        \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\          tar -xzf "$archive" -C "$tmpdir"
        \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\      - name: Setup Python
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
    ;

    try std.testing.expectError(error.MissingMarker, checkCheckoutSnapshot(stale_workflow));
}
