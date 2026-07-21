const std = @import("std");
const routes = @import("bootstrap_toolchain_route_contract.zig");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return error.MissingWorkflowMarker;
    }
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        return error.ForbiddenWorkflowMarker;
    }
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingWorkflowMarker;
    const later_index = std.mem.indexOfPos(u8, haystack, earlier_index + earlier.len, later) orelse return error.MissingWorkflowMarker;
    if (earlier_index >= later_index) {
        return error.WorkflowMarkerOrderDrifted;
    }
}

pub fn checkToolchainActivationMarkers(workflow: []const u8) !void {
    try requireContains(workflow, "      - name: Setup pinned Zig toolchain\n");
    try requireContains(workflow, "          extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"\n");
    try requireContains(workflow, "verify_and_activate_archive \"$repo_archive_path\"");
    try requireContains(workflow, "verify_and_activate_archive \"$archive_path\"");
    try requireContains(workflow, "            tar -xJf \"$archive\" -C .zig-toolchain");
    try requireContains(workflow, "activate_extracted_zig");
    try routes.requireRoute(workflow, "              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n", "              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n");
    try requireContains(workflow, "          zig_path=\"$extract_root/zig\"\n");
    try requireContains(workflow, "          echo \"$extract_root\" >> \"$GITHUB_PATH\"\n");
    try requireContains(workflow, "          \"$zig_path\" version\n");

    try requireAbsent(workflow, "echo \"$archive_path\" >> \"$GITHUB_PATH\"");
    try requireAbsent(workflow, "echo \"$repo_archive_path\" >> \"$GITHUB_PATH\"");
}

pub fn checkToolchainActivationOrder(workflow: []const u8) !void {
    try requireOrder(workflow, "      - name: Setup pinned Zig toolchain\n", "      - name: Validate current Zig bootstrap helpers\n");
    try requireOrder(workflow, "          extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"\n", "          try_local_archive() {\n");
    try requireOrder(workflow, "          try_local_archive() {\n", "verify_and_activate_archive \"$repo_archive_path\"");
    const repo_activate_index = std.mem.indexOf(u8, workflow, "verify_and_activate_archive \"$repo_archive_path\"") orelse return error.MissingWorkflowMarker;
    const repo_probe_index = routes.routeIndex(workflow, "              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n", "              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n") orelse return error.MissingWorkflowMarker;
    const download_index = std.mem.indexOf(u8, workflow, "          try_download() {\n") orelse return error.MissingWorkflowMarker;
    const archive_activate_index = std.mem.indexOf(u8, workflow, "verify_and_activate_archive \"$archive_path\"") orelse return error.MissingWorkflowMarker;
    const archive_probe_index = routes.routeIndex(workflow, "                if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n", "                if zig run scripts/zigux/check_zig_toolchain.zig -- --zig \"$zig_path\"; then\n") orelse return error.MissingWorkflowMarker;
    try std.testing.expect(repo_activate_index < repo_probe_index);
    try std.testing.expect(download_index < archive_activate_index);
    try std.testing.expect(archive_activate_index < archive_probe_index);
    try requireOrder(workflow, "          if [ \"$download_success\" -ne 1 ]; then\n", "          zig_path=\"$extract_root/zig\"\n");
    try requireOrder(workflow, "          zig_path=\"$extract_root/zig\"\n", "          echo \"$extract_root\" >> \"$GITHUB_PATH\"\n");
    try requireOrder(workflow, "          echo \"$extract_root\" >> \"$GITHUB_PATH\"\n", "          \"$zig_path\" version\n");
    try requireOrder(workflow, "          \"$zig_path\" version\n", "      - name: Validate current Zig bootstrap helpers\n");
}

test "Lane 05 activates only the verified extracted pinned Zig root" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkToolchainActivationMarkers(workflow);
}

test "Lane 05 activation proves pinned Zig before later workflow gates" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkToolchainActivationOrder(workflow);
}

test "Lane 05 activation rejects adding archive paths to GITHUB_PATH" {
    const broken =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\          verify_and_activate_archive() {
        \\            tar -xJf "$archive" -C .zig-toolchain
        \\          }
        \\          activate_extracted_zig() {
        \\            zig_path="$extract_root/zig"
        \\          }
        \\          try_local_archive() {
        \\            verify_and_activate_archive "$repo_archive_path"
        \\              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig "$zig_path"; then
        \\                return 0
        \\              fi
        \\          }
        \\          try_download() {
        \\            verify_and_activate_archive "$archive_path"
        \\                if zig run scripts/zigux/check_zig_toolchain.zig -- --zig "$zig_path"; then
        \\                  return 0
        \\                fi
        \\          }
        \\          if [ "$download_success" -ne 1 ]; then
        \\            exit 1
        \\          fi
        \\          zig_path="$extract_root/zig"
        \\          echo "$archive_path" >> "$GITHUB_PATH"
        \\          echo "$extract_root" >> "$GITHUB_PATH"
        \\          "$zig_path" version
        \\      - name: Validate current Zig bootstrap helpers
        \\
    ;

    try std.testing.expectError(error.ForbiddenWorkflowMarker, checkToolchainActivationMarkers(broken));
}

test "Lane 05 activation rejects running zig before GITHUB_PATH export" {
    const broken =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\          verify_and_activate_archive() {
        \\            tar -xJf "$archive" -C .zig-toolchain
        \\          }
        \\          activate_extracted_zig() {
        \\            zig_path="$extract_root/zig"
        \\          }
        \\          try_local_archive() {
        \\            verify_and_activate_archive "$repo_archive_path"
        \\              if zig run scripts/zigux/check_zig_toolchain.zig -- --zig "$zig_path"; then
        \\                return 0
        \\              fi
        \\          }
        \\          try_download() {
        \\            verify_and_activate_archive "$archive_path"
        \\                if zig run scripts/zigux/check_zig_toolchain.zig -- --zig "$zig_path"; then
        \\                  return 0
        \\                fi
        \\          }
        \\          if [ "$download_success" -ne 1 ]; then
        \\            exit 1
        \\          fi
        \\          zig_path="$extract_root/zig"
        \\          "$zig_path" version
        \\          echo "$extract_root" >> "$GITHUB_PATH"
        \\      - name: Validate current Zig bootstrap helpers
        \\
    ;

    try checkToolchainActivationMarkers(broken);
    try std.testing.expectError(error.MissingWorkflowMarker, checkToolchainActivationOrder(broken));
}
