const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrder(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "toolchain search roots include repo and workspace roots in stable order" {
    try requireContains(
        checker_source,
        "def iter_zig_search_roots(root: Path = ROOT) -> list[Path]:",
    );
    try requireOrder(
        checker_source,
        "add_search_root(root / \".zig-toolchain\")",
        "add_search_root(root / \"toolchains\")",
    );
    try requireOrder(
        checker_source,
        "add_search_root(root / \"toolchains\")",
        "add_search_root(root / \".toolchains\")",
    );
    try requireContains(
        checker_source,
        "for parent in root.parents:\n        add_search_root(parent / \".toolchains\")\n        add_search_root(parent / \"toolchains\")",
    );
}

test "repo-local candidates prefer pinned channel directories before generic roots" {
    try requireContains(
        checker_source,
        "zig_search_roots = iter_zig_search_roots(root)",
    );
    try requireContains(
        checker_source,
        "pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"",
    );
    try requireOrder(
        checker_source,
        "if pinned_channel is not None:\n        pinned_dirname = f\"zig-x86_64-linux-{pinned_channel}\"\n        for base in zig_search_roots:",
        "for base in zig_search_roots:\n        if not base.exists():",
    );
    try requireOrder(
        checker_source,
        "add_candidate_roots(base / pinned_dirname)",
        "add_candidate_roots(base)",
    );
}

test "candidate collection keeps direct zig before bin zig and deduplicates paths" {
    try requireOrder(
        checker_source,
        "def add_candidate_roots(base: Path) -> None:\n        add_candidate(base / \"zig\")",
        "add_candidate(base / \"bin\" / \"zig\")",
    );
    try requireContains(
        checker_source,
        "if path not in candidates:\n            candidates.append(path)",
    );
}

test "resolver probes repo-local candidates before PATH fallback" {
    try requireOrder(
        checker_source,
        "pinned_channel = load_pinned_channel(policy_path)",
        "for candidate in iter_repo_local_zig_candidates(root=root, pinned_channel=pinned_channel):",
    );
    try requireOrder(
        checker_source,
        "if candidate.is_file():\n            return str(candidate)",
        "return which(\"zig\")",
    );
    try requireContains(
        checker_source,
        "expect_equal(resolve_zig_executable(root=root, policy_path=policy_path, which=lambda _: \"/usr/bin/zig\"), \"/usr/bin/zig\")",
    );
}
