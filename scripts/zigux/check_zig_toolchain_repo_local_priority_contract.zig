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

test "repo-local search roots include pinned and adjacent toolchain directories" {
    try requireContains(checker_source, "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains(checker_source, "add_search_root(root / \".zig-toolchain\")");
    try requireContains(checker_source, "add_search_root(root / \"toolchains\")");
    try requireContains(checker_source, "add_search_root(root / \".toolchains\")");
    try requireContains(checker_source, "add_search_root(parent / \".toolchains\")");
    try requireContains(checker_source, "add_search_root(parent / \"toolchains\")");
    try requireBefore(
        checker_source,
        "add_search_root(root / \".zig-toolchain\")",
        "for parent in root.parents:",
    );
}

test "pinned channel candidates are enumerated before generic local candidates" {
    try requireContains(checker_source, "zig_search_roots = iter_zig_search_roots(root)");
    try requireContains(checker_source, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try requireContains(checker_source, "add_candidate_roots(base / pinned_dirname)");
    try requireContains(checker_source, "add_candidate_roots(child / pinned_dirname)");
    try requireBefore(
        checker_source,
        "if pinned_channel is not None:",
        "for base in zig_search_roots:",
    );
    try requireBefore(
        checker_source,
        "add_candidate_roots(base / pinned_dirname)",
        "add_candidate_roots(base)",
    );
    try requireBefore(
        checker_source,
        "add_candidate_roots(child / pinned_dirname)",
        "add_candidate_roots(child)",
    );
}

test "PATH fallback remains after explicit and repo-local resolution" {
    try requireBefore(
        checker_source,
        "if explicit_zig is not None:",
        "pinned_channel = load_pinned_channel(policy_path)",
    );
    try requireBefore(
        checker_source,
        "pinned_channel = load_pinned_channel(policy_path)",
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
    );
    try requireBefore(
        checker_source,
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    );
    try requireContains(checker_source, "return normalize_explicit_zig_path(explicit_zig)");
    try requireContains(checker_source, "if candidate.is_file():");
    try requireContains(checker_source, "return str(candidate)");
}
