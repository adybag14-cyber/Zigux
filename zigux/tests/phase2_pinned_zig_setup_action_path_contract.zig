const std = @import("std");

const workflow_setup_step =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          set -euxo pipefail
    \\          eval "$(python3 - <<'PY'
    \\          import json
    \\          from pathlib import Path
    \\
    \\          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))
    \\          targets = policy["upgrade_policy"]["archive_target_scope"]
    \\          if len(targets) != 1:
    \\              raise SystemExit(f"expected exactly one pinned archive target, got {len(targets)}")
    \\          target = targets[0]
    \\          channel = policy["channel"]
    \\          filename = f"zig-{target}-{channel}.tar.xz"
    \\          url = f"https://ziglang.org/builds/{filename}"
    \\          print(f"ZIGUX_ZIG_TARGET='{target}'")
    \\          print(f"ZIGUX_ZIG_CHANNEL='{channel}'")
    \\          print(f"ZIGUX_ZIG_FILENAME='{filename}'")
    \\          print(f"ZIGUX_ZIG_URL='{url}'")
    \\          PY
    \\          )"
    \\          mkdir -p .zig-toolchain
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
    \\          mirror_file=".zig-toolchain/community-mirrors.txt"
    \\          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\          repo_archive_parts_dir="${repo_archive_path}.parts"
    \\          rm -f "$archive_path" "$mirror_file"
    \\          rm -rf "$extract_root"
    \\          try_local_archive() {
    \\            if [ ! -f "$repo_archive_path" ]; then
    \\              if [ ! -d "$repo_archive_parts_dir" ]; then
    \\                return 1
    \\              fi
    \\              python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1
    \\            fi
    \\            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
    \\              tar -xJf "$repo_archive_path" -C .zig-toolchain
    \\              zig_path="$extract_root/zig"
    \\              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
    \\                return 0
    \\              fi
    \\            fi
    \\            rm -rf "$extract_root"
    \\            return 1
    \\          }
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
    \\          if [ "$download_success" -ne 1 ]; then
    \\            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
    \\            exit 1
    \\          fi
    \\          zig_path="$extract_root/zig"
    \\          echo "$extract_root" >> "$GITHUB_PATH"
    \\          "$zig_path" version
;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "bootstrap action builds the pinned Zig archive path from policy" {
    try requireContains(workflow_setup_step, "- name: Setup pinned Zig toolchain");
    try requireContains(workflow_setup_step, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try requireContains(workflow_setup_step, "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]");
    try requireContains(workflow_setup_step, "expected exactly one pinned archive target");
    try requireContains(workflow_setup_step, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    try requireContains(workflow_setup_step, "url = f\"https://ziglang.org/builds/{filename}\"");
    try requireContains(workflow_setup_step, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    try requireContains(workflow_setup_step, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
}

test "local archive route is verified before extraction and path publication" {
    try requireContains(workflow_setup_step, "try_local_archive() {");
    try requireContains(workflow_setup_step, "python3 scripts/zigux/stage-pinned-zig-archive.py");
    try requireContains(workflow_setup_step, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"");
    try requireContains(workflow_setup_step, "tar -xJf \"$repo_archive_path\" -C .zig-toolchain");
    try requireContains(workflow_setup_step, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"");
    try requireContains(workflow_setup_step, "echo \"$extract_root\" >> \"$GITHUB_PATH\"");

    try requireOrdered(workflow_setup_step, "python3 scripts/zigux/stage-pinned-zig-archive.py", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"");
    try requireOrdered(workflow_setup_step, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\"", "tar -xJf \"$repo_archive_path\"");
    try requireOrdered(workflow_setup_step, "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"", "echo \"$extract_root\" >> \"$GITHUB_PATH\"");
}

test "download route keeps mirror attempt ahead of official fallback" {
    try requireContains(workflow_setup_step, "try_download() {");
    try requireContains(workflow_setup_step, "https://ziglang.org/download/community-mirrors.txt");
    try requireContains(workflow_setup_step, "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap");
    try requireContains(workflow_setup_step, "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireContains(workflow_setup_step, "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");

    try requireOrdered(workflow_setup_step, "if try_local_archive; then", "https://ziglang.org/download/community-mirrors.txt");
    try requireOrdered(workflow_setup_step, "https://ziglang.org/download/community-mirrors.txt", "if try_download \"$ZIGUX_ZIG_URL\"; then");
    try requireOrdered(workflow_setup_step, "if try_download \"$ZIGUX_ZIG_URL\"; then", "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org");
}
