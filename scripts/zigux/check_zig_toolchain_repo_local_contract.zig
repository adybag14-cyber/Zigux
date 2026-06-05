const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireSequence(source: []const u8, markers: []const []const u8) !void {
    var offset: usize = 0;
    for (markers) |marker| {
        const relative = std.mem.indexOf(u8, source[offset..], marker) orelse return error.MissingSequenceMarker;
        offset += relative + marker.len;
    }
}

test "repo local zig search roots include workspace and parent fallbacks" {
    try requireContains(checker_source, "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:");
    try requireContains(checker_source, "add_search_root(root / \".zig-toolchain\")");
    try requireContains(checker_source, "add_search_root(root / \"toolchains\")");
    try requireContains(checker_source, "add_search_root(root / \".toolchains\")");
    try requireContains(checker_source, "for parent in root.parents:");
    try requireContains(checker_source, "add_search_root(parent / \".toolchains\")");
    try requireContains(checker_source, "add_search_root(parent / \"toolchains\")");

    try requireBefore(checker_source, "add_search_root(root / \".zig-toolchain\")", "for parent in root.parents:");
    try requireBefore(checker_source, "add_search_root(root / \"toolchains\")", "add_search_root(root / \".toolchains\")");
}

test "pinned channel candidate search is preferred before generic repo local zig" {
    try requireContains(checker_source, "def iter_repo_local_zig_candidates(");
    try requireContains(checker_source, "zig_search_roots = iter_zig_search_roots(root)");
    try requireContains(checker_source, "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"");
    try requireContains(checker_source, "add_candidate_roots(base / pinned_dirname)");
    try requireContains(checker_source, "add_candidate_roots(child / pinned_dirname)");
    try requireContains(checker_source, "add_candidate_roots(base)");
    try requireContains(checker_source, "add_candidate_roots(child)");

    try requireSequence(checker_source, &.{
        "zig_search_roots = iter_zig_search_roots(root)",
        "if pinned_channel is not None:",
        "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"",
        "add_candidate_roots(base / pinned_dirname)",
        "for base in zig_search_roots:",
        "add_candidate_roots(base)",
    });
}

test "repo local executable resolution remains ahead of PATH fallback" {
    try requireContains(checker_source, "pinned_channel = load_pinned_channel(policy_path)");
    try requireContains(checker_source, "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):");
    try requireContains(checker_source, "if candidate.is_file():\n            return str(candidate)");
    try requireContains(checker_source, "return which(\"zig\")");

    try requireSequence(checker_source, &.{
        "if explicit_zig is not None:",
        "return normalize_explicit_zig_path(explicit_zig)",
        "pinned_channel = load_pinned_channel(policy_path)",
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
        "return which(\"zig\")",
    });
}
