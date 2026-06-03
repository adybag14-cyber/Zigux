const std = @import("std");

const workflow_packet =
    \\repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\repo_archive_parts_dir="${repo_archive_path}.parts"
    \\try_local_archive() {
    \\  if [ ! -f "$repo_archive_path" ]; then
    \\    if [ ! -d "$repo_archive_parts_dir" ]; then
    \\      return 1
    \\    fi
    \\    python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
    \\  fi
    \\  if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\    tar -xJf "$repo_archive_path" -C .zig-toolchain
    \\  fi
    \\}
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
    \\  done < "$mirror_file"
    \\fi
    \\if [ "$download_success" -ne 1 ]; then
    \\  if try_download "$ZIGUX_ZIG_URL"; then
    \\    download_success=1
    \\  fi
    \\fi
;

const workflow_step_packet =
    \\- name: Self-test current staged pinned Zig archive helper
    \\  run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
    \\- name: Self-test current Zig installer helper
    \\  run: python3 scripts/zigux/install-zig.py --self-test
    \\- name: Self-test current Lane 05 stage helper contract checker
    \\  run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
    \\- name: Check current Lane 05 stage helper contract packet
    \\  run: python3 scripts/zigux/check-lane05-stage-helper-contract.py
    \\- name: Self-test current Lane 05 stage helper selftest checker
    \\  run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test
    \\- name: Check current Lane 05 stage helper selftest packet
    \\  run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py
;

const stage_helper_output_packet =
    \\print("STAGE_PINNED_ZIG_ARCHIVE=pass")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_ROOT={root}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE={input_mode}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_TARGET={metadata['target']}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_FILENAME={metadata['filename']}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE={metadata['size']}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256={metadata['sha256']}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256={actual_sha}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_DESTINATION={destination}")
    \\print(f"STAGE_PINNED_ZIG_ARCHIVE_STATUS={status}")
;

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = try requireContains(haystack, earlier);
    const later_index = try requireContains(haystack, later);
    try std.testing.expect(earlier_index < later_index);
}

test "workflow stages repo-local archive parts before every download fallback" {
    try requireOrder(
        workflow_packet,
        "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
        "python3 scripts/zigux/stage-pinned-zig-archive.py --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1",
    );
    try requireOrder(
        workflow_packet,
        "python3 scripts/zigux/stage-pinned-zig-archive.py --root \"$GITHUB_WORKSPACE\" --parts-dir \"$repo_archive_parts_dir\" || return 1",
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    );
    try requireOrder(workflow_packet, "if try_local_archive; then", "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then");
    try requireOrder(workflow_packet, "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then", "https://ziglang.org/download/community-mirrors.txt");
    try requireOrder(workflow_packet, "https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
}

test "stage helper emits stable bootstrap diagnostics for source and parts inputs" {
    const required_fields = [_][]const u8{
        "STAGE_PINNED_ZIG_ARCHIVE=pass",
        "STAGE_PINNED_ZIG_ARCHIVE_ROOT=",
        "STAGE_PINNED_ZIG_ARCHIVE_INPUT_MODE=",
        "STAGE_PINNED_ZIG_ARCHIVE_TARGET=",
        "STAGE_PINNED_ZIG_ARCHIVE_FILENAME=",
        "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SIZE=",
        "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=",
        "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=",
        "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=",
        "STAGE_PINNED_ZIG_ARCHIVE_STATUS=",
    };

    for (required_fields) |field| {
        _ = try requireContains(stage_helper_output_packet, field);
    }
    try requireOrder(stage_helper_output_packet, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=", "STAGE_PINNED_ZIG_ARCHIVE_ACTUAL_SHA256=");
    try requireOrder(stage_helper_output_packet, "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=", "STAGE_PINNED_ZIG_ARCHIVE_STATUS=");
}

test "workflow self-tests the stage helper before installer-adjacent Lane 05 guards" {
    try requireOrder(
        workflow_step_packet,
        "Self-test current staged pinned Zig archive helper",
        "Self-test current Zig installer helper",
    );
    try requireOrder(
        workflow_step_packet,
        "Self-test current Zig installer helper",
        "Self-test current Lane 05 stage helper contract checker",
    );
    try requireOrder(
        workflow_step_packet,
        "Check current Lane 05 stage helper contract packet",
        "Self-test current Lane 05 stage helper selftest checker",
    );
    try requireOrder(
        workflow_step_packet,
        "Self-test current Lane 05 stage helper selftest checker",
        "Check current Lane 05 stage helper selftest packet",
    );
}
