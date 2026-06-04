const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
};

const ordered_workflow_markers = [_][]const u8{
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "if len(targets) != 1:",
    "target = targets[0]",
    "channel = policy[\"channel\"]",
    "filename = f\"zig-{target}-{channel}.tar.xz\"",
    "canonical_repo = \"adybag14-cyber/zig\"",
    "canonical_tag = \"upstream-748e7c5e39fc\"",
    "url = f\"https://ziglang.org/builds/{filename}\"",
    "canonical_url = f\"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}\"",
    "print(f\"ZIGUX_ZIG_TARGET='{target}'\")",
    "print(f\"ZIGUX_ZIG_CHANNEL='{channel}'\")",
    "print(f\"ZIGUX_ZIG_FILENAME='{filename}'\")",
    "print(f\"ZIGUX_ZIG_URL='{url}'\")",
    "print(f\"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'\")",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
};

fn requireContains(haystack: []const u8, needle: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, haystack, needle) orelse ContractError.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) ContractError!void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const position = try requireContains(haystack, marker);
        if (index != 0 and position <= previous) return ContractError.MarkerOutOfOrder;
        previous = position;
    }
}

fn requirePolicyAlignment(workflow: []const u8, policy: []const u8) ContractError!void {
    const target = "\"x86_64-linux\"";
    const channel = "\"channel\": \"0.17.0-dev.758+748e7c5e3\"";
    const digest = "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"";

    _ = try requireContains(policy, target);
    _ = try requireContains(policy, channel);
    _ = try requireContains(policy, digest);
    _ = try requireContains(workflow, "filename = f\"zig-{target}-{channel}.tar.xz\"");
    _ = try requireContains(workflow, "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"");
    _ = try requireContains(workflow, "repo_archive_parts_dir=\"${repo_archive_path}.parts\"");
}

fn validateToolchainEvalExports(workflow: []const u8, policy: []const u8) ContractError!void {
    try requireOrdered(workflow, &ordered_workflow_markers);
    try requirePolicyAlignment(workflow, policy);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, 1024 * 1024);
    defer allocator.free(workflow);
    const policy = try std.fs.cwd().readFileAlloc(allocator, policy_path, 64 * 1024);
    defer allocator.free(policy);

    validateToolchainEvalExports(workflow, policy) catch |err| {
        std.debug.print("LANE05_TOOLCHAIN_EVAL_EXPORTS_CONTRACT=fail\n", .{});
        std.debug.print("LANE05_TOOLCHAIN_EVAL_EXPORTS_CONTRACT_NOTE={s}\n", .{@errorName(err)});
        return err;
    };

    std.debug.print("LANE05_TOOLCHAIN_EVAL_EXPORTS_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_TOOLCHAIN_EVAL_EXPORTS_MARKER_COUNT={d}\n", .{ordered_workflow_markers.len});
}

test "accepts current policy-derived setup exports" {
    try validateToolchainEvalExports(current_workflow, current_policy);
}

test "rejects missing canonical URL export" {
    const stale = replace(
        current_workflow,
        "print(f\"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'\")",
        "print(f\"ZIGUX_ZIG_CANONICAL='{canonical_url}'\")",
    );
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateToolchainEvalExports(stale, current_policy));
}

test "rejects filename derivation after repo archive path use" {
    const stale = replace(
        current_workflow,
        "filename = f\"zig-{target}-{channel}.tar.xz\"",
        "# filename derivation moved elsewhere",
    );
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateToolchainEvalExports(stale, current_policy));
}

test "rejects stale policy channel" {
    const stale = replace(
        current_policy,
        "\"channel\": \"0.17.0-dev.758+748e7c5e3\"",
        "\"channel\": \"0.17.0-dev.87+9b177a7d2\"",
    );
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateToolchainEvalExports(current_workflow, stale));
}

fn replace(source: []const u8, needle: []const u8, replacement: []const u8) []u8 {
    return std.mem.replaceOwned(u8, std.testing.allocator, source, needle, replacement) catch unreachable;
}

const current_policy =
    \\{
    \\  "phase": "Phase 2",
    \\  "channel": "0.17.0-dev.758+748e7c5e3",
    \\  "minimum_version": "0.17.0-dev.758+748e7c5e3",
    \\  "archive_sha256": {
    \\    "x86_64-linux": "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6"
    \\  },
    \\  "upgrade_policy": {
    \\    "channel_minimum_lockstep": true,
    \\    "archive_target_scope": [
    \\      "x86_64-linux"
    \\    ]
    \\  }
    \\}
;

const current_workflow =
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
    \\          canonical_repo = "adybag14-cyber/zig"
    \\          canonical_tag = "upstream-748e7c5e39fc"
    \\          url = f"https://ziglang.org/builds/{filename}"
    \\          canonical_url = f"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}"
    \\          print(f"ZIGUX_ZIG_TARGET='{target}'")
    \\          print(f"ZIGUX_ZIG_CHANNEL='{channel}'")
    \\          print(f"ZIGUX_ZIG_FILENAME='{filename}'")
    \\          print(f"ZIGUX_ZIG_URL='{url}'")
    \\          print(f"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'")
    \\          PY
    \\          )"
    \\          mkdir -p .zig-toolchain
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
    \\          mirror_file=".zig-toolchain/community-mirrors.txt"
    \\          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
    \\          repo_archive_parts_dir="${repo_archive_path}.parts"
    \\          if try_local_archive; then
    \\            download_success=1
    \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\            download_success=1
    \\          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
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
