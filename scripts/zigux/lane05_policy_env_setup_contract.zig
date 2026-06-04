const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    MarkerOutOfOrder,
};

const ordered_markers = [_][]const u8{
    "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))",
    "targets = policy[\"upgrade_policy\"][\"archive_target_scope\"]",
    "if len(targets) != 1:",
    "raise SystemExit(f\"expected exactly one pinned archive target, got {len(targets)}\")",
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
    "archive_path=\".zig-toolchain/$ZIGUX_ZIG_FILENAME\"",
    "extract_root=\"$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL\"",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, 1024 * 1024);
    defer allocator.free(workflow);

    try validateWorkflow(workflow);
}

fn validateWorkflow(workflow: []const u8) ContractError!void {
    var previous_index: usize = 0;
    for (ordered_markers, 0..) |marker, index| {
        const marker_index = try requireExactlyOnce(workflow, marker);
        if (index != 0 and marker_index <= previous_index) {
            return ContractError.MarkerOutOfOrder;
        }
        previous_index = marker_index;
    }
}

fn requireExactlyOnce(haystack: []const u8, needle: []const u8) ContractError!usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return ContractError.MissingMarker;
    const second = std.mem.indexOfPos(u8, haystack, first + needle.len, needle);
    if (second != null) return ContractError.DuplicateMarker;
    return first;
}

test "accepts current policy-derived setup environment contract" {
    try validateWorkflow(valid_workflow);
}

test "rejects setup that allows multiple archive targets" {
    const stale = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "if len(targets) != 1:\n              raise SystemExit(f\"expected exactly one pinned archive target, got {len(targets)}\")\n          target = targets[0]",
        "target = targets[0]",
    ) catch unreachable;
    defer std.testing.allocator.free(stale);

    try std.testing.expectError(ContractError.MissingMarker, validateWorkflow(stale));
}

test "rejects setup that drops the canonical release fallback" {
    const stale = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        valid_workflow,
        "canonical_repo = \"adybag14-cyber/zig\"",
        "canonical_repo = \"ziglang/zig\"",
    ) catch unreachable;
    defer std.testing.allocator.free(stale);

    try std.testing.expectError(ContractError.MissingMarker, validateWorkflow(stale));
}

test "rejects setup that downloads before exporting archive variables" {
    const wrong_order =
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
        \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
        \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
        \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
        \\          print(f"ZIGUX_ZIG_CHANNEL='{channel}'")
        \\          print(f"ZIGUX_ZIG_FILENAME='{filename}'")
        \\          print(f"ZIGUX_ZIG_URL='{url}'")
        \\          print(f"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'")
        \\          if try_download "$ZIGUX_ZIG_URL"; then
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validateWorkflow(wrong_order));
}

const valid_workflow =
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
    \\          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
    \\          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
    \\          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
    \\          if try_download "$ZIGUX_ZIG_URL"; then
;
