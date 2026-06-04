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

test "explicit zig path stays first resolver priority" {
    try requireContains(checker_source, "def resolve_zig_executable(");
    try requireBefore(
        checker_source,
        "if explicit_zig is not None:\n        return normalize_explicit_zig_path(explicit_zig)",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
    try requireBefore(
        checker_source,
        "pinned_channel = load_pinned_channel(policy_path)",
        "return which(\"zig\")",
    );
}

test "pinned repo local layouts stay before PATH fallback" {
    try requireContains(checker_source, "def iter_repo_local_zig_candidates(");
    try requireContains(checker_source, "add_search_root(root / \".zig-toolchain\")");
    try requireContains(checker_source, "add_search_root(root / \"toolchains\")");
    try requireContains(checker_source, "add_search_root(root / \".toolchains\")");
    try requireContains(checker_source, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try requireContains(checker_source, "add_candidate_roots(base / pinned_dirname)");
    try requireContains(checker_source, "add_candidate_roots(child / pinned_dirname)");
    try requireBefore(
        checker_source,
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    );
}

test "missing zig diagnostic names both PATH and repo local roots" {
    try requireContains(checker_source, "def describe_missing_zig(");
    try requireContains(checker_source, "zig not found on PATH or in repo-local toolchain search roots");
    try requireContains(checker_source, "for pinned channel {pinned_channel}");
    try requireContains(checker_source, "return message, format_search_roots(search_roots)");
}
