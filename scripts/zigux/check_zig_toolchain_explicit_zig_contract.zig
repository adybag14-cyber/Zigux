const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "explicit zig CLI path is validated before repo-local and PATH fallback" {
    try requireContains(checker_source, "parser.add_argument(\"--zig\", help=\"Explicit zig executable path.\")");
    try requireContains(checker_source, "def normalize_explicit_zig_path(explicit_zig: str) -> str:");
    try requireContains(checker_source, "normalized = Path(explicit_zig).expanduser()");
    try requireContains(checker_source, "if not normalized.exists():");
    try requireContains(checker_source, "raise ValueError(f\"explicit zig path does not exist: {normalized}\")");
    try requireContains(checker_source, "if normalized.is_dir():");
    try requireContains(checker_source, "raise ValueError(f\"explicit zig path is a directory, expected an executable file: {normalized}\")");
    try requireBefore(
        checker_source,
        "if explicit_zig is not None:",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
    try requireBefore(
        checker_source,
        "return normalize_explicit_zig_path(explicit_zig)",
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
    );
}

test "explicit zig status failures keep the requested path visible" {
    try requireContains(checker_source, "zig = resolve_zig_executable(args.zig)");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_PATH={zig or args.zig or 'unresolved'}\")",
        "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")",
    );
}

test "explicit zig success and executable failures use the resolved executable path" {
    try requireBefore(
        checker_source,
        "version = read_zig_version(zig)",
        "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)",
    );
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw}\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try requireContains(checker_source, "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try requireContains(checker_source, "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try requireBefore(
        checker_source,
        "exit_code = 0 if status == \"present\" else 1",
        "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")",
    );
    try requireBefore(
        checker_source,
        "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")",
        "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")",
    );
}
